import csv
from pathlib import Path
from core.models import MeatProduct


def load_products(csv_path: str) -> dict[str, MeatProduct]:
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"Product file not found: {csv_path}")

    products: dict[str, MeatProduct] = {}

    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        required_columns = {
            "sku",
            "name",
            "category",
            "wholesale_cost_per_lb",
            "yield_percent",
            "default_retail_price_per_lb",
        }

        missing = required_columns - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Products CSV is missing columns: {', '.join(sorted(missing))}")

        for row in reader:
            sku = row["sku"].strip().upper()
            if not sku:
                continue

            products[sku] = MeatProduct(
                sku=sku,
                name=row["name"].strip(),
                category=row["category"].strip(),
                wholesale_cost_per_lb=float(row["wholesale_cost_per_lb"]),
                yield_percent=float(row["yield_percent"]),
                default_retail_price_per_lb=float(row["default_retail_price_per_lb"]),
            )

    return products
