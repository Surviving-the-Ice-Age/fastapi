from fastapi import APIRouter
from pydantic import BaseModel
from typing import List 
from services import sentiment_service as svc

router = APIRouter()

class SentimentInput(BaseModel):
    messages: List[str] 

@router.post("/predict")
def analyze_messages(data: SentimentInput):
    return svc.analyze_messages(data.messages) 
