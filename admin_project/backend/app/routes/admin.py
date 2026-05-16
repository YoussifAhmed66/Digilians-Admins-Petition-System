from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.petition_service import PetitionService

router = APIRouter(prefix="/admin", tags=["admin"])


class DecisionRequest(BaseModel):
    status: str
    admin_name: str
    admin_notes: str | None = None


class LogActionRequest(BaseModel):
    admin_name: str
    action: str = "printed"
    notes: str | None = None


@router.get("/petitions")
async def list_petitions(service: PetitionService = Depends()):
    return await service.list_petitions()


@router.get("/petitions/{id}")
async def get_petition(id: str, service: PetitionService = Depends()):
    return await service.get_petition(id)


@router.post("/petitions/{id}/decision")
async def make_decision(id: str, req: DecisionRequest, service: PetitionService = Depends()):
    return await service.make_decision(id, status=req.status, admin_name=req.admin_name, admin_notes=req.admin_notes)


@router.post("/petitions/{id}/log-action")
async def log_action(id: str, req: LogActionRequest, service: PetitionService = Depends()):
    return await service.log_action(id, action=req.action, admin_name=req.admin_name, notes=req.notes)
