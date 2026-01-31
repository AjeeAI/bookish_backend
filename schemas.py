from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# --- INPUT SCHEMAS (What Frontend sends) ---

class ContactForm(BaseModel):
    firstName: str
    lastName: str
    email: str
    subject: str
    message: str

class NewsletterSub(BaseModel):
    email: str

# --- OUTPUT SCHEMAS (What Frontend receives) ---

from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional
from datetime import datetime

class ArticleResponse(BaseModel):
    id: int
    title: str
    excerpt: Optional[str] = None
    content: str
    
    # 1. READ from DB 'created_at' -> STORE in 'date' -> SEND to Frontend as 'date'
    date: datetime = Field(..., validation_alias="created_at") 
    
    # 2. READ from DB 'cover_image_url' -> STORE in 'image' -> SEND to Frontend as 'image'
    image: Optional[str] = Field(None, validation_alias="cover_image_url")
    
    # 3. READ from DB 'author_name' -> STORE in 'author'
    author: str = Field(..., validation_alias="author_name")
    
    # 4. READ from DB 'category_name' -> STORE in 'category'
    category: str = Field(..., validation_alias="category_name")

    class Config:
        from_attributes = True
        populate_by_name = True
# --- ADMIN / AUTH SCHEMAS ---

class LoginRequest(BaseModel):
    email: str = Field(..., example= "okikisblog@gmail.com")
    password: str = Field(..., example="AdminOkiki")

class ArticleCreate(BaseModel):
    title: str
    excerpt: str
    content: str
    category_id: int # Send the ID of the category (e.g., 1 for Articles)
    cover_image_url: str
    is_published: bool = True

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None
    cover_image_url: Optional[str] = None
    is_published: Optional[bool] = None
# Helper to format date as string (YYYY-MM-DD) if needed by frontend
# But usually React handles ISO dates well.


# from pydantic import BaseModel, Field, EmailStr
# from typing import Optional, List

# # --- AUTHENTICATION ---
# class SignUp(BaseModel):
#     username: str = Field(..., min_length=3, max_length=50, example="ajee_dev")
#     email: str = Field(..., example="ajee@gmail.com") # Validates email format
#     password: str = Field(..., min_length=6, example="ajee123")
#     full_name: Optional[str] = Field(None, example="Adesoji Ajijolaoluwa")

# class Login(BaseModel):
#     email: str = Field(..., example="ajee@gmail.com")
#     password: str = Field(..., example="ajee123")

# # --- USERS ---
# class UpdateProfile(BaseModel):
#     full_name: Optional[str] = Field(None, example="Adesoji A.")
#     bio: Optional[str] = Field(None, example="Fullstack developer loving FastAPI.")
#     avatar_url: Optional[str] = Field(None, example="https://image.com/me.png")

# # --- CATEGORIES ---
# class AddCategory(BaseModel):
#     name: str = Field(..., min_length=2, example="Technology")
#     description: Optional[str] = Field(None, example="All things tech and coding.")

# # --- POSTS ---
# class AddPost(BaseModel):
#     title: str = Field(..., min_length=5, example="Review of Gionee M11")
#     content: str = Field(..., min_length=10, example="This phone has excellent battery life...")
#     summary: Optional[str] = Field(None, example="A quick look at the M11 battery.")
    
#     # We use ID now because we have a separate Categories table
#     category_id: Optional[int] = Field(None, example=1) 
    
#     cover_image_url: Optional[str] = Field(None, example="https://images.com/phone.jpg")
#     is_published: bool = Field(False, example=True)
    
#     # Optional: You can accept a list of tag IDs or names
#     tags: Optional[List[str]] = Field(None, example=["tech", "mobile", "review"])

# class UpdatePost(BaseModel):
#     title: Optional[str] = None
#     content: Optional[str] = None
#     summary: Optional[str] = None
#     category_id: Optional[int] = None
#     cover_image_url: Optional[str] = None # Added this!
#     is_published: Optional[bool] = None

# # Note: We removed DeletePost and DeleteComment because 
# # we usually pass IDs in the URL (e.g. /posts/1) instead of the body.

# # --- COMMENTS ---
# class AddComment(BaseModel):
#     post_id: int = Field(..., example=5)
#     content: str = Field(..., min_length=1, example="Great article! really helped me.")
    
    
# # --- OUTPUT SCHEMA ---

# from datetime import datetime

# class UserResponse(BaseModel):
#     id: int
#     username: str
#     email: str
#     avatar_url: Optional[str]
    
#     class Config:
#         from_attributes = True # Tells Pydantic to read from SQLAlchemy models

# class PostResponse(BaseModel):
#     id: int
#     title: str
#     slug: str
#     author_name: str # From the join
#     created_at: datetime
    
#     class Config:
#         from_attributes = True