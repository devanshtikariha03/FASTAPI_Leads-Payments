# # app/routers/leads.py

# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel, Field
# from typing import List
# from app.core.db import supabase
# from app.core.auth import verify_jwt_token
# from postgrest import APIError

# router = APIRouter(prefix="/api/v1/leads", tags=["leads"])

# class Lead(BaseModel):
#     realid: str = Field(..., min_length=1)
#     name:   str = Field(..., min_length=1)
#     phone:  int = Field(..., ge=1000000000, le=9999999999)

# class LeadsRequest(BaseModel):
#     leads: List[Lead] = Field(..., min_items=1)

# @router.post("", summary="Receive and insert leads")
# def create_leads(
#     body: LeadsRequest,
#     token=Depends(verify_jwt_token)
# ):
#     records = [lead.dict() for lead in body.leads]
#     try:
#         resp = supabase.from_("Leads").insert(records).execute()
#     except APIError as e:
#         raise HTTPException(status_code=500, detail=e.message)
#     return {"success": True, "inserted": len(resp.data)}


# app/routers/leads.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, conint
from typing import List, Optional, Literal
from postgrest import APIError
from app.core.db import supabase
from app.core.auth import verify_jwt_token

router = APIRouter(prefix="/api/v1/leads", tags=["leads"])

class Lead(BaseModel):
    date: str = Field(
        ...,
        pattern=r'^\d{4}-\d{2}-\d{2}\s*-\s*\d{4}-\d{2}-\d{2}$',
        description="DATERANGE in format YYYY-MM-DD - YYYY-MM-DD"
    )
    realid: str
    name: str
    phone_1: int
    phone_2: Optional[int] = None
    email: Optional[str] = None
    gender: Literal['male', 'female']
    preferred_language: Literal['en','hi','mr','te','ta','kn','gu','bn']
    home_state: str
    segment_band: Literal['6.B0_Segment6','5.B0_Segment5','4.B0_Segment4']
    collection_stage: str
    emi_eligible_flag: bool
    priority: conint(ge=0, le=100)
    bill_date: str  # YYYY-MM-DD
    due_date: str   # YYYY-MM-DD
    total_due: int
    min_due: int
    any_dispute_raised: Optional[str] = None
    days_past_due: Optional[int] = None
    app_lastvisit_timestamp_after_bill_date: Optional[str] = None  # YYYY-MM-DD HH:MM:SS
    app_payment_visit: Optional[bool] = None
    last_connected_call_time: Optional[str] = None                  # YYYY-MM-DD HH:MM:SS
    last_payment_details: Optional[str] = None
    last_connected_conversation: Optional[str] = None

class LeadsRequest(BaseModel):
    leads: List[Lead]

@router.post("", summary="Receive and insert leads")
def create_leads(body: LeadsRequest, token=Depends(verify_jwt_token)):
    records = [lead.dict() for lead in body.leads]
    try:
        resp = supabase.from_("Leads").insert(records).execute()
    except APIError as e:
        raise HTTPException(status_code=500, detail=e.message)
    return {"success": True, "inserted": len(resp.data)}
