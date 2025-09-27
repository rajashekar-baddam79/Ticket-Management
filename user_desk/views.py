from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserRegisterSerializer, LoginSerializer, UserProfileSerializer, TicketSerializer, AssignTicketSerializer, TicketStatusUpdateSerializer, UserSearchSerializer, TicketSearchSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, Ticket
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .tasks import check_for_escalations
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.


class UserRegistrationView(APIView):
    Permission_classes = [AllowAny]
    
    @swagger_auto_schema(request_body=UserRegisterSerializer)
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message: User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({"detail": "Logged in successfully"})
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=None)
    def post(self, request):
        logout(request)
        return Response({"detail": "Logged out successfully"})
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(responses={200: UserProfileSerializer})
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=UserProfileSerializer)
    def put(self, request):
        # Use partial=True to allow for partial updates
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Account updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        request.user.delete()
        return Response({"message": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

class TicketListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(responses={200: TicketSerializer})
    def get(self, request):
        user = request.user
        if user.role == 'admin':
            tickets = Ticket.objects.all()
        elif user.role == 'agent':
            tickets = Ticket.objects.filter(assigned_to=user)
        else:
            tickets = Ticket.objects.filter(created_by=user)
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(request_body=TicketSerializer)
    def post(self, request):
        # User can raise a ticket
        if request.user.role != 'user':
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TicketDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        ticket = get_object_or_404(Ticket, pk=pk)
        if user.role == 'admin':
            return ticket
        elif user.role == 'agent' and ticket.assigned_to == user:
            return ticket
        elif user.role == 'user' and ticket.created_by == user:
            return ticket
        else:
            return None

    def get(self, request, pk):
        user = request.user
        ticket = self.get_object(pk, user)
        if ticket is None:
            return Response({"error": "Not found or no permission"}, status=status.HTTP_404_NOT_FOUND)
        serializer = TicketSerializer(ticket)
        return Response(serializer.data)

# Agent: Update ticket status, add comment
class AgentUpdateTicketAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=TicketStatusUpdateSerializer)
    def patch(self, request, pk):
        if request.user.role != 'agent':
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        ticket = get_object_or_404(Ticket, pk=pk, assigned_to=request.user)
        
        # Update status if provided
        serializer = TicketStatusUpdateSerializer(ticket, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        ticket_serializer = TicketSerializer(ticket)
        return Response({"ticket": ticket_serializer.data}, status=status.HTTP_200_OK)


# Assign Ticket to Agent (Admin only)
class AdminAssignTicketAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=AssignTicketSerializer)
    def post(self, request, pk):
        if request.user.role != 'admin':
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        ticket = get_object_or_404(Ticket, pk=pk)
        serializer = AssignTicketSerializer(data=request.data)
        if serializer.is_valid():
            agent_id = serializer.validated_data['agent_id']
            agent = get_object_or_404(CustomUser, pk=agent_id, role='agent')
            ticket.assigned_to = agent
            ticket.save()
            ticket_serializer = TicketSerializer(ticket)
            return Response(ticket_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AdminDeleteTicketAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, pk):
        user = request.user
        if user.role != 'admin':
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        ticket = get_object_or_404(Ticket, pk=pk)
        ticket.delete()
        return Response({"message": "Ticket deleted."}, status=status.HTTP_204_NO_CONTENT)
    

class AdminUserListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'admin':
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        users = CustomUser.objects.all()
        serializer = UserRegisterSerializer(users, many=True)
        return Response(serializer.data)
    
class ManualEscalationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        if user.role != 'admin':
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        ticket = get_object_or_404(Ticket, pk=pk)
        
        # Call the Celery task asynchronously
        check_for_escalations.delay(ticket.id)
        
        return Response({'message': f'Escalation task dispatched for ticket {pk}.'}, status=status.HTTP_202_ACCEPTED)
    
class TicketSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_QUERY, description="Search by ticket title", type=openapi.TYPE_STRING),
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter by status", type=openapi.TYPE_STRING),
            openapi.Parameter('priority', openapi.IN_QUERY, description="Filter by priority", type=openapi.TYPE_STRING),
            openapi.Parameter('assigned_to', openapi.IN_QUERY, description="Filter by assigned user ID", type=openapi.TYPE_INTEGER),
        ],
        responses={200: TicketSearchSerializer(many=True)},
        operation_description="Search and filter tickets by title, status, priority, and assigned user"
    )

    def get(self, request):
        user = request.user
        tickets = Ticket.objects.none()

        # Role-based query sets
        if user.role == 'admin':
            tickets = Ticket.objects.all()
        elif user.role == 'agent':
            tickets = Ticket.objects.filter(assigned_to=user)
        elif user.role == 'user':
            tickets = Ticket.objects.filter(created_by=user)

        # Filtering based on search params
        title = request.query_params.get('title')
        status_param = request.query_params.get('status')
        priority = request.query_params.get('priority')
        assigned_to = request.query_params.get('assigned_to')

        if title:
            tickets = tickets.filter(title__icontains=title)
        if status_param:
            tickets = tickets.filter(status=status_param)
        if priority:
            tickets = tickets.filter(priority=priority)
        if assigned_to and user.role == 'admin':
            # Only admin can filter by assigned_to
            filters &= Q(assigned_to__id=assigned_to)
        serializer = TicketSearchSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserSearchView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('keyword', openapi.IN_QUERY, description="Keyword to search users by name or email", type=openapi.TYPE_STRING),
        ],
        responses={200: UserSearchSerializer(many=True)},
        operation_description="Search users by keyword matching first name, last name or email"
    )

    def get(self, request):
        user = request.user
        if user.role != 'admin':
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        keyword = request.query_params.get('keyword')

        if keyword:
            users = CustomUser.objects.filter(
                Q(first_name__icontains=keyword) |
                Q(last_name__icontains=keyword) |
                Q(email__icontains=keyword)
            )
        else:
            users = CustomUser.objects.none()

        serializer = UserSearchSerializer(users, many=True)
        return Response(serializer.data)
