# modules/finance/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import AuditLog
from core.permissions import CanViewFinancialReports

class FinancialReportsView(APIView):
    permission_classes = [CanViewFinancialReports]

    def get(self, request):
        # Log access
        AuditLog.objects.create(
            user=request.user,
            action="viewed_financial_reports",
            ip_address=request.META.get("REMOTE_ADDR")
        )
        return Response({"data": "Financial data"})