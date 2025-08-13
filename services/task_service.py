from sqlalchemy.orm import Session
from models.task import Task as TaskModel
from models.staff import Staff as StaffModel
from schemas.task import Task
from typing import Optional

class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def assign_task(self, task_id: int, firm_id: str, staff_id: int) -> Task:
        task = self.db.query(TaskModel).filter(TaskModel.task_id == task_id, TaskModel.firm_id == firm_id).first()
        if not task:
            raise ValueError("Task not found")
        staff = self.db.query(StaffModel).filter(StaffModel.staff_id == staff_id, StaffModel.firm_id == firm_id).first()
        if not staff:
            raise ValueError("Staff not found")
        if task.type == "je_approval" and staff.training_level != "manager":
            raise ValueError("JE approval requires manager training level")
        task.assigned_staff_id = staff_id
        task.status = "assigned"
        self.db.commit()
        self.db.refresh(task)
        return Task.from_orm(task)
