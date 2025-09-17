from sqlalchemy.orm import Session
from domains.core.models.client import Business as BusinessModel
from domains.core.schemas.client import Business
from typing import List

class BusinessService:
    def __init__(self, db: Session):
        self.db = db

    def create_client(self, client: Business) -> BusinessModel:
        """Create a new client."""
        db_client = BusinessModel(**client.dict())
        self.db.add(db_client)
        self.db.commit()
        self.db.refresh(db_client)
        return db_client

    def get_client(self, client_id: int) -> BusinessModel:
        """Get a client by ID."""
        client = self.db.query(BusinessModel).filter(BusinessModel.client_id == client_id).first()
        if not client:
            raise ValueError("Business not found")
        return client

    def list_clients(self) -> List[BusinessModel]:
        """List all clients."""
        clients = self.db.query(BusinessModel).all()
        return clients
