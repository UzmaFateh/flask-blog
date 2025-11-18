import os
import re
import smtplib
import markdown
import bleach
from markupsafe import Markup
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Cloudinary Imports
import cloudinary
import cloudinary.uploader







from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))


# Load .env variables
load_dotenv()

# ------------------------
# Flask app initialization & Config
# ------------------------
app = Flask(__name__, instance_relative_config=True)
os.makedirs(app.instance_path, exist_ok=True)



app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 # 10 MB

# Local UPLOAD_FOLDER path is now irrelevant for storage, but kept for context if needed
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
migrate = Migrate(app, db)



# ------------------------
try:
    cloudinary.config(
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key = os.getenv('CLOUDINARY_API_KEY'),
        api_secret = os.getenv('CLOUDINARY_API_SECRET')
    )
except Exception as e:
    print(f"Cloudinary Configuration Failed. Check .env file: {e}")


# ------------------------
# Helper Functions
# ------------------------

def get_cloudinary_url(public_id, width=800, height=600):
    """Generates an optimized Cloudinary URL from a public ID."""
    if not public_id:
        # Placeholder image URL ya default image ka public ID return kar sakte hain
        return "/static/images/default_placeholder.png" 
        
    url = cloudinary.utils.cloudinary_url(
        public_id,
        format="jpg",
        crop="fill",
        width=width,
        height=height,
        secure=True
    )[0]
    return url

def delete_cloudinary_image(public_id):
    """Deletes an image from Cloudinary using its public ID."""
    if public_id and public_id != 'default_placeholder':
        try:
            cloudinary.uploader.destroy(public_id)
            print(f"Cloudinary image deleted successfully: {public_id}")
        except Exception as e:
            print(f"Failed to delete Cloudinary image {public_id}: {e}")

# Email Helper Functions (unchanged logic)
def send_email(to_email, subject, body):
    """Sends an email using configured SMTP settings."""
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
        print(f"Email sent successfully to {to_email}.")
    except Exception as e:
        print(f"Email sending failed to {to_email}: {e}")

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
    body = f"Hi,\n\nWe reviewed your post titled '{post_title}' but unfortunately it was not approved and has been removed.\n\nIf you have any questions, feel free to contact us."
    send_email(user_email, subject, body)

def send_post_deletion_email(user_email, post_title):
    subject = "Your blog post has been deleted"
    body = f"Hi,\n\nWe wanted to let you know that your post titled '{post_title}' has been deleted by the admin.\n\nIf you have questions, please contact us."
    send_email(user_email, subject, body)

def render_secure_markdown(content):
    """Converts Markdown to HTML and sanitizes it using bleach to prevent XSS."""
    allowed_tags = ['a', 'p', 'b', 'i', 'em', 'strong', 'ul', 'ol', 'li', 'blockquote',
                    'code', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'img']
    allowed_attrs = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title']
    }
    
    html_content = markdown.markdown(content, extensions=['fenced_code', 'codehilite'])
    
    sanitized_html = bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )
    return Markup(sanitized_html)

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
    # image_filename will now store the Cloudinary Public ID
    image_filename = db.Column(db.String(100), nullable=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy=True)
    status = db.Column(db.String(20), default='Pending') 
    views = db.Column(db.Integer, default=0)
    is_editors_pick = db.Column(db.Boolean, default=False)

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
    role = db.Column(db.String(10), nullable=False) # user / admin
    posts = db.relationship('BlogPost', backref='author', lazy=True)

# ------------------------
# Helper for unique slug
# ------------------------
def generate_unique_slug(title):
    """Generates a URL-safe, unique slug from a title."""
    base_slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    slug = base_slug
    counter = 1
    while BlogPost.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug

# ------------------------
# Context Processors
# ------------------------
@app.context_processor
def inject_categories():
    categories = ['Technology', 'Health', 'Travel', 'Food', 'Education', 'Others']
    return dict(categories=categories)

@app.context_processor
def inject_cloudinary_helper():
    """Jinja templates mein get_cloudinary_url use karne ke liye helper."""
    return dict(get_cloudinary_url=get_cloudinary_url)


# ------------------------
# Routes
# ------------------------
@app.route('/')
def index():
    """Homepage: Shows latest, popular, and editor-picked approved posts."""
    latest_posts = BlogPost.query.filter_by(status='Approved').order_by(BlogPost.created_at.desc()).limit(8).all()
    popular_posts = BlogPost.query.filter_by(status='Approved').order_by(BlogPost.views.desc()).limit(5).all()
    more_posts = BlogPost.query.filter_by(status='Approved').order_by(BlogPost.created_at.desc()).offset(8).limit(8).all()
    editor_picks = BlogPost.query.filter_by(is_editors_pick=True, status='Approved').order_by(BlogPost.created_at.desc()).limit(10).all()

    return render_template(
        'index.html',
        posts=latest_posts,
        popular_posts=popular_posts,
        more_posts=more_posts,
        editor_picks=editor_picks
    )

@app.route('/all-posts')
def all_posts():
    """View for all approved posts with pagination."""
    POSTS_PER_PAGE = 16
    page = request.args.get('page', 1, type=int)
    query = BlogPost.query.filter_by(status='Approved').order_by(BlogPost.created_at.desc())
    pagination = query.paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
    
    return render_template('all_posts.html', posts=pagination.items, pagination=pagination)

@app.route('/new', methods=['GET', 'POST'])
def new_post():
    """Route for a standard user to submit a post for approval (status=Pending)."""
    if 'user_id' not in session:
        flash('You must be logged in to create a post.', 'warning')
        return redirect(url_for('login'))
    
    if session.get('role') != 'user':
        flash('Admins should use the admin dashboard to create approved posts.', 'info')

    categories = ["Technology", "Health", "Travel", "Food", "Education", "Others"]

    if request.method == 'POST':
        title = request.form['title']
        slug = generate_unique_slug(title)
        category = request.form['category']
        content = request.form['content']
        image = request.files.get('image')
        image_public_id = None
        
        # --- Cloudinary Upload Logic ---
        if image and image.filename != '':
            try:
                # Upload to Cloudinary (folder 'blog_posts' mein store karein)
                upload_result = cloudinary.uploader.upload(image, folder="blog_posts")
                image_public_id = upload_result['public_id']
            except Exception as e:
                flash(f"Image upload failed: {e}", 'error')
                return redirect(url_for('new_post'))
        # -------------------------------

        post = BlogPost(
            user_id=session['user_id'],
            title=title,
            slug=slug,
            category=category,
            content=content,
            image_filename=image_public_id, # Storing public ID
            status='Pending'
        )
        db.session.add(post)
        db.session.commit()

        user_email = User.query.get(session['user_id']).email
        send_post_submission_email(user_email, title)

        flash('Your post has been submitted for review!', 'info')
        return redirect(url_for('index'))

    return render_template('new_post.html', categories=categories)


@app.route('/post/<slug>', methods=['GET', 'POST'])
def post_detail(slug):
    """Shows post details, handles view count, and accepts comments."""
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    
    if post.status != 'Approved' and session.get('role') != 'admin':
        flash("Post not found or is currently under review.", "danger")
        return redirect(url_for('index'))
    
    # View counter (NOTE: Optimize this for production by using caching)
    post.views = (post.views or 0) + 1
    db.session.commit()

    if request.method == 'POST':
        name = request.form['name']
        message = request.form['message']
        comment = Comment(post_id=post.id, name=name, message=message)
        db.session.add(comment)
        db.session.commit()
        flash('Comment submitted!', 'success')
        return redirect(url_for('post_detail', slug=slug))

    content_html = render_secure_markdown(post.content)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc()).all()
    
    return render_template('post.html', post=post, content_html=content_html, comments=comments)

@app.route('/category/<category_name>')
def posts_by_category(category_name):
    """Lists all approved posts belonging to a specific category."""
    posts = BlogPost.query.filter_by(category=category_name, status='Approved').order_by(BlogPost.created_at.desc()).all()
    return render_template('category.html', posts=posts, category=category_name)

# ------------------------
# Auth Routes
# ------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handles new user registration."""
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
    """Handles user login and session creation."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            session['username'] = user.username
            
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash("Invalid email or password!", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Clears the session and logs the user out."""
    session.clear()
    return redirect(url_for('index'))

# ------------------------
# Admin Routes
# ------------------------
def admin_required(f):
    """Decorator to enforce admin role."""
    def wrapper(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash("Access denied: Admin privileges required.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard showing all posts for review/management."""
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin_dashboard.html', posts=posts)

@app.route('/approve_post/<int:post_id>')
@admin_required
def approve_post(post_id):
    """Approves a post, changes its status, and notifies the author."""
    post = BlogPost.query.get_or_404(post_id)
    post.status = 'Approved'
    db.session.commit()
    user = User.query.get(post.user_id)
    if user:
        send_post_approval_email(user.email, post.title)
    flash(f"Post '{post.title}' approved and author notified.", 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/reject_post/<int:post_id>')
@admin_required
def reject_post(post_id):
    """Rejects a post, deletes it from DB and Cloudinary, and notifies the author."""
    post = BlogPost.query.get_or_404(post_id)
    
    # 1. Image deletion from Cloudinary
    delete_cloudinary_image(post.image_filename)
    
    # 2. Email notification
    user = User.query.get(post.user_id)
    if user:
        send_post_rejection_email(user.email, post.title)
        
    # 3. Database deletion
    db.session.delete(post)
    db.session.commit()
    flash(f"Post '{post.title}' rejected, deleted, and author notified.", "info")
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_post/<int:post_id>')
@admin_required
def delete_post(post_id):
    """Deletes an already published post from DB and Cloudinary, and notifies the author."""
    post = BlogPost.query.get_or_404(post_id)
    
    # 1. Image deletion from Cloudinary
    delete_cloudinary_image(post.image_filename)
    
    # 2. Email notification
    user = User.query.get(post.user_id)
    if user:
        send_post_deletion_email(user.email, post.title)
        
    # 3. Database deletion
    db.session.delete(post)
    db.session.commit()
    flash(f"Post '{post.title}' deleted and author notified.", "warning")
    return redirect(url_for('admin_dashboard'))


@app.route('/editors_picks')
def editors_picks():
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.filter_by(is_editors_pick=True)\
        .order_by(BlogPost.created_at.desc())\
        .paginate(page=page, per_page=16)
    return render_template('editors_picks.html', posts=posts)

# @app.route('/toggle_editors_pick/<int:post_id>', methods=['POST'])
# def toggle_editors_pick(post_id):
#     if 'user_id' not in session or session.get('role') != 'admin':
#         return redirect(url_for('login'))
#     post = BlogPost.query.get_or_404(post_id)
#     data = request.get_json()
#     post.is_editors_pick = data.get('is_editors_pick', False)
#     db.session.commit()
#     return {'success': True}
@app.route('/toggle_editors_pick/<int:post_id>', methods=['POST'])
@admin_required
def toggle_editors_pick(post_id):
    """Toggles the is_editors_pick status via AJAX."""
    post = BlogPost.query.get_or_404(post_id)
    if post.status == 'Approved':
        data = request.get_json()
        post.is_editors_pick = data.get('is_editors_pick', False)
        db.session.commit()
        return {'success': True}
    return {'success': False, 'message': 'Only approved posts can be Editor\'s Picks.'}, 400




@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@admin_required
def edit_post(post_id):
    """Allows admin to edit any post."""
    post = BlogPost.query.get_or_404(post_id)
    categories = ["Technology", "Health", "Travel", "Food", "Education", "Others"]
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.category = request.form['category']
        post.content = request.form['content']
        image = request.files.get('image')

        # --- Cloudinary Re-upload/Update Logic ---
        if image and image.filename != '':
            try:
                # Delete old image if it exists
                delete_cloudinary_image(post.image_filename) 
                # Upload new image
                upload_result = cloudinary.uploader.upload(image, folder="blog_posts")
                post.image_filename = upload_result['public_id']
            except Exception as e:
                flash(f"Image re-upload failed: {e}", 'error')
                return redirect(url_for('edit_post', post_id=post_id))
        # -------------------------------
        
        db.session.commit()
        flash(f"Post '{post.title}' updated.", 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_post.html', post=post, categories=categories)

@app.route('/add_post', methods=['GET', 'POST'])
@admin_required
def add_post():
    """Admin-only route for creating posts that are automatically Approved."""
    categories = ["Technology", "Health", "Travel", "Food", "Education", "Others"]

    if request.method == 'POST':
        title = request.form['title']
        slug = generate_unique_slug(title)
        category = request.form['category']
        content = request.form['content']
        image_file = request.files.get('image')
        image_public_id = None

        # --- Cloudinary Upload Logic ---
        if image_file and image_file.filename != '':
            try:
                upload_result = cloudinary.uploader.upload(image_file, folder="blog_posts")
                image_public_id = upload_result['public_id']
            except Exception as e:
                flash(f"Image upload failed: {e}", 'error')
                return redirect(url_for('add_post'))
        # -------------------------------

        new_post = BlogPost(
            user_id=session['user_id'],
            title=title,
            slug=slug,
            category=category,
            content=content,
            image_filename=image_public_id, # Storing public ID
            status='Approved'
        )
        db.session.add(new_post)
        db.session.commit()

        flash('Post created and immediately published!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_post.html', categories=categories)




@app.route('/about')
def about():
    """Simple About Us page."""
    return render_template('about.html')


# ------------------------
# DB Setup and Seeding
# ------------------------
with app.app_context():
    db.create_all()
    
    # Check and create default admin user
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        hashed_admin_pass = generate_password_hash(admin_password)
        admin = User(email=admin_email, username=admin_username, password=hashed_admin_pass, role="admin")
        db.session.add(admin)
        db.session.commit()

    # Seed a sample post if none exists
    if not BlogPost.query.first():
        # Using a dummy public ID for the seeded post. 
        # In a real scenario, you'd upload a default image to Cloudinary and use its Public ID here.
        DUMMY_PUBLIC_ID = "default_placeholder" 
        
        sample_post = BlogPost(
            user_id=admin.id,
            title="Cloudinary Integration Successful!",
            slug="cloudinary-integration-successful",
            category="Technology",
            content="Congratulations! Image storage has been moved to Cloudinary. This post uses a dummy Public ID: **`default_placeholder`**. To see an actual image, create a new post with a file.",
            status="Approved",
            image_filename=DUMMY_PUBLIC_ID,
            is_editors_pick=True
        )
        db.session.add(sample_post)
        db.session.commit()


# ------------------------
# App Entry Point
# ------------------------
if __name__ == '__main__':
    # Use debug=True for local development
    app.run(debug=True)