from pydantic import BaseModel
from typing import List, Optional

class InferenceRequest(BaseModel):
    """
    Model for the incoming API request.
    Expects a 'query' field with the clinical signs.
    """
    query: str

class Syndrome(BaseModel):
    """
    Model to represent a single syndrome in the result.
    Includes the syndrome name (especially eponyms), involved artery, location, reasoning, and a single (optional) suggested image.
    """
    name: str
    artery: str
    location: str
    reasoning: str
    suggested_image: Optional[str] = None

class InferenceResponse(BaseModel):
    """
    Model for the API response.
    Returns separate lists for ischemic and hemorrhagic syndromes.
    """
    ischemic_syndromes: List[Syndrome]
    hemorrhagic_syndromes: List[Syndrome] 