from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MeatProduct:
    sku: str
    name: str
    category: str
    wholesale_cost_per_lb: float
    yield_percent: float
    default_retail_price_per_lb: float


@dataclass
class Customer:
    name: str
    phone: str
    pickup_date: str
    notes: str = ""


@dataclass
class OrderItem:
    product: MeatProduct
    final_weight_lbs: float
    prep_minutes: float
    packaging_cost: float


@dataclass
class CostBreakdown:
    sku: str
    product_name: str
    category: str
    final_weight_lbs: float
    wholesale_cost_per_lb: float
    yield_percent: float
    true_cost_per_lb: float
    product_cost: float
    labor_cost: float
    packaging_cost: float
    overhead_cost: float
    total_internal_cost: float
    selling_price: float
    profit: float
    margin_percent: float


@dataclass
class OrderSummary:
    order_id: str
    customer: Customer
    items: list[CostBreakdown] = field(default_factory=list)
    deposit_paid: float = 0.00
    status: str = "Quote"

    @property
    def total_internal_cost(self) -> float:
        return round(sum(item.total_internal_cost for item in self.items), 2)

    @property
    def final_customer_price(self) -> float:
        return round(sum(item.selling_price for item in self.items), 2)

    @property
    def total_profit(self) -> float:
        return round(self.final_customer_price - self.total_internal_cost, 2)

    @property
    def overall_margin_percent(self) -> float:
        if self.final_customer_price <= 0:
            return 0.00
        return round((self.total_profit / self.final_customer_price) * 100, 2)

    @property
    def balance_due(self) -> float:
        return round(max(self.final_customer_price - self.deposit_paid, 0), 2)


def generate_order_id() -> str:
    return f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
