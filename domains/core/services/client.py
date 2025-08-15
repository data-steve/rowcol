from sqlalchemy.orm import Session
from domains.core.models.client import Client as ClientModel
from domains.core.schemas.client import Client
from typing import List

class ClientService:
    def __init__(self, db: Session):
        self.db = db

    def create_client(self, client: Client) -> ClientModel:
        """Create a new client."""
        db_client = ClientModel(**client.dict())
        self.db.add(db_client)
        self.db.commit()
        self.db.refresh(db_client)
        return db_client

    def get_client(self, client_id: int) -> ClientModel:
        """Get a client by ID."""
        client = self.db.query(ClientModel).filter(ClientModel.client_id == client_id).first()
        if not client:
            raise ValueError("Client not found")
        return client

    def list_clients(self) -> List[ClientModel]:
        """List all clients."""
        clients = self.db.query(ClientModel).all()
        return clients
