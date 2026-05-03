from core.models import CostBreakdown, OrderItem


class ButcherCostAnalyzer:
    def __init__(
        self,
        labor_rate_per_hour: float,
        overhead_cost_per_order_item: float,
        target_margin_percent: float,
    ):
        if labor_rate_per_hour < 0:
            raise ValueError("Labor rate cannot be negative.")
        if overhead_cost_per_order_item < 0:
            raise ValueError("Overhead cost cannot be negative.")
        if target_margin_percent <= 0 or target_margin_percent >= 100:
            raise ValueError("Target margin must be between 1 and 99 percent.")

        self.labor_rate_per_hour = labor_rate_per_hour
        self.labor_rate_per_minute = labor_rate_per_hour / 60
        self.overhead_cost_per_order_item = overhead_cost_per_order_item
        self.target_margin_decimal = target_margin_percent / 100

    def calculate_item_cost(self, item: OrderItem) -> CostBreakdown:
        product = item.product

        if product.yield_percent <= 0 or product.yield_percent > 100:
            raise ValueError(f"{product.name} has an invalid yield percent.")
        if product.wholesale_cost_per_lb < 0:
            raise ValueError(f"{product.name} has an invalid wholesale cost.")
        if item.final_weight_lbs <= 0:
            raise ValueError("Final weight must be greater than 0.")
        if item.prep_minutes < 0:
            raise ValueError("Prep minutes cannot be negative.")
        if item.packaging_cost < 0:
            raise ValueError("Packaging cost cannot be negative.")

        true_cost_per_lb = product.wholesale_cost_per_lb / (product.yield_percent / 100)
        product_cost = item.final_weight_lbs * true_cost_per_lb
        labor_cost = item.prep_minutes * self.labor_rate_per_minute
        overhead_cost = self.overhead_cost_per_order_item
        total_internal_cost = product_cost + labor_cost + item.packaging_cost + overhead_cost
        selling_price = total_internal_cost / (1 - self.target_margin_decimal)
        profit = selling_price - total_internal_cost
        margin_percent = (profit / selling_price) * 100 if selling_price else 0

        return CostBreakdown(
            sku=product.sku,
            product_name=product.name,
            category=product.category,
            final_weight_lbs=round(item.final_weight_lbs, 2),
            wholesale_cost_per_lb=round(product.wholesale_cost_per_lb, 2),
            yield_percent=round(product.yield_percent, 2),
            true_cost_per_lb=round(true_cost_per_lb, 2),
            product_cost=round(product_cost, 2),
            labor_cost=round(labor_cost, 2),
            packaging_cost=round(item.packaging_cost, 2),
            overhead_cost=round(overhead_cost, 2),
            total_internal_cost=round(total_internal_cost, 2),
            selling_price=round(selling_price, 2),
            profit=round(profit, 2),
            margin_percent=round(margin_percent, 2),
        )
