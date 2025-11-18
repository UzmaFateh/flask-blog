# # migrate_data.py

# import os
# import sqlite3
# from app import db, User, BlogPost, Comment
# from datetime import datetime

# # SQLite DB path
# sqlite_path = os.path.join("instance", "blog.db")
# sqlite_conn = sqlite3.connect(sqlite_path)
# sqlite_cursor = sqlite_conn.cursor()

# # -------------------
# # Users migrate karna
# # -------------------
# sqlite_cursor.execute("SELECT id, email, username, password, role FROM user;")
# users = sqlite_cursor.fetchall()

# for u in users:
#     # Check if already exists in PostgreSQL to avoid duplicates
#     if not User.query.get(u[0]):
#         user = User(id=u[0], email=u[1], username=u[2], password=u[3], role=u[4])
#         db.session.add(user)

# db.session.commit()
# print(f"✅ {len(users)} users migrated!")

# # -------------------
# # BlogPosts migrate karna
# # -------------------
# sqlite_cursor.execute("""
#     SELECT id, user_id, title, slug, category, excerpt, img_path, created_at, status, likes, comments_count 
#     FROM blog_post;
# """)
# posts = sqlite_cursor.fetchall()

# for p in posts:
#     if not BlogPost.query.get(p[0]):
#         post = BlogPost(
#             id=p[0],
#             user_id=p[1],
#             title=p[2],
#             slug=p[3],
#             category=p[4],
#             excerpt=p[5],
#             img_path=p[6],
#             created_at=datetime.fromisoformat(p[7]),
#             status=p[8],
#             likes=p[9],
#             comments_count=p[10]
#         )
#         db.session.add(post)

# db.session.commit()
# print(f"✅ {len(posts)} blog posts migrated!")

# # -------------------
# # Comments migrate karna
# # -------------------
# sqlite_cursor.execute("SELECT id, post_id, author, content, created_at FROM comment;")
# comments = sqlite_cursor.fetchall()

# for c in comments:
#     if not Comment.query.get(c[0]):
#         comment = Comment(
#             id=c[0],
#             post_id=c[1],
#             author=c[2],
#             content=c[3],
#             created_at=datetime.fromisoformat(c[4])
#         )
#         db.session.add(comment)

# db.session.commit()
# print(f"✅ {len(comments)} comments migrated!")

# # Close SQLite connection
# sqlite_conn.close()
# print("🎉 Data migration from SQLite to PostgreSQL completed successfully!")




# MigrateData.py
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from app import db, User, BlogPost, Comment  # SQLAlchemy models

# Load .env
load_dotenv()

# PostgreSQL DB session
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# SQLite DB path
sqlite_path = os.path.join("instance", "blog.db")

def migrate_users(sqlite_cursor):
    sqlite_cursor.execute("SELECT * FROM user;")
    users = sqlite_cursor.fetchall()
    print(f"✅ Found {len(users)} users in SQLite.")

    for u in users:
        # Check if already exists in PostgreSQL
        if not User.query.filter_by(email=u[1]).first():
            new_user = User(
                id=u[0],
                email=u[1],
                username=u[2],
                password_hash=u[3],
                role=u[4]
            )
            db.session.add(new_user)
    db.session.commit()
    print("✅ Users migrated successfully.")

def migrate_blog_posts(sqlite_cursor):
    sqlite_cursor.execute("SELECT * FROM blog_post;")
    posts = sqlite_cursor.fetchall()
    print(f"✅ Found {len(posts)} blog posts in SQLite.")

    for p in posts:
        if not BlogPost.query.filter_by(id=p[0]).first():
            new_post = BlogPost(
                id=p[0],
                user_id=p[1],
                title=p[2],
                slug=p[3],
                category=p[4],
                summary=p[5],
                image_path=p[6],  # Ensure images paths are preserved
                created_at=datetime.fromisoformat(p[7]),
                status=p[8],
                likes=p[9],
                comments_count=p[10]
            )
            db.session.add(new_post)
    db.session.commit()
    print("✅ Blog posts migrated successfully.")

def migrate_comments(sqlite_cursor):
    sqlite_cursor.execute("SELECT * FROM comment;")
    comments = sqlite_cursor.fetchall()
    print(f"✅ Found {len(comments)} comments in SQLite.")

    for c in comments:
        if not Comment.query.filter_by(id=c[0]).first():
            new_comment = Comment(
                id=c[0],
                blog_post_id=c[1],
                name=c[2],
                content=c[3],
                created_at=datetime.fromisoformat(c[4])
            )
            db.session.add(new_comment)
    db.session.commit()
    print("✅ Comments migrated successfully.")

def main():
    # Connect SQLite DB
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_cursor = sqlite_conn.cursor()
    print("🔹 Connected to SQLite DB.")

    with app.app_context():
        migrate_users(sqlite_cursor)
        migrate_blog_posts(sqlite_cursor)
        migrate_comments(sqlite_cursor)

    sqlite_conn.close()
    print("✅ Migration completed successfully! All data (including image paths) is now in PostgreSQL.")

if __name__ == "__main__":
    main()

