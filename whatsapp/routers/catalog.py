from fastapi import APIRouter, Query
from ..services import catalog_service

router = APIRouter(prefix="/catalog", tags=["catalog"])

@router.get("")
async def get_catalog(q: str = Query("", description="search query"), category: str = "", page: int = 1, limit: int = 10):
    return catalog_service.list_catalog(q=q, category=category, page=page, limit=limit)

@router.get("/categories")
async def get_categories():
    return {"categories": catalog_service.categories()}

@router.get("/{csv_id}")
async def get_item(csv_id: str):
    item = catalog_service.get_item(csv_id)
    if not item:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Item not found")
    return item
