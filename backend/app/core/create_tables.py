from app.core.database import engine
from app.core.database import Base

def init_models():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_models()
