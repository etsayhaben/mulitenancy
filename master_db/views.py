# master_db/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django_tenants.utils import tenant_context
from .models import Client, Domain
from .services import create_tenant  # ← You should have this service

class TenantRegisterAPIView(APIView):
    permission_classes = [IsAdminUser]  # Only admins can create tenants

    def post(self, request):
        name = request.data.get('name')
        domain = request.data.get('domain')
        contact_email = request.data.get('contact_email')
        plan = request.data.get('plan', 'free')

        if not name or not domain:
            return Response(
                {"error": "name and domain are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            tenant = create_tenant(
                name=name,
                domain=domain,
                contact_email=contact_email,
                plan=plan
            )
            return Response({
                "id": tenant.id,
                "name": tenant.name,
                "schema_name": tenant.schema_name,
                "domain": domain,
                "message": "Tenant created successfully"
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )