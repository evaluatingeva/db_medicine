from pydantic import BaseModel
from typing import List

class SearchResponse(BaseModel):
    items: List[str]
