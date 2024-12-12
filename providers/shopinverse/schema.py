from typing import List, Optional
from pydantic import HttpUrl, BaseModel, field_validator
# from dataclasses import dataclass

class Variant(BaseModel):
    id: int
    title: str
    option1: Optional[str]
    option2: Optional[str]
    option3: Optional[str]
    sku: Optional[str]
    requires_shipping: bool
    taxable: bool
    featured_image: Optional[str]
    available: bool
    price: str
    grams: int
    compare_at_price: Optional[str]
    position: int
    product_id: int
    created_at: str
    updated_at: str


    @field_validator("featured_image", mode="before")
    def normalize_featured_image(cls, value):
        """
        Ensures that `featured_image` is extracted as a string URL if it is a dictionary.
        """
        if isinstance(value, dict) and "src" in value:
            return value["src"]
        return value

class Image(BaseModel):
    id: int
    created_at: str
    position: int
    updated_at: str
    product_id: int
    variant_ids: List[int]
    src: HttpUrl
    width: int
    height: int

class Option(BaseModel):
    name: str
    position: int
    values: List[str]

class Product(BaseModel):
    id: int
    title: str
    handle: str
    body_html: str
    published_at: str
    created_at: str
    updated_at: str
    vendor: str
    product_type: str
    tags: List[str]
    variants: List[Variant]
    images: List[Image]
    options: List[Option]

class ProductData(BaseModel):
    products: List[Product]