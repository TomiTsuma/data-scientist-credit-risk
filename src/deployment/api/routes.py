from fastapi import APIRouter
from .schemas import HealthResponse

router = APIRouter()

@router.get('/health', response_model=HealthResponse)
def health_check():
    return {'status': 'healthy', 'version': '0.1.0'}
