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
from ._schemas import ErrorResponse

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


class Payment(BaseModel):
    date: str = Field(
        ...,
        pattern=r'^\d{4}-\d{2}-\d{2}\s*-\s*\d{4}-\d{2}-\d{2}$',
        description="DATERANGE YYYY-MM-DD - YYYY-MM-DD"
    )
    realid: str = Field(..., min_length=1)
    Amount: conint(gt=0)
    tag: Literal['<STAB','STAB','<MAD','MAD','<TAD','TAD'] = Field(
        ..., alias="Payment Tag"
    )

    @validator('date')
    def validate_range(cls, v):
        parts = v.split(' - ')
        if len(parts) != 2:
            raise ValueError("date must be two dates separated by ' - '")
        return v


class PaymentsRequest(BaseModel):
    payments: List[Payment] = Field(..., min_items=1)


@router.post(
    "",
    summary="Receive and insert payments",
    response_model=dict,
    responses={
        200: {"description": "Payments processed successfully"},
        400: {
            "model": ErrorResponse,
            "description": "Validation error or bad request",
            "content": {
                "application/json": {
                    "example": {"error": "Payment Tag is required"}
                }
            },
        },
        401: {
            "model": ErrorResponse,
            "description": "Invalid or expired token",
            "content": {
                "application/json": {
                    "example": {"error": "Invalid or expired token"}
                }
            },
        },
        403: {
            "model": ErrorResponse,
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"error": "Authentication required"}
                }
            },
        },
        409: {
            "model": ErrorResponse,
            "description": "Conflict — duplicate payment",
            "content": {
                "application/json": {
                    "example": {"error": "Duplicate payment record"}
                }
            },
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"error": "Internal server error"}
                }
            },
        },
    },
)
def create_payments(
    body: PaymentsRequest = Body(...),
    token=Depends(verify_jwt_token)
):
    if not body.payments:
        raise HTTPException(status_code=400, detail="Request body cannot be empty")

    records = [p.dict(by_alias=True) for p in body.payments]
    try:
        resp = supabase.from_("payments").insert(records).execute()
    except APIError as e:
        if getattr(e, "code", "") == "23505" or "duplicate key" in e.message.lower():
            raise HTTPException(status_code=409, detail="Duplicate payment record")
        raise HTTPException(status_code=500, detail="Internal server error")

    return {"success": True, "inserted": len(resp.data)}

