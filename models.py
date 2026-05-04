from pydantic import BaseModel, Field
from typing import List


class BrandRecommendation(BaseModel):
    brand_name: str = Field(description="The name of the protein powder brand")
    rank: int = Field(description="Ranking position (1 to 3)")
    reasoning: str = Field(description="Brief explanation for this ranking")


class ProteinReport(BaseModel):
    recommendations: List[BrandRecommendation]


class BrandAEOScore(BaseModel):
    brand_name: str
    total_points: int
    model_appearances: int
    models_that_ranked: List[str]
    visibility_pct: float