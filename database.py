from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Database Connection
db_url = f"mysql+pymysql://{os.getenv('dbuser')}:{os.getenv('dbpassword')}@{os.getenv('dbhost')}:{os.getenv('dbport')}/{os.getenv('dbname')}"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ssl_cert_path = os.path.join(BASE_DIR, "isrgrootx1.pem")
engine = create_engine(db_url,
                        connect_args={
        "ssl": {
            "ca": ssl_cert_path
        }
        
        
    },
        pool_pre_ping=True,   # <--- Checks connection before using it
        pool_recycle=1800,    # <--- Refreshes connection every 30 mins
        pool_size=10,
        max_overflow=20)

session = sessionmaker(bind=engine)
db = session()

# 1. Create Database
db.execute(text("CREATE DATABASE IF NOT EXISTS blogify_db"))
print("Database checked/created")

# --- TABLE CREATION ---

# 2. Users (Authors)
db.execute(text("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(100) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(100),
        userType ENUM('user', 'admin') DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""))

# 3. Categories
db.execute(text("""
    CREATE TABLE IF NOT EXISTS categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        slug VARCHAR(50) NOT NULL UNIQUE
    );
"""))

# 4. Posts (Articles) - Matching your Frontend Fields
# Note: 'image' in frontend will map to 'cover_image_url' here
db.execute(text("""
    CREATE TABLE IF NOT EXISTS posts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        category_id INT NULL,
        title VARCHAR(255) NOT NULL,
        slug VARCHAR(255) UNIQUE,
        excerpt VARCHAR(300), 
        content LONGTEXT NOT NULL,
        cover_image_url VARCHAR(255),
        is_published BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
    );
"""))

# 5. Contacts (For the Contact Form)
db.execute(text("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        email VARCHAR(100) NOT NULL,
        subject VARCHAR(150),
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""))

# 6. Subscribers (For the Newsletter)
db.execute(text("""
    CREATE TABLE IF NOT EXISTS subscribers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(100) NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""))

print("All tables checked/created successfully.")

# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker
# from dotenv import load_dotenv
# import os

# load_dotenv()

# # Ensure you handle special characters in passwords if needed
# db_url = f"mysql+pymysql://{os.getenv('dbuser')}:{os.getenv('dbpassword')}@{os.getenv('dbhost')}:{os.getenv('dbport')}/{os.getenv('dbname')}"
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ssl_cert_path = os.path.join(BASE_DIR, "isrgrootx1.pem")
# engine = create_engine(db_url,
#                         connect_args={
#         "ssl": {
#             "ca": ssl_cert_path
#         }
#     })
# session = sessionmaker(bind=engine)
# db = session()

# # 1. Create Database
# create_db = text("CREATE DATABASE IF NOT EXISTS blogify_db")
# db.execute(create_db)
# print("Database checked/created")

# # --- TABLE CREATION ---
# # Note: Order matters due to Foreign Keys!

# # 2. Users Table updated
# create_users_table = text("""
#     CREATE TABLE IF NOT EXISTS users (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         username VARCHAR(50) NOT NULL UNIQUE,
#         email VARCHAR(100) NOT NULL UNIQUE,
#         password_hash VARCHAR(255) NOT NULL,
#         full_name VARCHAR(100),
#         bio TEXT,
#         avatar_url VARCHAR(255),
#         role ENUM('user', 'admin') DEFAULT 'user',
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
#     );
# """)
# db.execute(create_users_table)
# print("Users table checked/created")

# # 3. Categories Table (Must be before posts)
# create_categories_table = text("""
#     CREATE TABLE IF NOT EXISTS categories (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         name VARCHAR(50) NOT NULL,
#         slug VARCHAR(50) NOT NULL UNIQUE,
#         description TEXT
#     );
# """)
# db.execute(create_categories_table)
# print("Categories table checked/created")

# # 4. Posts Table
# create_posts_table = text("""
#     CREATE TABLE IF NOT EXISTS posts (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         user_id INT NOT NULL,
#         category_id INT NULL,
#         title VARCHAR(255) NOT NULL,
#         slug VARCHAR(255) NOT NULL UNIQUE,
#         content LONGTEXT NOT NULL,
#         summary VARCHAR(500),
#         cover_image_url VARCHAR(255),
#         is_published BOOLEAN DEFAULT FALSE,
#         views INT DEFAULT 0,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#         FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
#         FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
#     );
# """)
# db.execute(create_posts_table)
# print("Posts table checked/created")

# # 5. Tags Table
# create_tags_table = text("""
#     CREATE TABLE IF NOT EXISTS tags (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         name VARCHAR(50) NOT NULL UNIQUE,
#         slug VARCHAR(50) NOT NULL UNIQUE
#     );
# """)
# db.execute(create_tags_table)
# print("Tags table checked/created")

# # 6. Post_Tags Pivot Table
# create_post_tags_table = text("""
#     CREATE TABLE IF NOT EXISTS post_tags (
#         post_id INT NOT NULL,
#         tag_id INT NOT NULL,
#         PRIMARY KEY (post_id, tag_id),
#         FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
#         FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
#     );
# """)
# db.execute(create_post_tags_table)
# print("Post_Tags table checked/created")

# # 7. Comments Table
# create_comments_table = text("""
#     CREATE TABLE IF NOT EXISTS comments (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         post_id INT NOT NULL,
#         user_id INT NOT NULL,
#         content TEXT NOT NULL,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#         FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
#         FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
#     );
# """)
# db.execute(create_comments_table)
# print("Comments table checked/created")

# # 8. Post Likes Table
# create_post_likes_table = text("""
#     CREATE TABLE IF NOT EXISTS post_likes (
#         user_id INT NOT NULL,
#         post_id INT NOT NULL,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         PRIMARY KEY (user_id, post_id),
#         FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
#         FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
#     );
# """)
# db.execute(create_post_likes_table)
# print("Post_Likes table checked/created")