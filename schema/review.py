from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class ReviewSchema:
    stars: float | None = None
    title: str | None = None
    content: str | None = None


@dataclass
class ReviewsResponseSchema:
    reviews: List[ReviewSchema] | None = field(default_factory=list)
    total_reviews: int | None= 0
    rating_breakdown: Optional[dict] = field(default_factory=dict)
    total_ratings: Optional[int] = 0
    average_rating: Optional[float] = 0.0

