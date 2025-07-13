from pydantic import BaseModel, Field, ConfigDict
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
    model_config = ConfigDict(from_attributes=True)
    
    case_id: str
    clinical_history: str

class ValidationSubmissionRequest(BaseModel):
    user_identifier: str = Field(..., max_length=5, min_length=5, pattern=r'^\d{5}$', description="Últimos 5 dígitos do CPF do usuário.")
    case_id: str
    user_group: str
    answer: str
    user_type: str

class SUSSubmissionRequest(BaseModel):
    user_identifier: str = Field(..., max_length=5, min_length=5, pattern=r'^\d{5}$', description="Últimos 5 dígitos do CPF do usuário.")
    q1: int = Field(..., ge=1, le=5)
    q2: int = Field(..., ge=1, le=5)
    q3: int = Field(..., ge=1, le=5)
    q4: int = Field(..., ge=1, le=5)
    q5: int = Field(..., ge=1, le=5)
    q6: int = Field(..., ge=1, le=5)
    q7: int = Field(..., ge=1, le=5)
    q8: int = Field(..., ge=1, le=5)
    q9: int = Field(..., ge=1, le=5)
    q10: int = Field(..., ge=1, le=5)

class SUSSubmissionResponse(BaseModel):
    status: str
    message: str

class ValidationSubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    user_identifier: str
    case_id: str
    answer: str

class AdminActionRequest(BaseModel):
    password: str 

class SUSResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    user_identifier: str
    q1: int
    q2: int
    q3: int
    q4: int
    q5: int
    q6: int
    q7: int
    q8: int
    q9: int
    q10: int
    created_at: str 