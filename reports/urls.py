from django.urls import path

from .views import (
    OrderReportDetailView,
    OrderReportListCreateView,
    ProductReportDetailView,
    ProductReportListCreateView,
)

urlpatterns = [
    path("orders", OrderReportListCreateView.as_view()),
    path("orders/<int:pk>", OrderReportDetailView.as_view()),
    path("products", ProductReportListCreateView.as_view()),
    path("products/<int:pk>", ProductReportDetailView.as_view()),
]