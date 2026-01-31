# backend/seed.py
from database import db
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

def seed_database():
    print("🌱 Seeding Database...")

    # 1. Seed Categories (These match the filters in your Blog.jsx)
    categories = ["Articles", "Poems", "Image posts", "Stories"]
    
    print("Checking categories...")
    for cat in categories:
        slug = cat.lower().replace(" ", "-")
        # Check if exists first to avoid errors
        check = db.execute(text("SELECT id FROM categories WHERE slug = :slug"), {"slug": slug}).fetchone()
        
        if not check:
            print(f"Creating category: {cat}")
            query = text("INSERT INTO categories (name, slug) VALUES (:name, :slug)")
            db.execute(query, {"name": cat, "slug": slug})
    
    print("✅ Categories synced!")

    # 2. Seed Admin User (So your login works for sure)
    admin_email = os.getenv("ADMIN_EMAIL")
    
    if admin_email:
        print(f"Checking Admin User ({admin_email})...")
        user = db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": admin_email}).fetchone()
        
        if not user:
            print(f"Creating Admin User...")
            insert_query = text("""
                INSERT INTO users (username, email, password_hash, full_name, userType)
                VALUES ('admin', :email, 'env_managed', 'Super Admin', 'admin')
            """)
            db.execute(insert_query, {"email": admin_email})
            print("✅ Admin User Created!")
        else:
            print("ℹ️ Admin User already exists.")
    else:
        print("⚠️ ADMIN_EMAIL not found in .env, skipping admin creation.")

    db.commit()
    print("🚀 Database Seeded Successfully!")

if __name__ == "__main__":
    seed_database()