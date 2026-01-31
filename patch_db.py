# backend/patch_db.py
from database import db
from sqlalchemy import text

def expand_excerpt_column():
    print("🛠️ Patching Database...")
    try:
        # This SQL command changes the column type to TEXT
        query = text("ALTER TABLE posts MODIFY COLUMN excerpt TEXT")
        db.execute(query)
        db.commit()
        print("✅ Success! You can now write long excerpts.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    expand_excerpt_column()