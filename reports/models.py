from django.db import models


class OrderReport(models.Model):
    order_id = models.PositiveIntegerField(unique=True)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_profit = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "orders_reports"


class ProductReport(models.Model):
    order_report = models.ForeignKey(
        OrderReport,
        on_delete=models.CASCADE,
        related_name="product_reports",
    )
    product_id = models.PositiveIntegerField()
    total_sold = models.PositiveIntegerField()
    stock_quantity = models.PositiveIntegerField()
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    profit = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "product_reports"
        constraints = [
            models.UniqueConstraint(
                fields=["order_report", "product_id"],
                name="uq_product_report_order_product",
            )
        ]