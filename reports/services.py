import os
from decimal import Decimal, InvalidOperation

import requests
from django.db import transaction
from rest_framework.exceptions import APIException, NotFound


class UpstreamError(APIException):
    status_code = 502
    default_detail = "Dịch vụ nguồn không trả về dữ liệu hợp lệ."


def upstream_get(url, authorization):
    try:
        return requests.get(
            url,
            headers={"Authorization": authorization},
            timeout=5,
            allow_redirects=False,
        )
    except requests.RequestException as exc:
        raise UpstreamError("Không kết nối được dịch vụ nguồn.") from exc


def fetch_json(url, authorization):
    response = upstream_get(url, authorization)

    if response.status_code == 404:
        raise NotFound("Không tìm thấy đơn hàng hoặc sản phẩm ở dịch vụ nguồn.")

    if response.status_code != 200:
        raise UpstreamError(
            f"Dịch vụ nguồn trả về HTTP {response.status_code}."
        )

    try:
        return response.json()
    except ValueError as exc:
        raise UpstreamError("Dịch vụ nguồn trả về JSON không hợp lệ.") from exc


def verify_token(authorization):
    url = os.getenv(
        "REPORT_AUTH_VERIFY_URL",
        "http://127.0.0.1:8001/auth/verify",
    )
    response = upstream_get(url, authorization)

    if response.status_code in (401, 403):
        return False

    if response.status_code != 200:
        raise UpstreamError("Dịch vụ xác thực trả về phản hồi không hợp lệ.")

    return True


def fetch_order(order_id, authorization):
    base_url = os.getenv("REPORT_ORDERS_URL", "http://127.0.0.1:8002/orders")
    return fetch_json(f"{base_url.rstrip('/')}/{order_id}", authorization)


def fetch_product(product_id, authorization):
    base_url = os.getenv("REPORT_PRODUCTS_URL", "http://127.0.0.1:8004/products")
    return fetch_json(f"{base_url.rstrip('/')}/{product_id}", authorization)


def calculate_order(order):
    totals = {}
    zero = Decimal("0.00")

    try:
        items = order["items"]
        if not isinstance(items, list) or not items:
            raise ValueError("Đơn hàng phải có ít nhất một mặt hàng.")

        for item in items:
            product_id = item["product_id"]
            quantity = item["quantity"]
            unit_price = Decimal(str(item["unit_price"]))
            unit_cost = Decimal(str(item["unit_cost"]))

            if type(product_id) is not int or not 1 <= product_id <= 2147483647:
                raise ValueError("Mã sản phẩm không hợp lệ.")
            if type(quantity) is not int or quantity <= 0:
                raise ValueError("Số lượng mua không hợp lệ.")
            if not all(
                amount.is_finite()
                and amount >= zero
                and amount == amount.quantize(Decimal("0.01"))
                for amount in (unit_price, unit_cost)
            ):
                raise ValueError("Đơn giá không hợp lệ.")

            line = totals.setdefault(
                product_id,
                {"total_sold": 0, "revenue": zero, "cost": zero},
            )
            line["total_sold"] += quantity
            line["revenue"] += unit_price * quantity
            line["cost"] += unit_cost * quantity

        total_revenue = sum(line["revenue"] for line in totals.values())
        total_cost = sum(line["cost"] for line in totals.values())
        limit = Decimal("99999999.99")

        if total_revenue > limit or total_cost > limit:
            raise ValueError("Giá trị vượt giới hạn DECIMAL(10, 2).")
        if any(line["total_sold"] > 2147483647 for line in totals.values()):
            raise ValueError("Số lượng bán vượt giới hạn INT.")

    except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
        raise UpstreamError("Dữ liệu mặt hàng của đơn hàng không hợp lệ.") from exc

    return totals, {
        "total_revenue": total_revenue,
        "total_cost": total_cost,
        "total_profit": total_revenue - total_cost,
    }


def create_order_report(order_id, authorization):
    from .models import OrderReport

    _, order_values = calculate_order(fetch_order(order_id, authorization))
    return OrderReport.objects.get_or_create(
        order_id=order_id,
        defaults=order_values,
    )


def create_product_report(order_id, product_id, authorization):
    from .models import OrderReport, ProductReport

    lines, order_values = calculate_order(fetch_order(order_id, authorization))
    if product_id not in lines:
        raise NotFound("Sản phẩm không có trong đơn hàng này.")

    product = fetch_product(product_id, authorization)
    stock = product.get("stock_quantity") if isinstance(product, dict) else None
    if type(stock) is not int or not 0 <= stock <= 2147483647:
        raise UpstreamError("Dịch vụ sản phẩm trả về tồn kho không hợp lệ.")

    line = lines[product_id]
    with transaction.atomic():
        order_report, _ = OrderReport.objects.get_or_create(
            order_id=order_id,
            defaults=order_values,
        )
        return ProductReport.objects.get_or_create(
            order_report=order_report,
            product_id=product_id,
            defaults={
                **line,
                "stock_quantity": stock,
                "profit": line["revenue"] - line["cost"],
            },
        )