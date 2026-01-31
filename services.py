import jwt
import datetime
import os
from sqlalchemy import text
from fastapi import HTTPException

# --- USER & AUTH MANAGER ---
class UserManager:
    def __init__(self, db_session):
        self.db = db_session
        self.secret = os.getenv("secret_key", "supersecretkey")
        self.admin_email = os.getenv("ADMIN_EMAIL", "admin_email")
        self.admin_pass = os.getenv("ADMIN_PASSWORD", "admin_password")

    def login(self, login_data):
        # 1. Validation (Outside try/except so 400 errors are returned correctly)
        if login_data.email != self.admin_email or login_data.password != self.admin_pass:
            raise HTTPException(status_code=400, detail="Invalid Credentials")

        try:
            # 2. Check DB for Admin
            query = text("SELECT * FROM users WHERE email = :email")
            user = self.db.execute(query, {"email": self.admin_email}).mappings().fetchone()

            admin_id = None
            
            if not user:
                print("Admin not found in DB. Creating now...")
                # WRITE OPERATION -> Needs Rollback protection
                try:
                    insert_query = text("""
                        INSERT INTO users (username, email, password_hash, full_name, userType)
                        VALUES ('admin', :email, 'env_managed', 'Super Admin', 'admin')
                    """)
                    result = self.db.execute(insert_query, {"email": self.admin_email})
                    self.db.commit() # Commit changes
                    admin_id = result.lastrowid
                except Exception as e:
                    self.db.rollback() # <--- ROLLBACK ON FAILURE
                    print(f"Error creating admin: {str(e)}")
                    raise HTTPException(status_code=500, detail="Could not create admin user")
            else:
                admin_id = user.id

            # 3. Generate Token
            payload = {
                "id": admin_id,
                "userType": "admin",
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }
            token = jwt.encode(payload, self.secret, algorithm="HS256")
            
            return {
                "token": token, 
                "user": {"name": "Super Admin", "userType": "admin"}
            }
            
        except HTTPException as he:
            raise he
        except Exception as e:
            # Fallback for unexpected read errors
            raise HTTPException(status_code=500, detail=str(e))


# --- ARTICLE MANAGER ---
class ArticleManager:
    def __init__(self, db_session):
        self.db = db_session

    # --- INSIDE ArticleManager CLASS ---

    def get_all_articles(self):
        try:
            query = text("""
                SELECT p.*, u.full_name as author_name, c.name as category_name 
                FROM posts p
                LEFT JOIN users u ON p.user_id = u.id
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.is_published = TRUE
                ORDER BY p.created_at DESC
            """)
            result = self.db.execute(query).mappings().all()
            return result
        except Exception as e:
            self.db.rollback()  # <--- THIS WAS MISSING! RESET THE SESSION.
            print(f"Read Error: {e}") # helpful for debugging
            raise HTTPException(status_code=500, detail=f"Database Read Error: {str(e)}")

    def get_article_by_id(self, article_id):
        try:
            query = text("""
                SELECT p.*, u.full_name as author_name, c.name as category_name 
                FROM posts p
                LEFT JOIN users u ON p.user_id = u.id
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.id = :id
            """)
            article = self.db.execute(query, {"id": article_id}).mappings().fetchone()
            
            if not article:
                # 404 is not a DB error, so we don't need rollback, but good practice to close
                raise HTTPException(status_code=404, detail="Article not found")
            return article
            
        except HTTPException as he:
            raise he
        except Exception as e:
            self.db.rollback() # <--- THIS WAS MISSING!
            raise HTTPException(status_code=500, detail=str(e))
    def create_article(self, data, user_id):
        slug = data.title.lower().replace(" ", "-")
        query = text("""
            INSERT INTO posts (title, slug, excerpt, content, category_id, cover_image_url, is_published, user_id)
            VALUES (:title, :slug, :excerpt, :content, :cat_id, :img, :pub, :uid)
        """)
        try:
            self.db.execute(query, {
                "title": data.title,
                "slug": slug,
                "excerpt": data.excerpt,
                "content": data.content,
                "cat_id": data.category_id,
                "img": data.cover_image_url,
                "pub": data.is_published,
                "uid": user_id
            })
            self.db.commit()
            return {"message": "Article Created Successfully"}
        except Exception as e:
            self.db.rollback() # <--- ROLLBACK
            raise HTTPException(status_code=500, detail=f"Error creating article: {str(e)}")

    def update_article(self, id, data):
        try:
            fields = []
            values = {"id": id}
            
            if data.title:
                fields.append("title = :title")
                values["title"] = data.title
            if data.content:
                fields.append("content = :content")
                values["content"] = data.content
            if data.excerpt:
                fields.append("excerpt = :excerpt")
                values["excerpt"] = data.excerpt
            if data.cover_image_url:
                fields.append("cover_image_url = :img")
                values["img"] = data.cover_image_url
            if data.is_published is not None:
                fields.append("is_published = :pub")
                values["pub"] = data.is_published
            if data.category_id:
                fields.append("category_id = :cat")
                values["cat"] = data.category_id
                
            if not fields: return {"message": "No changes detected"}
            
            query = text(f"UPDATE posts SET {', '.join(fields)} WHERE id = :id")
            self.db.execute(query, values)
            self.db.commit()
            return {"message": "Article Updated"}
        except Exception as e:
            self.db.rollback() # <--- ROLLBACK
            raise HTTPException(status_code=500, detail=f"Error updating article: {str(e)}")

    def delete_article(self, id):
        try:
            query = text("DELETE FROM posts WHERE id = :id")
            result = self.db.execute(query, {"id": id})
            
            if result.rowcount == 0:
                self.db.rollback() # Safety rollback
                raise HTTPException(status_code=404, detail="Article not found")

            self.db.commit()
            return {"message": "Article Deleted"}
        except HTTPException as he:
            raise he
        except Exception as e:
            self.db.rollback() # <--- ROLLBACK
            raise HTTPException(status_code=500, detail=f"Error deleting article: {str(e)}")


# --- CONTACT MANAGER ---
class ContactManager:
    def __init__(self, db_session):
        self.db = db_session

    def submit_message(self, data):
        query = text("""
            INSERT INTO contacts (first_name, last_name, email, subject, message)
            VALUES (:fn, :ln, :email, :sub, :msg)
        """)
        try:
            self.db.execute(query, {
                "fn": data.firstName,
                "ln": data.lastName,
                "email": data.email,
                "sub": data.subject,
                "msg": data.message
            })
            self.db.commit()
            return {"message": "Message received successfully"}
        except Exception as e:
            self.db.rollback() # <--- ROLLBACK
            raise HTTPException(status_code=500, detail=f"Error saving message: {str(e)}")


# --- NEWSLETTER MANAGER ---
class NewsletterManager:
    def __init__(self, db_session):
        self.db = db_session

    def subscribe(self, email):
        query = text("INSERT IGNORE INTO subscribers (email) VALUES (:email)")
        try:
            self.db.execute(query, {"email": email})
            self.db.commit()
            return {"message": "Subscribed successfully"}
        except Exception as e:
            self.db.rollback() # <--- ROLLBACK
            raise HTTPException(status_code=500, detail=f"Error subscribing: {str(e)}")