from pydantic import BaseModel, Field
from typing import List, Optional

class InferenceRequest(BaseModel):
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

class ValidationCaseResponse(BaseModel):
    case_id: str
    clinical_history: str

    class Config:
        orm_mode = True

class ValidationSubmissionRequest(BaseModel):
    user_identifier: str = Field(..., max_length=5, min_length=5, description="Últimos 5 dígitos do CPF do usuário.")
    case_id: str
    user_group: str
    answer: str

class ValidationSubmissionResponse(BaseModel):
    user_identifier: str
    case_id: str
    answer: str

    class Config:
        orm_mode = True

class AdminActionRequest(BaseModel):
    password: str 