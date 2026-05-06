from sqlalchemy import create_engine

# Use the EXACT string you have in db.py
url = "mysql+pymysql://root:MyF%40stAPI2026%21@127.0.0.1:3306/fastapi_db"
engine = create_engine(url)

try:
    with engine.connect() as conn:
        print("✅ Success! Connection established.")
except Exception as e:
    print(f"❌ Failed! Error: {e}")