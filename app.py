from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from database import db
from middleware import verify_token

# Import all schemas (Read and Write)
from schemas import (
    ArticleResponse, 
    ContactForm, 
    NewsletterSub,
    LoginRequest,
    ArticleCreate,
    ArticleUpdate
)

# Import all services
from services import (
    ArticleManager, 
    ContactManager, 
    NewsletterManager, 
    UserManager
)

app = FastAPI(title="VerdantVistas API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DEPENDENCIES (The Factory Functions) ---

# 1. User Manager (This was missing!)
def get_user_manager():
    return UserManager(db)

# 2. Article Manager
def get_article_manager():
    return ArticleManager(db)

# 3. Contact Manager
def get_contact_manager(): 
    return ContactManager(db)

# 4. Newsletter Manager
def get_news_manager(): 
    return NewsletterManager(db)


# --- ROUTES ---

@app.get("/")
def home():
    return {"message": "VerdantVistas API is running"}

# --- AUTH ---
@app.post("/api/auth/login")
def login(
    data: LoginRequest, 
    manager: UserManager = Depends(get_user_manager)
):
    return manager.login(data)

# --- PUBLIC ARTICLES ---
@app.get("/api/articles", response_model=List[ArticleResponse])
def get_articles(manager: ArticleManager = Depends(get_article_manager)):
    return manager.get_all_articles()

@app.get("/api/articles/{id}", response_model=ArticleResponse)
def get_single_article(id: int, manager: ArticleManager = Depends(get_article_manager)):
    return manager.get_article_by_id(id)

# --- ADMIN ARTICLE MANAGEMENT (Protected) ---
@app.post("/api/articles")
def create_article(
    data: ArticleCreate, 
    user: dict = Depends(verify_token), # Ensures user is logged in
    manager: ArticleManager = Depends(get_article_manager)
):
    # Simple Role Based Access Control
    if user['userType'] != 'admin': 
        raise HTTPException(status_code=403, detail="Admins Only")
        
    return manager.create_article(data, user['id'])

@app.put("/api/articles/{id}")
def update_article(
    id: int, 
    data: ArticleUpdate, 
    user: dict = Depends(verify_token), 
    manager: ArticleManager = Depends(get_article_manager)
):
    if user['userType'] != 'admin': 
        raise HTTPException(status_code=403, detail="Admins Only")
        
    return manager.update_article(id, data)

@app.delete("/api/articles/{id}")
def delete_article(
    id: int, 
    user: dict = Depends(verify_token), 
    manager: ArticleManager = Depends(get_article_manager)
):
    if user['userType'] != 'admin': 
        raise HTTPException(status_code=403, detail="Admins Only")
        
    return manager.delete_article(id)

# --- CONTACT FORM ---
@app.post("/api/contact")
def send_message(
    form_data: ContactForm, 
    manager: ContactManager = Depends(get_contact_manager)
):
    return manager.submit_message(form_data)

# --- NEWSLETTER ---
@app.post("/api/subscribe")
def subscribe_newsletter(
    sub_data: NewsletterSub, 
    manager: NewsletterManager = Depends(get_news_manager)
):
    return manager.subscribe(sub_data.email)
# from fastapi import FastAPI, Depends, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from database import db
# from middleware import verify_token
# from typing import List

# # 1. UPDATE IMPORTS: Added response models, removed DeletePost
# from schemas import (
#     SignUp, Login, AddPost, 
#     UserResponse, PostResponse # <--- New response models
# )
# from services import UserManager, PostManager

# app = FastAPI(title="Blogify API", version="1.0.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- DEPENDENCIES ---
# def get_user_manager():
#     return UserManager(db)

# def get_post_manager(): 
#     return PostManager(db)

# @app.get("/")
# def home():
#     return {"message": "Blogify API is running!"}

# # --- AUTH ROUTES ---
# @app.post("/signup")
# def sign_up(input: SignUp, manager: UserManager = Depends(get_user_manager)):
#     return manager.register(input)

# @app.post("/login")
# def login(input: Login, manager: UserManager = Depends(get_user_manager)):
#     return manager.login(input)

# # 2. ADD RESPONSE MODEL: Hides passwords, formats dates
# @app.get("/users/me", response_model=UserResponse)
# def get_my_profile(
#     user_data: dict = Depends(verify_token), 
#     manager: UserManager = Depends(get_user_manager)
# ):
#     return manager.get_user_profile(user_data["id"])

# # --- BLOG POST ROUTES ---

# # 3. ADD RESPONSE MODEL: Ensures clean output
# @app.get("/posts", response_model=List[PostResponse])
# def get_posts(manager: PostManager = Depends(get_post_manager)):
#     return manager.get_all_posts()

# @app.post("/posts")
# def create_post(
#     input: AddPost,
#     user_data: dict = Depends(verify_token), 
#     manager: PostManager = Depends(get_post_manager)
# ):
#     return manager.add_post(input, user_data)

# # 4. FIX DELETE ROUTE: Use path parameter '{id}' instead of Body
# @app.delete("/posts/{id}") 
# def delete_post(
#     id: int, # <--- Comes from URL now
#     user_data: dict = Depends(verify_token),
#     manager: PostManager = Depends(get_post_manager)
# ):
#     return manager.delete_post(id, user_data)