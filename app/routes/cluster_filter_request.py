from pydantic import BaseModel
from typing import List


class ClusterFilterRequest(BaseModel):
    filter_places: List[str] = ["url", "summary", "keywords", "title", "entities"]
    filter_including: List[str] = []
    filter_excluding: List[str] = []
