import csv
from dataclasses import asdict
from datetime import datetime
from io import StringIO
from core.models import OrderSummary


def order_items_as_rows(order: OrderSummary) -> list[dict]:
    rows = []
    for item in order.items:
        row = asdict(item)
        row.update({
            "order_id": order.order_id,
            "customer_name": order.customer.name,
            "customer_phone": order.customer.phone,
            "pickup_date": order.customer.pickup_date,
            "order_status": order.status,
            "customer_notes": order.customer.notes,
            "deposit_paid": order.deposit_paid,
            "balance_due": order.balance_due,
            "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        rows.append(row)
    return rows


def order_csv_text(order: OrderSummary) -> str:
    rows = order_items_as_rows(order)
    if not rows:
        return ""

    fieldnames = [
        "exported_at",
        "order_id",
        "customer_name",
        "customer_phone",
        "pickup_date",
        "order_status",
        "customer_notes",
        "deposit_paid",
        "balance_due",
        "sku",
        "product_name",
        "category",
        "final_weight_lbs",
        "wholesale_cost_per_lb",
        "yield_percent",
        "true_cost_per_lb",
        "product_cost",
        "labor_cost",
        "packaging_cost",
        "overhead_cost",
        "total_internal_cost",
        "selling_price",
        "profit",
        "margin_percent",
    ]

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return output.getvalue()


def receipt_text(order: OrderSummary) -> str:
    lines = []
    lines.append("BUTCHER SHOP ORDER RECEIPT")
    lines.append("=" * 42)
    lines.append(f"Order ID:     {order.order_id}")
    lines.append(f"Customer:     {order.customer.name}")
    lines.append(f"Phone:        {order.customer.phone}")
    lines.append(f"Pickup Date:  {order.customer.pickup_date}")
    lines.append(f"Status:       {order.status}")
    if order.customer.notes:
        lines.append(f"Notes:        {order.customer.notes}")
    lines.append("")
    lines.append("Items")
    lines.append("-" * 42)

    for item in order.items:
        lines.append(f"{item.product_name} | {item.final_weight_lbs:.2f} lb | ${item.selling_price:.2f}")

    lines.append("-" * 42)
    lines.append(f"Final Customer Price: ${order.final_customer_price:.2f}")
    lines.append(f"Deposit Paid:         ${order.deposit_paid:.2f}")
    lines.append(f"Balance Due:          ${order.balance_due:.2f}")
    lines.append("=" * 42)
    return "\n".join(lines)
