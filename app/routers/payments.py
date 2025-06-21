# from pydantic import BaseModel, Field
# from typing import List
# from fastapi import APIRouter, Depends, HTTPException
# from app.core.db import supabase
# from app.core.auth import verify_jwt_token
# from postgrest import APIError

# router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

# class Payment(BaseModel):
#     realid:      str
#     amount:      int
#     tag: str  # must match column name

# class PaymentsRequest(BaseModel):
#     payments: List[Payment]

# @router.post("")
# def create_payments(body: PaymentsRequest, token=Depends(verify_jwt_token)):
#     records = [p.dict() for p in body.payments]
#     try:
#         resp = supabase.from_("payments").insert(records).execute()
#     except APIError as e:
#         raise HTTPException(500, detail=e.message)
#     return {"success": True, "inserted": len(resp.data)}


# app/routers/payments.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, conint, validator
from typing import List, Literal
from postgrest import APIError
from app.core.db import supabase
from app.core.auth import verify_jwt_token

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

class Payment(BaseModel):
    date: str = Field(
        ...,
        pattern=r'^\d{4}-\d{2}-\d{2}\s*-\s*\d{4}-\d{2}-\d{2}$',
        description="DATERANGE in format YYYY-MM-DD - YYYY-MM-DD"
    )
    realid: str = Field(..., min_length=1)
    Amount: conint(gt=0)
    tag: Literal['<STAB','STAB','<MAD','MAD','<TAD','TAD']  # enforce valid tags

    @validator('date')
    def validate_range(cls, v):
        start, end = [d.strip() for d in v.split('-')]
        if start >= end:
            raise ValueError("date range start must be before end")
        return v

class PaymentsRequest(BaseModel):
    payments: List[Payment] = Field(..., min_items=1)

@router.post("", summary="Receive and insert payments")
def create_payments(body: PaymentsRequest, token=Depends(verify_jwt_token)):
    records = [p.dict(by_alias=True) for p in body.payments]
    try:
        resp = supabase.from_("payments").insert(records).execute()
    except APIError as e:
        raise HTTPException(status_code=500, detail=e.message)
    return {"success": True, "inserted": len(resp.data)}
