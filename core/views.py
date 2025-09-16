# core/views.py
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model

# JWT
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

# Serializers (adjust import if needed)
from core.auth_serializers import CustomTokenObtainPairSerializer, UserRegisterSerializer


# ------------------------------
# 🔐 JWT Views
# ------------------------------

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom login view that includes role and permissions in the token.
    """
    serializer_class = CustomTokenObtainPairSerializer


class UserRegisterView(APIView):
    permission_classes=[]
    """
    Register a new user and return JWT tokens.
    """
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role,
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------------------------
# 🧑‍💼 Current User View
# ------------------------------

class CurrentUserView(APIView):
    """
    GET: Return current user info (for /me endpoint)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "role": request.user.role,
            "roles": [g.name for g in request.user.groups.all()],
            "permissions": list(request.user.get_all_permissions()),
        })


# ------------------------------
# 🔐 Custom Permission
# ------------------------------

class IsAdminUser(BasePermission):
    """
    Allow access only to superusers (or customize as needed).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


# ------------------------------
# 🔐 Role & Permission API
# ------------------------------

class PermissionListView(APIView):
    """
    GET: List all permissions in the system.
    Used by frontend role editor.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        permissions = []
        for perm in Permission.objects.select_related('content_type').all():
            permissions.append({
                'id': perm.id,
                'codename': perm.codename,
                'name': perm.name,
                'app_label': perm.content_type.app_label,
                'model': perm.content_type.model,
            })
        return Response({'permissions': permissions})


class RoleListView(APIView):
    """
    GET: List all roles (Groups)
    POST: Create a new role
    """
    # permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        roles = []
        for group in Group.objects.prefetch_related('permissions').all():
            roles.append({
                'id': group.id,
                'name': group.name,
                'permissions': [p.codename for p in group.permissions.all()],
                'user_count': group.user_set.count(),
            })
        return Response({'roles': roles})

    def post(self, request):
        name = request.data.get('name')
        permission_codenames = request.data.get('permissions', [])

        if not name:
            return Response({'error': 'Role name is required'}, status=status.HTTP_400_BAD_REQUEST)

        if Group.objects.filter(name=name).exists():
            return Response({'error': 'A role with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            perms = Permission.objects.filter(codename__in=permission_codenames)
            if len(perms) != len(permission_codenames):
                return Response({'error': 'One or more permissions are invalid'}, status=status.HTTP_400_BAD_REQUEST)
        except Permission.DoesNotExist:
            return Response({'error': 'Invalid permission'}, status=status.HTTP_400_BAD_REQUEST)

        group = Group.objects.create(name=name)
        group.permissions.set(perms)

        return Response({
            'id': group.id,
            'name': group.name,
            'permissions': [p.codename for p in group.permissions.all()]
        }, status=status.HTTP_201_CREATED)


class RoleDetailView(APIView):
    """
    GET: Get single role
    PUT: Update role
    DELETE: Delete role (if no users assigned)
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self, role_id):
        return get_object_or_404(Group, id=role_id)

    def get(self, request, role_id):
        group = self.get_object(role_id)
        return Response({
            'id': group.id,
            'name': group.name,
            'permissions': [p.codename for p in group.permissions.all()],
            'user_count': group.user_set.count(),
        })

    def put(self, request, role_id):
        group = self.get_object(role_id)
        name = request.data.get('name')
        permission_codenames = request.data.get('permissions', [])

        if name and name != group.name:
            if Group.objects.exclude(id=role_id).filter(name=name).exists():
                return Response({'error': 'A role with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)
            group.name = name

        try:
            perms = Permission.objects.filter(codename__in=permission_codenames)
            if len(perms) != len(permission_codenames):
                return Response({'error': 'One or more permissions are invalid'}, status=status.HTTP_400_BAD_REQUEST)
        except Permission.DoesNotExist:
            return Response({'error': 'Invalid permission'}, status=status.HTTP_400_BAD_REQUEST)

        group.permissions.set(perms)
        group.save()

        return Response({
            'id': group.id,
            'name': group.name,
            'permissions': [p.codename for p in group.permissions.all()]
        })

    def delete(self, request, role_id):
        group = self.get_object(role_id)

        if group.user_set.exists():
            return Response(
                {'error': 'Cannot delete role: it is assigned to one or more users'},
                status=status.HTTP_400_BAD_REQUEST
            )

        group.delete()
        return Response({'message': 'Role deleted successfully'}, status=status.HTTP_200_OK)