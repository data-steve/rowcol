from database import engine
from models.service import Base as ServiceBase
from models.engagement import Base as EngagementBase
from models.task import Base as TaskBase

if __name__ == "__main__":
    ServiceBase.metadata.create_all(bind=engine)
    EngagementBase.metadata.create_all(bind=engine)
    TaskBase.metadata.create_all(bind=engine)
    print("Tables created successfully.")