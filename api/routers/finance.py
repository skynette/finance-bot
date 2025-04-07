from fastapi import APIRouter
from api.dependencies import get_current_user
from api.services import FinanceService

router = APIRouter(prefix="/finance", tags=["finance"])

@router.get("/currencies")
async def list_currencies():
    # Implement currency listing
    pass