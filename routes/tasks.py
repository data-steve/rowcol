from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.task import Task, TaskAssignment  # Pydantic schemas
from services.task import TaskService
from database import get_db

router = APIRouter(prefix="/api", tags=["Tasks"])

@router.get("/tasks", response_model=list[Task])
async def list_tasks(engagement_id: int = None, firm_id: str = None, db: Session = Depends(get_db)):
    service = TaskService(db)
    return service.list_tasks(firm_id, engagement_id)

@router.patch("/tasks/{task_id}/assign", response_model=Task)  # Use Pydantic Task
async def assign_task(task_id: int, firm_id: str, assignment: TaskAssignment, db: Session = Depends(get_db)):
    service = TaskService(db)
    task = service.assign_task(task_id, firm_id, assignment.assigned_staff_id)
    return task