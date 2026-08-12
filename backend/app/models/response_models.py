from pydantic import BaseModel
from typing import List, Optional


class ImageResponse(BaseModel):
    image_path: str
    page: int
    source: str


class QueryResponse(BaseModel):
    answer: str
    images: Optional[List[ImageResponse]] = []