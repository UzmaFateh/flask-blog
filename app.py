
# import os
# from datetime import datetime
# from flask import Flask, render_template, request, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.utils import secure_filename
# import markdown

# app = Flask(__name__, instance_relative_config=True)

# # Ensure instance folder exists
# os.makedirs(app.instance_path, exist_ok=True)

# # Configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'blog.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # Upload folder for images
# UPLOAD_FOLDER = os.path.join('static', 'uploads')
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# db = SQLAlchemy(app)

# # ------------------------
# # Models
# # ------------------------

# # BlogPost model
# class BlogPost(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(150), nullable=False)
#     slug = db.Column(db.String(150), unique=True, nullable=False)
#     category = db.Column(db.String(100), nullable=False)  # ✅ New field
#     content = db.Column(db.Text, nullable=False)
#     image_filename = db.Column(db.String(100), nullable=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     comments = db.relationship('Comment', backref='post', lazy=True)

# # Comment model
# class Comment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
#     name = db.Column(db.String(100), nullable=False)
#     message = db.Column(db.Text, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

# # ------------------------
# # Routes
# # ------------------------

# # Home Page
# @app.route('/')
# def index():
#     posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
#     return render_template('index.html', posts=posts)

# # New Post Page
# @app.route('/new', methods=['GET', 'POST'])
# def new_post():
#     if request.method == 'POST':
#         title = request.form['title']
#         slug = request.form['slug']
#         category = request.form['category']  # ✅ Get category
#         content = request.form['content']
#         image = request.files['image']

#         image_filename = None
#         if image and image.filename != '':
#             image_filename = secure_filename(image.filename)
#             image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

#         post = BlogPost(
#             title=title,
#             slug=slug,
#             category=category,
#             content=content,
#             image_filename=image_filename
#         )
#         db.session.add(post)
#         db.session.commit()
#         return redirect(url_for('index'))

#     return render_template('new_post.html')

# # Post Detail Page
# @app.route('/post/<slug>', methods=['GET', 'POST'])
# def post_detail(slug):
#     post = BlogPost.query.filter_by(slug=slug).first_or_404()

#     # Handle comment submit
#     if request.method == 'POST':
#         name = request.form['name']
#         message = request.form['message']
#         comment = Comment(post_id=post.id, name=name, message=message)
#         db.session.add(comment)
#         db.session.commit()
#         return redirect(url_for('post_detail', slug=slug))

#     # Convert markdown to HTML
#     content_html = markdown.markdown(post.content)

#     # Get comments
#     comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc()).all()

#     return render_template('post.html', post=post, content_html=content_html, comments=comments)

# # ------------------------
# # Run App
# # ------------------------

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)


import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import markdown

app = Flask(__name__, instance_relative_config=True)

# Ensure instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload folder for images
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# ------------------------
# Models
# ------------------------

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=False)  # ✅ category
    content = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ------------------------
# Routes
# ------------------------

@app.route('/')
def index():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        slug = request.form['slug']
        category = request.form['category']
        content = request.form['content']
        image = request.files['image']

        image_filename = None
        if image and image.filename != '':
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        post = BlogPost(
            title=title,
            slug=slug,
            category=category,
            content=content,
            image_filename=image_filename
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('new_post.html')

@app.route('/post/<slug>', methods=['GET', 'POST'])
def post_detail(slug):
    post = BlogPost.query.filter_by(slug=slug).first_or_404()

    # Handle comment submit
    if request.method == 'POST':
        name = request.form['name']
        message = request.form['message']
        comment = Comment(post_id=post.id, name=name, message=message)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('post_detail', slug=slug))

    content_html = markdown.markdown(post.content)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc()).all()

    return render_template('post.html', post=post, content_html=content_html, comments=comments)

@app.route('/category/<category_name>')
def posts_by_category(category_name):
    posts = BlogPost.query.filter_by(category=category_name).order_by(BlogPost.created_at.desc()).all()
    return render_template('category.html', posts=posts, category=category_name)

# ------------------------
# Run App
# ------------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)






