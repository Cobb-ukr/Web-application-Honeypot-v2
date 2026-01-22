from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import AttackLog, DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("--- Debugging Attack Logs ---")
logs = db.query(AttackLog).all()
for log in logs:
    print(f"ID: {log.id} | Type: '{log.attack_type}' | Time: {log.timestamp}")

success_count = db.query(AttackLog).filter(AttackLog.attack_type == "Successful Login").count()
print(f"\nTotal Successful Logins (DB Query): {success_count}")
