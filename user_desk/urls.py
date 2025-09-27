from django.urls import path
from django.contrib.auth import views as auth_views
from .import views

urlpatterns = [

    # Auth & User
    path('auth/register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', views.LoginView.as_view(), name='user-login'),
    path('auth/logout/', views.LogoutView.as_view(), name='user-logout'),
    path('auth/user/', views.UserProfileView.as_view(), name='user-profile'),

    # Tickets
    path('tickets/', views.TicketListCreateView.as_view(), name='ticket-list-create'),
    path('tickets/<int:pk>/', views.TicketDetailAPIView.as_view(), name='ticket-detail'),
    path('agent/tickets/<int:pk>/update/', views.AgentUpdateTicketAPIView.as_view(), name='agent-ticket-update'),
    path('admin/tickets/<int:pk>/assign/', views.AdminAssignTicketAPIView.as_view(), name='admin-ticket-assign'),
    path('admin/tickets/<int:pk>/delete/', views.AdminDeleteTicketAPIView.as_view(), name='admin-ticket-delete'),

    path('admin/tickets/<int:pk>/escalate/', views.ManualEscalationView.as_view(), name='ticket-escalate'),

    # Ticket search & filtering
    path('search/tickets/', views.TicketSearchAPIView.as_view(), name='ticket-search'),

    # Admin user management
    path('admin/users/', views.AdminUserListAPIView.as_view(), name='admin-user-list'),

    # User search (Admin only)
    path('search/users/', views.UserSearchView.as_view(), name='user-search'),
]
