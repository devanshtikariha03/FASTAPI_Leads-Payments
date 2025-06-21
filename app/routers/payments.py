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

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List
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
    realid: str
    Amount: int
    Payment_Tag: str = Field(..., alias="Payment Tag")

class PaymentsRequest(BaseModel):
    payments: List[Payment]

@router.post("", summary="Receive and insert payments")
def create_payments(body: PaymentsRequest, token=Depends(verify_jwt_token)):
    # Use by_alias to send "Payment Tag" key
    records = [p.dict(by_alias=True) for p in body.payments]
    try:
        resp = supabase.from_("Payments").insert(records).execute()
    except APIError as e:
        raise HTTPException(status_code=500, detail=e.message)
    return {"success": True, "inserted": len(resp.data)}

