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

from fastapi import APIRouter, Depends, HTTPException, Body
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
    Amount: conint(gt=0)  # must be > 0
    tag: Literal['<STAB','STAB','<MAD','MAD','<TAD','TAD'] = Field(
        ..., alias="Payment Tag"
    )

    @validator('date')
    def validate_range(cls, v):
        """Ensure exactly two dates separated by ' - '."""
        try:
            start, end = [part.strip() for part in v.split(' - ', 1)]
        except ValueError:
            raise ValueError("date must be two dates separated by ' - '")
        return v

class PaymentsRequest(BaseModel):
    payments: List[Payment] = Field(..., min_items=1)

@router.post("", summary="Receive and insert payments")
def create_payments(
    body: PaymentsRequest = Body(...),
    token=Depends(verify_jwt_token)
):
    # 1) Empty-body check
    if not body.payments:
        raise HTTPException(status_code=400, detail="Request body cannot be empty")

    # 2) Attempt insert and catch duplicates via unique-violation
    records = [p.dict(by_alias=True) for p in body.payments]
    try:
        resp = supabase.from_("payments").insert(records).execute()
    except APIError as e:
        # Postgres unique violation is code 23505
        if getattr(e, "code", "") == "23505" or "duplicate key" in e.message.lower():
            raise HTTPException(status_code=409, detail="Duplicate payment record")
        # otherwise it's an internal error
        raise HTTPException(status_code=500, detail=e.message)

    return {"success": True, "inserted": len(resp.data)}

