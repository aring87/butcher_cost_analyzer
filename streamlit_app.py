import pandas as pd
import streamlit as st

from config import (
    LABOR_RATE_PER_HOUR,
    OVERHEAD_COST_PER_ORDER_ITEM,
    PRODUCTS_CSV_PATH,
    TARGET_MARGIN_PERCENT,
)
from core.calculator import ButcherCostAnalyzer
from core.models import Customer, OrderItem, OrderSummary, generate_order_id
from core.products import load_products
from core.reporting import order_csv_text, receipt_text


st.set_page_config(
    page_title="Butcher Shop Cost Analyzer",
    page_icon="🥩",
    layout="wide",
)


def money(value: float) -> str:
    return f"${value:,.2f}"


@st.cache_data
def load_product_table(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def initialize_session() -> None:
    if "order_id" not in st.session_state:
        st.session_state.order_id = generate_order_id()

    if "items" not in st.session_state:
        st.session_state.items = []


initialize_session()

st.title("🥩 Butcher Shop Cost Analyzer")
st.caption("Automate order quotes, final weighed pricing, deposits, balances, and profit margins.")

with st.sidebar:
    st.header("Business Settings")

    labor_rate = st.number_input(
        "Labor Rate per Hour",
        min_value=0.0,
        value=float(LABOR_RATE_PER_HOUR),
        step=1.0,
        format="%.2f",
    )

    overhead_cost = st.number_input(
        "Overhead Cost per Item",
        min_value=0.0,
        value=float(OVERHEAD_COST_PER_ORDER_ITEM),
        step=0.50,
        format="%.2f",
    )

    target_margin = st.number_input(
        "Target Margin %",
        min_value=1.0,
        max_value=99.0,
        value=float(TARGET_MARGIN_PERCENT),
        step=1.0,
        format="%.2f",
    )

    st.divider()

    if st.button("Start New Order", use_container_width=True):
        st.session_state.order_id = generate_order_id()
        st.session_state.items = []
        st.rerun()

products = load_products(PRODUCTS_CSV_PATH)
product_df = load_product_table(PRODUCTS_CSV_PATH)

analyzer = ButcherCostAnalyzer(
    labor_rate_per_hour=labor_rate,
    overhead_cost_per_order_item=overhead_cost,
    target_margin_percent=target_margin,
)

left, right = st.columns([1, 1])

with left:
    st.subheader("Customer / Order Info")

    customer_name = st.text_input("Customer Name")
    customer_phone = st.text_input("Customer Phone")
    pickup_date = st.date_input("Pickup Date")
    order_status = st.selectbox("Order Status", ["Quote", "Pending", "Ready", "Paid", "Cancelled"])
    deposit_paid = st.number_input("Deposit Paid", min_value=0.0, value=0.0, step=5.0, format="%.2f")
    customer_notes = st.text_area("Order Notes", height=90)

with right:
    st.subheader("Product Database")
    st.dataframe(
        product_df,
        use_container_width=True,
        hide_index=True,
    )

st.divider()

st.subheader("Add Meat Item")

item_col1, item_col2, item_col3, item_col4 = st.columns([2, 1, 1, 1])

with item_col1:
    sku_options = list(products.keys())
    selected_sku = st.selectbox(
        "Product",
        sku_options,
        format_func=lambda sku: f"{sku} — {products[sku].name}",
    )

with item_col2:
    final_weight = st.number_input("Final Weight lbs", min_value=0.01, value=1.00, step=0.25, format="%.2f")

with item_col3:
    prep_minutes = st.number_input("Prep Minutes", min_value=0.0, value=5.0, step=1.0, format="%.2f")

with item_col4:
    packaging_cost = st.number_input("Packaging Cost", min_value=0.0, value=1.00, step=0.25, format="%.2f")

add_item = st.button("Add Item to Order", type="primary")

if add_item:
    product = products[selected_sku]
    order_item = OrderItem(
        product=product,
        final_weight_lbs=final_weight,
        prep_minutes=prep_minutes,
        packaging_cost=packaging_cost,
    )

    try:
        breakdown = analyzer.calculate_item_cost(order_item)
        st.session_state.items.append(breakdown)
        st.success(f"Added {breakdown.product_name} — Recommended Price: {money(breakdown.selling_price)}")
    except ValueError as error:
        st.error(str(error))

if st.session_state.items:
    st.divider()
    st.subheader("Current Order Items")

    items_df = pd.DataFrame([
        item if isinstance(item, dict) else item.__dict__
        for item in st.session_state.items
    ])
    display_columns = [
        "sku",
        "product_name",
        "category",
        "final_weight_lbs",
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

    st.dataframe(
        items_df[display_columns],
        use_container_width=True,
        hide_index=True,
    )

    remove_col, clear_col = st.columns([1, 1])

    with remove_col:
        remove_index = st.number_input(
            "Remove item row number",
            min_value=1,
            max_value=len(st.session_state.items),
            value=1,
            step=1,
        )
        if st.button("Remove Selected Item"):
            st.session_state.items.pop(remove_index - 1)
            st.rerun()

    with clear_col:
        st.write("")
        st.write("")
        if st.button("Clear All Items"):
            st.session_state.items = []
            st.rerun()

customer = Customer(
    name=customer_name.strip() or "Unknown Customer",
    phone=customer_phone.strip() or "N/A",
    pickup_date=str(pickup_date),
    notes=customer_notes.strip(),
)

order = OrderSummary(
    order_id=st.session_state.order_id,
    customer=customer,
    items=st.session_state.items,
    deposit_paid=deposit_paid,
    status=order_status,
)

st.divider()
st.subheader("Order Summary")

metric1, metric2, metric3, metric4, metric5 = st.columns(5)
metric1.metric("Internal Cost", money(order.total_internal_cost))
metric2.metric("Customer Price", money(order.final_customer_price))
metric3.metric("Deposit Paid", money(order.deposit_paid))
metric4.metric("Balance Due", money(order.balance_due))
metric5.metric("Profit Margin", f"{order.overall_margin_percent:.2f}%")

st.write(f"**Order ID:** {order.order_id}")

download_col1, download_col2 = st.columns([1, 1])

with download_col1:
    st.download_button(
        "Download Cost Analysis CSV",
        data=order_csv_text(order),
        file_name=f"{order.order_id}_cost_analysis.csv",
        mime="text/csv",
        disabled=not bool(order.items),
        use_container_width=True,
    )

with download_col2:
    st.download_button(
        "Download Customer Receipt",
        data=receipt_text(order),
        file_name=f"{order.order_id}_customer_receipt.txt",
        mime="text/plain",
        disabled=not bool(order.items),
        use_container_width=True,
    )

with st.expander("Receipt Preview"):
    st.code(receipt_text(order), language="text")
