from sqlalchemy.orm import Session
from models.task import Task as TaskModel
from schemas.task import Task
from typing import List

class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, task: Task) -> TaskModel:
        """Create a new task."""
        db_task = TaskModel(**task.dict())
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def list_tasks(self) -> List[TaskModel]:
        """List all tasks."""
        tasks = self.db.query(TaskModel).all()
        return tasks
    
    def assign_task(self, task_id: int, firm_id: str, staff_id: int) -> TaskModel:
        """Assign a task to staff member."""
        task = self.db.query(TaskModel).filter(TaskModel.task_id == task_id, TaskModel.firm_id == firm_id).first()
        if not task:
            raise ValueError("Task not found")
        
        # Mock assignment logic
        task.assigned_staff_id = staff_id
        task.status = "assigned"
        self.db.commit()
        self.db.refresh(task)
        return task
