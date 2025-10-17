import os

from flask_migrate import Migrate
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import markdown
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load .env variables
load_dotenv()

app = Flask(__name__, instance_relative_config=True)
os.makedirs(app.instance_path, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.secret_key = 'secret-key'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key')


# print("SECRET_KEY in production =", app.config['SECRET_KEY'])
# Limit upload size to 10 MB
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB

# Make sure the upload folder exists
app.config['UPLOAD_FOLDER'] = 'static/uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)





UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ------------------------
# Email Helper Functions
# ------------------------
def send_email(to_email, subject, body):
    try:
        mail_user = os.getenv("MAIL_USERNAME")
        mail_pass = os.getenv("MAIL_PASSWORD")
        admin_email = os.getenv("ADMIN_EMAIL")

        msg = MIMEMultipart()
        msg['From'] = admin_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(os.getenv("MAIL_SERVER"), int(os.getenv("MAIL_PORT")))
        server.starttls()
        server.login(mail_user, mail_pass)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Email sending failed:", e)

def send_post_submission_email(user_email, post_title):
    subject = "Your blog post is under review"
    body = f"Hi,\n\nYour post titled '{post_title}' has been submitted for review. It will be published once approved by the admin.\n\nThank you!"
    send_email(user_email, subject, body)

def send_post_approval_email(user_email, post_title):
    subject = "Your blog post has been published"
    body = f"Hi,\n\nGood news! Your post titled '{post_title}' has been approved and published.\n\nThank you for contributing!"
    send_email(user_email, subject, body)

def send_post_rejection_email(user_email, post_title):
    subject = "Your blog post was not approved"
    body = f"Hi,\n\nWe reviewed your post titled '{post_title}' but unfortunately it was not approved.\n\nIf you have any questions, feel free to contact us."
    send_email(user_email, subject, body)

def send_post_deletion_email(user_email, post_title):
    subject = "Your blog post has been deleted"
    body = f"Hi,\n\nWe wanted to let you know that your post titled '{post_title}' has been deleted by the admin.\n\nIf you have questions, please contact us."
    send_email(user_email, subject, body)

# ------------------------
# Models
# ------------------------
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy=True)
    status = db.Column(db.String(20), default='Pending')
    views = db.Column(db.Integer, default=0)
    is_editors_pick = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='Pending')  # Pending / Approved / Rejected

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    posts = db.relationship('BlogPost', backref='author', lazy=True)

# ------------------------
# Helper for unique slug
# ------------------------
def generate_unique_slug(title):
    base_slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    slug = base_slug
    counter = 1
    while BlogPost.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug

# ------------------------
# Routes
# ------------------------
# @app.route('/')
# def index():
#     # ✅ FIXED: Only show Approved posts on homepage
#     latest_posts = BlogPost.query.filter_by(status='Approved').order_by(BlogPost.created_at.desc()).limit(8).all()
#     popular_posts = BlogPost.query.filter_by(status='Approved').order_by(BlogPost.views.desc()).limit(5).all()
#     more_posts = BlogPost.query.filter_by(status='Approved').order_by(BlogPost.created_at.desc()).offset(8).limit(8).all()
#     editor_picks = BlogPost.query.filter_by(is_editors_pick=True, status='Approved').order_by(BlogPost.created_at.desc()).limit(10).all()

#     return render_template(
#         'index.html',
#         posts=latest_posts,
#         popular_posts=popular_posts,
#         more_posts=more_posts,
#         editor_picks=editor_picks
#     )

# @app.route('/all-posts')
# def all_posts():
#     POSTS_PER_PAGE = 16
#     page = request.args.get('page', 1, type=int)
#     query = BlogPost.query.filter_by(status='Approved').order_by(BlogPost.created_at.desc())
#     total_posts = query.count()
#     total_pages = (total_posts + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE
#     posts = query.offset((page - 1) * POSTS_PER_PAGE).limit(POSTS_PER_PAGE).all()
#     return render_template('all_posts.html', posts=posts, page=page, total_pages=total_pages)

@app.route('/new', methods=['GET', 'POST'])
def new_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'user':
        return "Only users can create posts."

    categories = ["Technology", "Health", "Travel", "Food", "Education", "Others"]

    if request.method == 'POST':
        title = request.form['title']
        slug = generate_unique_slug(title)
        category = request.form['category']
        content = request.form['content']
        image = request.files['image']
        image_filename = None
        if image and image.filename != '':
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        post = BlogPost(
            user_id=session['user_id'],
            title=title,
            slug=slug,
            category=category,
            content=content,
            image_filename=image_filename
        )
        db.session.add(post)
        db.session.commit()

        user_email = User.query.get(session['user_id']).email
        send_post_submission_email(user_email, title)

        flash('Your post has been submitted for review!', 'info')
        return redirect(url_for('index'))

    return render_template('new_post.html', categories=categories)


# @app.route('/new', methods=['GET', 'POST'])
# def new_post():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     if session.get('role') != 'user':
#         return "Only users can create posts."

#     categories = ["Technology", "Health", "Travel", "Food", "Education", "Others"]

#     if request.method == 'POST':
#         # Use .get() instead of ['key'] to avoid KeyError or hanging
#         title = request.form.get('title')
#         category = request.form.get('category')
#         content = request.form.get('content')
#         image = request.files.get('image')

#         if not title or not content:
#             flash('Please fill in all required fields.', 'error')
#             return redirect(url_for('new_post'))

#         # Generate slug after confirming title exists
#         slug = generate_unique_slug(title)

#         # Handle image upload
#         image_filename = None
#         if image and image.filename:
#             image_filename = secure_filename(image.filename)
#             image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

#         # Save post
#         post = BlogPost(
#             user_id=session['user_id'],
#             title=title,
#             slug=slug,
#             category=category,
#             content=content,
#             image_filename=image_filename
#         )
#         db.session.add(post)
#         db.session.commit()

#         # Send confirmation email
#         user_email = User.query.get(session['user_id']).email
#         send_post_submission_email(user_email, title)

#         flash('Your post has been submitted for review!', 'info')
#         return redirect(url_for('index'))

#     return render_template('new_post.html', categories=categories)



@app.context_processor
def inject_categories():
    categories = ['Technology', 'Health', 'Travel', 'Food', 'Education', 'Others']
    return dict(categories=categories)


@app.route('/post/<slug>', methods=['GET', 'POST'])
def post_detail(slug):
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    post.views = (post.views or 0) + 1
    db.session.commit()

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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for('signup'))
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, username=username, password=hashed_password, role='user')
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash("Invalid email or password!", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin_dashboard.html', posts=posts)

@app.route('/approve_post/<int:post_id>')
def approve_post(post_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    post = BlogPost.query.get_or_404(post_id)
    post.status = 'Approved'
    db.session.commit()
    user = User.query.get(post.user_id)
    if user:
        send_post_approval_email(user.email, post.title)
    return redirect(url_for('admin_dashboard'))

@app.route('/reject_post/<int:post_id>')
def reject_post(post_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    post = BlogPost.query.get_or_404(post_id)
    user = User.query.get(post.user_id)
    if user:
        send_post_rejection_email(user.email, post.title)
    db.session.delete(post)
    db.session.commit()
    flash("Post rejected and user notified.", "info")
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    post = BlogPost.query.get_or_404(post_id)
    user = User.query.get(post.user_id)
    if user:
        send_post_deletion_email(user.email, post.title)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/editors_picks')
def editors_picks():
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.filter_by(is_editors_pick=True)\
        .order_by(BlogPost.created_at.desc())\
        .paginate(page=page, per_page=16)
    return render_template('editors_picks.html', posts=posts)

@app.route('/toggle_editors_pick/<int:post_id>', methods=['POST'])
def toggle_editors_pick(post_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    post = BlogPost.query.get_or_404(post_id)
    data = request.get_json()
    post.is_editors_pick = data.get('is_editors_pick', False)
    db.session.commit()
    return {'success': True}

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    post = BlogPost.query.get_or_404(post_id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.category = request.form['category']
        post.content = request.form['content']
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_post.html', post=post)

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        slug = generate_unique_slug(title)
        category = request.form['category']
        content = request.form['content']
        image_file = request.files['image']
        image_filename = None
        if image_file and image_file.filename != '':
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join('static/uploads', image_filename)
            image_file.save(image_path)

        new_post = BlogPost(
            user_id=session['user_id'],
            title=title,
            slug=slug,
            category=category,
            content=content,
            image_filename=image_filename,
            status='Pending'
        )
        db.session.add(new_post)
        db.session.commit()

        user_email = User.query.get(session['user_id']).email
        send_post_submission_email(user_email, title)

        flash('Your post has been submitted for review!', 'info')
        return redirect(url_for('index'))

    return render_template('add_post.html')

# ------------------------
# Create DB + secure admin
# ------------------------
with app.app_context():
    db.create_all()
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    if not User.query.filter_by(email=admin_email).first():
        hashed_admin_pass = generate_password_hash(admin_password)
        admin = User(email=admin_email, username=admin_username, password=hashed_admin_pass, role="admin")
        db.session.add(admin)
        db.session.commit()

# if __name__ == '__main__':
#     app.run(debug=True)


# for render deployment
# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8080))
#     app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

