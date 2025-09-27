from rest_framework import serializers
from .models import CustomUser, Ticket


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'role', 'phone','address', 'dob']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            role=validated_data.get('role', 'user'),
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', ''),
            dob=validated_data.get('dob', None),
        )
        user.set_password(password)  # Secure password hashing!
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
class TicketSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['created_by', 'assigned_to', 'status']

class TicketStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['status']

class AssignTicketSerializer(serializers.Serializer):
    agent_id = serializers.IntegerField()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username','email','first_name','last_name','phone','address','dob','role']
        read_only_fields = ['username','role']

class TicketSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'title', 'status', 'priority', 'assigned_to']


class UserSearchSerializer(serializers.ModelSerializer):
    nameEmail = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email', 'role', 'nameEmail']

    def get_nameEmail(self, obj):
        return f"{obj.first_name} {obj.last_name} - {obj.email}"
