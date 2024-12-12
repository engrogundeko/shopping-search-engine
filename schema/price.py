from dataclasses import dataclass
from typing import Optional


@dataclass
class PriceDetailSchema:
    name: str
    currency: str
    product_id: str
    product_url: str
    current_price: str | None = ""
    discount: Optional[str] = None
    old_price: str | None = None
    product_affiliate_url: str | None = None

