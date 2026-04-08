from app.database.engine import engine
from app.database.base import Base

from app.models import *

print("🔄 Creating all database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Done! All tables created successfully.")
