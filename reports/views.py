from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .authentication import RemoteTokenAuthentication
from .models import OrderReport, ProductReport
from .serializers import (
    OrderReportInputSerializer,
    OrderReportSerializer,
    ProductReportInputSerializer,
    ProductReportSerializer,
)
from .services import create_order_report, create_product_report


class AuthenticatedReportView:
    authentication_classes = [RemoteTokenAuthentication]
    permission_classes = [IsAuthenticated]


class ReportListCreateView(AuthenticatedReportView, generics.ListCreateAPIView):
    input_serializer_class = None
    create_report = None

    def create(self, request, *args, **kwargs):
        serializer = self.input_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        report, created = self.create_report(
            authorization=request.auth,
            **serializer.validated_data,
        )
        return Response(
            self.get_serializer(report).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class OrderReportListCreateView(ReportListCreateView):
    queryset = OrderReport.objects.order_by("id")
    serializer_class = OrderReportSerializer
    input_serializer_class = OrderReportInputSerializer
    create_report = staticmethod(create_order_report)


class ProductReportListCreateView(ReportListCreateView):
    queryset = ProductReport.objects.order_by("id")
    serializer_class = ProductReportSerializer
    input_serializer_class = ProductReportInputSerializer
    create_report = staticmethod(create_product_report)


class OrderReportDetailView(
    AuthenticatedReportView, generics.RetrieveDestroyAPIView
):
    queryset = OrderReport.objects.all()
    serializer_class = OrderReportSerializer


class ProductReportDetailView(
    AuthenticatedReportView, generics.RetrieveDestroyAPIView
):
    queryset = ProductReport.objects.all()
    serializer_class = ProductReportSerializer