from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_assign_task(test_task, test_staff):
    response = client.patch(
        f"/api/tasks/{test_task.task_id}/assign?firm_id={test_task.firm_id}",
        json={"task_id": test_task.task_id, "assigned_staff_id": test_staff.staff_id}
    )
    assert response.status_code == 200
    assert response.json()["assigned_staff_id"] == test_staff.staff_id