from dataclasses import dataclass, field
from typing import List


@dataclass
class ProductSchema:
    name: str | None = None
    price: float | None = None
    brand: str | None = None
    categories: list[str] = field(default_factory=list)
    image_url: List[str] | None = field(default_factory=list)
    total_ratings: str | None = None
    rating: str | None = None
    old_price: str | None = None
    discount: str | None = None
    is_shop_express: bool | None = None