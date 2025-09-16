# core/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from master_db.views import TenantRegisterAPIView

from . import views

app_name = "core"

urlpatterns = [
    # Auth
    path("token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("me/", views.CurrentUserView.as_view(), name="current_user"),
    # Roles & Permissions
    path("permissions/", views.PermissionListView.as_view(), name="list_permissions"),
    path("roles/", views.RoleListView.as_view(), name="role_list"),
    path("roles/<int:role_id>/", views.RoleDetailView.as_view(), name="role_detail"),
    path("register-company/", TenantRegisterAPIView.as_view(), name="register-company"),
    path('api/tenant/register/', TenantRegisterAPIView.as_view(), name='tenant-register'),
]
