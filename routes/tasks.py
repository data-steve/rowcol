from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.task import Task as TaskModel  # SQLAlchemy model
from schemas.task import Task, TaskAssignment  # Pydantic schemas
from services.task_service import TaskService
from database import get_db

router = APIRouter(prefix="/api", tags=["Tasks"])

@router.get("/tasks", response_model=list[Task])
async def list_tasks(engagement_id: int = None, firm_id: str = None, db: Session = Depends(get_db)):
    query = db.query(TaskModel)
    if firm_id:
        query = query.filter(TaskModel.firm_id == firm_id)
    if engagement_id:
        query = query.filter(TaskModel.engagement_id == engagement_id)
    tasks = query.all()
    return tasks

@router.patch("/tasks/{task_id}/assign", response_model=Task)  # Use Pydantic Task
async def assign_task(task_id: int, firm_id: str, assignment: TaskAssignment, db: Session = Depends(get_db)):
    service = TaskService(db)
    task = service.assign_task(task_id, firm_id, assignment.assigned_staff_id)
    return task