from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Helpdesk Ticket Management API",
      default_version='v1',
      description="API documentation for the Helpdesk & Ticket Management System",
      contact=openapi.Contact(email="support@example.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

