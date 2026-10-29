
from app.database import DATABASE_PATH, get_recent_incidents

print("Database path:", DATABASE_PATH)
print("Database exists:", DATABASE_PATH.exists())
print("Saved incidents:", get_recent_incidents())
