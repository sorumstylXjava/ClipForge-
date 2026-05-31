from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.AIJob)
def create_ai_job(
    *,
    db: Session = Depends(deps.get_db),
    job_in: schemas.AIJobCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Queue a new AI Job.
    """
    video = crud.video.get(db, id=job_in.video_id)
    if not video or video.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Video not found")

    job_in.user_id = current_user.id
    job = crud.ai_job.create(db, obj_in=job_in)
    
    # Add usage log
    log = schemas.UsageLogCreate(
        action="ai_job_submit",
        user_id=current_user.id,
        video_id=video.id,
        ai_job_id=job.id,
        plan_at_time=current_user.plan
    )
    crud.usage_log.create(db, obj_in=log)
    
    return job

@router.get("/{id}", response_model=schemas.AIJob)
def get_ai_job_status(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get AI Job status.
    """
    job = crud.ai_job.get(db=db, id=id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return job

@router.get("/{id}/result", response_model=List[schemas.Clip])
def get_ai_job_result(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get AI Job results (generated clips).
    """
    job = crud.ai_job.get(db=db, id=id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")
        
    clips = db.query(models.Clip).filter(models.Clip.ai_job_id == id).all()
    return clips

@router.post("/{id}/cancel", response_model=schemas.AIJob)
def cancel_ai_job(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Cancel an AI Job.
    """
    job = crud.ai_job.get(db=db, id=id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
        
    job = crud.ai_job.update(db, db_obj=job, obj_in={"status": "cancelled"})
    return job
