from rest_framework import serializers

from .models import OrderReport, ProductReport


class OrderReportInputSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(min_value=1, max_value=2147483647)


class ProductReportInputSerializer(OrderReportInputSerializer):
    product_id = serializers.IntegerField(min_value=1, max_value=2147483647)


class OrderReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderReport
        fields = ["id", "order_id", "total_revenue", "total_cost", "total_profit"]


class ProductReportSerializer(serializers.ModelSerializer):
    order_report_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProductReport
        fields = [
            "id",
            "order_report_id",
            "product_id",
            "total_sold",
            "stock_quantity",
            "revenue",
            "cost",
            "profit",
        ]