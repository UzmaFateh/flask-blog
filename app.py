# import os
# from datetime import datetime
# from flask import Flask, render_template, request, redirect, url_for,flash
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

# class BlogPost(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(150), nullable=False)
#     slug = db.Column(db.String(150), unique=True, nullable=False)
#     category = db.Column(db.String(100), nullable=False)  # ✅ category
#     content = db.Column(db.Text, nullable=False)
#     image_filename = db.Column(db.String(100), nullable=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     comments = db.relationship('Comment', backref='post', lazy=True)
#     status = db.Column(db.String(20), default='Pending')  # 'Pending' or 'Approved'
   






# class Comment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
#     name = db.Column(db.String(100), nullable=False)
#     message = db.Column(db.Text, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

# # ------------------------


# # user modal

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100), unique=True, nullable=False)
#     password = db.Column(db.String(100), nullable=False)
#     role = db.Column(db.String(10), nullable=False)  # 'admin' or 'user'
# # ---------------------------------------------
# # Routes
# # ------------------------

# # @app.route('/')
# # def index():
# #     posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
# #     return render_template('index.html', posts=posts)

# @app.route('/')
# def index():
#     posts = BlogPost.query.filter_by(status='Approved').order_by(BlogPost.created_at.desc()).all()
#     return render_template('index.html', posts=posts)


# # @app.route('/new', methods=['GET', 'POST'])
# # def new_post():
# #     if request.method == 'POST':
# #         title = request.form['title']
# #         slug = request.form['slug']
# #         category = request.form['category']
# #         content = request.form['content']
# #         image = request.files['image']

# #         image_filename = None
# #         if image and image.filename != '':
# #             image_filename = secure_filename(image.filename)
# #             image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

# #         post = BlogPost(
# #             title=title,
# #             slug=slug,
# #             category=category,
# #             content=content,
# #             image_filename=image_filename
# #         )
# #         db.session.add(post)
# #         db.session.commit()
# #         return redirect(url_for('index'))

# #     return render_template('new_post.html')

# #Restrict New Post Page

# @app.route('/new', methods=['GET', 'POST'])
# def new_post():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     # Agar sirf user role allow hai, admin nahi
#     if session.get('role') != 'user':
#         return "Only users can create posts."

#     if request.method == 'POST':
#         title = request.form['title']
#         slug = request.form['slug']
#         category = request.form['category']
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
# #------------------------------------------------------------------------

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

#     content_html = markdown.markdown(post.content)
#     comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc()).all()

#     return render_template('post.html', post=post, content_html=content_html, comments=comments)

# @app.route('/category/<category_name>')
# def posts_by_category(category_name):
#     posts = BlogPost.query.filter_by(category=category_name).order_by(BlogPost.created_at.desc()).all()
#     return render_template('category.html', posts=posts, category=category_name)

# # ------------------------

# #login method for user

# from flask import session

# app.secret_key = 'secret-key'  # Session ke liye zaroori

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         user = User.query.filter_by(username=username, password=password).first()

#         if user:
#             session['user_id'] = user.id
#             session['role'] = user.role
#             if user.role == 'admin':
#                 return redirect(url_for('admin_dashboard'))
#             else:
#                 return redirect(url_for('index'))
#         else:
#             return "Invalid credentials"

#     return render_template('login.html')
# #------------------------------------------------------------

# #create admin n user for first time

# with app.app_context():
#     db.create_all()
#     if not User.query.filter_by(username="admin").first():
#         admin = User(username="admin", password="admin123", role="admin")
#         db.session.add(admin)
#     if not User.query.filter_by(username="user1").first():
#         user = User(username="user1", password="user123", role="user")
#         db.session.add(user)
#     db.session.commit()



# #Admin Dashboard Route

# # @app.route('/admin')
# # def admin_dashboard():
# #     if 'role' in session and session['role'] == 'admin':
# #         posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
# #         return render_template('admin_dashboard.html', posts=posts)
# #     return redirect(url_for('login'))

# #--------------------------------------------
# # Edit Post
# # @app.route('/admin/edit/<int:post_id>', methods=['GET', 'POST'])
# # def edit_post(post_id):
# #     if 'role' not in session or session['role'] != 'admin':
# #         return redirect(url_for('login'))

# #     post = BlogPost.query.get_or_404(post_id)

# #     if request.method == 'POST':
# #         post.title = request.form['title']
# #         post.slug = request.form['slug']
# #         post.category = request.form['category']
# #         post.content = request.form['content']

# #         image = request.files['image']
# #         if image and image.filename != '':
# #             image_filename = secure_filename(image.filename)
# #             image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
# #             post.image_filename = image_filename

# #         db.session.commit()
# #         return redirect(url_for('admin_dashboard'))

# #     return render_template('edit_post.html', post=post)


# # # Delete Post
# # @app.route('/admin/delete/<int:post_id>')
# # def delete_post(post_id):
# #     if 'role' not in session or session['role'] != 'admin':
# #         return redirect(url_for('login'))

# #     post = BlogPost.query.get_or_404(post_id)
# #     db.session.delete(post)
# #     db.session.commit()
# #     return redirect(url_for('admin_dashboard'))




# # @app.route('/admin')
# # def admin_dashboard():
# #     if 'user_id' not in session or session.get('role') != 'admin':
# #         return redirect(url_for('login'))
# #     posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
# #     return render_template('admin_dashboard.html', posts=posts)

# @app.route('/admin')
# def admin_dashboard():
#     if 'user_id' not in session or session.get('role') != 'admin':
#         return redirect(url_for('login'))
#     posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
#     return render_template('admin_dashboard.html', posts=posts)


# @app.route('/approve_post/<int:post_id>')
# def approve_post(post_id):
#     if 'user_id' not in session or session.get('role') != 'admin':
#         return redirect(url_for('login'))

#     post = BlogPost.query.get_or_404(post_id)
#     post.status = 'Approved'
#     db.session.commit()
#     flash('Post approved successfully!', 'success')
#     return redirect(url_for('admin_dashboard'))
# #------------------------------------------------------------------------------------------------
# #delete-post
# @app.route('/delete_post/<int:post_id>')
# def delete_post(post_id):
#     if 'user_id' not in session or session.get('role') != 'admin':
#         return redirect(url_for('login'))
#     post = BlogPost.query.get_or_404(post_id)
#     db.session.delete(post)
#     db.session.commit()
#     return redirect(url_for('admin_dashboard'))

# @app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
# def edit_post(post_id):
#     if 'user_id' not in session or session.get('role') != 'admin':
#         return redirect(url_for('login'))
#     post = BlogPost.query.get_or_404(post_id)
#     if request.method == 'POST':
#         post.title = request.form['title']
#         post.category = request.form['category']
#         post.content = request.form['content']
#         db.session.commit()
#         return redirect(url_for('admin_dashboard'))
#     return render_template('edit_post.html', post=post)



# #-----------------------------------------------------------
# #generate_slug
# import re

# def generate_slug(title):
#     return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

# #add post by admin

# # @app.route('/add_post', methods=['GET', 'POST'])
# # def add_post():
# #     if request.method == 'POST':
# #         title = request.form['title']
# #         category = request.form['category']
# #         content = request.form['content']
        
# #         slug = generate_slug(title)  # Slug banana zaroori hai
        
# #         new_post = BlogPost(title=title, category=category, content=content, slug=slug)
# #         db.session.add(new_post)
# #         db.session.commit()
        
# #         return redirect(url_for('admin_dashboard'))
    
# #     return render_template('add_post.html')


# #--------------------------------------------------------------------------
# # @app.route('/add_post', methods=['GET', 'POST'])
# # def add_post():
# #     if 'user_id' not in session:
# #         return redirect(url_for('login'))

# #     if request.method == 'POST':
# #         new_post = BlogPost(
# #             title=request.form['title'],
# #             category=request.form['category'],
# #             content=request.form['content'],
# #             status='Pending'  # ✅ Default Pending
# #         )
# #         db.session.add(new_post)
# #         db.session.commit()
# #         flash('Your post is submitted for review!', 'info')
# #         return redirect(url_for('index'))

# #     return render_template('add_post.html')
# #------------------------------------------------------------------------------



# @app.route('/add_post', methods=['GET', 'POST'])
# def add_post():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     if request.method == 'POST':
#         title = request.form['title']
#         slug = request.form['slug']  # ✅ required from form
#         category = request.form['category']
#         content = request.form['content']

#         # ✅ Handle image upload
#         image_file = request.files['image']
#         image_filename = None
#         if image_file and image_file.filename != '':
#             image_filename = secure_filename(image_file.filename)
#             image_path = os.path.join('static/uploads', image_filename)
#             image_file.save(image_path)

#         new_post = BlogPost(
#             title=title,
#             slug=slug,
#             category=category,
#             content=content,
#             image_filename=image_filename,
#             status='Pending'  # ✅ admin approval
#         )

#         db.session.add(new_post)
#         db.session.commit()
#         flash('Your post has been submitted for review!', 'info')
#         return redirect(url_for('index'))

#     return render_template('add_post.html')





# #logout route
# @app.route('/logout')
# def logout():
#     session.clear()  # saare session data delete ho jayenge
#     return redirect(url_for('login'))
# #------------------------------------------------------------
# # Run App
# # ------------------------

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)

#######################################################################################################
#######################################################################################################
#######################################################################################################
# import os
# from datetime import datetime
# from flask import Flask, render_template, request, redirect, url_for, flash, session
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.utils import secure_filename
# import markdown
# import re

# app = Flask(__name__, instance_relative_config=True)

# # Ensure instance folder exists
# os.makedirs(app.instance_path, exist_ok=True)

# # Configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'blog.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.secret_key = 'secret-key'

# # Upload folder
# UPLOAD_FOLDER = os.path.join('static', 'uploads')
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# db = SQLAlchemy(app)

# # ------------------------
# # Models
# # ------------------------
# class BlogPost(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(150), nullable=False)
#     slug = db.Column(db.String(150), unique=True, nullable=False)
#     category = db.Column(db.String(100), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     image_filename = db.Column(db.String(100), nullable=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     comments = db.relationship('Comment', backref='post', lazy=True)
#     status = db.Column(db.String(20), default='Pending')

# class Comment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
#     name = db.Column(db.String(100), nullable=False)
#     message = db.Column(db.Text, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(150), unique=True, nullable=False)  # ✅ new email field
#     username = db.Column(db.String(100), unique=True, nullable=False)
#     password = db.Column(db.String(100), nullable=False)
#     role = db.Column(db.String(10), nullable=False)  # 'admin' or 'user'

# # ------------------------
# # Routes
# # ------------------------
# @app.route('/')
# def index():
#     posts = BlogPost.query.filter_by(status='Approved').order_by(BlogPost.created_at.desc()).all()
#     return render_template('index.html', posts=posts)

# @app.route('/new', methods=['GET', 'POST'])
# def new_post():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#     if session.get('role') != 'user':
#         return "Only users can create posts."

#     if request.method == 'POST':
#         title = request.form['title']
#         slug = request.form['slug']
#         category = request.form['category']
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
#         flash('Your post has been submitted for review!', 'info')
#         return redirect(url_for('index'))
        
# #        

#     return render_template('new_post.html')

# @app.route('/post/<slug>', methods=['GET', 'POST'])
# def post_detail(slug):
#     post = BlogPost.query.filter_by(slug=slug).first_or_404()
#     if request.method == 'POST':
#         name = request.form['name']
#         message = request.form['message']
#         comment = Comment(post_id=post.id, name=name, message=message)
#         db.session.add(comment)
#         db.session.commit()
#         return redirect(url_for('post_detail', slug=slug))

#     content_html = markdown.markdown(post.content)
#     comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc()).all()
#     return render_template('post.html', post=post, content_html=content_html, comments=comments)

# @app.route('/category/<category_name>')
# def posts_by_category(category_name):
#     posts = BlogPost.query.filter_by(category=category_name).order_by(BlogPost.created_at.desc()).all()
#     return render_template('category.html', posts=posts, category=category_name)

# # ✅ Signup with Email, Username, Password
# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         email = request.form['email']
#         username = request.form['username']
#         password = request.form['password']

#         if User.query.filter_by(email=email).first():
#             flash("Email already registered!", "danger")
#             return redirect(url_for('signup'))
#         if User.query.filter_by(username=username).first():
#             flash("Username already exists!", "danger")
#             return redirect(url_for('signup'))

#         new_user = User(email=email, username=username, password=password, role='user')
#         db.session.add(new_user)
#         db.session.commit()
#         flash("Account created! Please login.", "success")
#         return redirect(url_for('login'))

#     return render_template('signup.html')

# # ✅ Login with Email + Password only
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         user = User.query.filter_by(email=email, password=password).first()

#         if user:
#             session['user_id'] = user.id
#             session['role'] = user.role
#             if user.role == 'admin':
#                 return redirect(url_for('admin_dashboard'))
#             else:
#                 return redirect(url_for('index'))
#         else:
#             flash("Invalid email or password!", "danger")

#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('login'))

# @app.route('/admin')
# def admin_dashboard():
#     if 'user_id' not in session or session.get('role') != 'admin':
#         return redirect(url_for('login'))
#     posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
#     return render_template('admin_dashboard.html', posts=posts)

# @app.route('/approve_post/<int:post_id>')
# def approve_post(post_id):
#     if 'user_id' not in session or session.get('role') != 'admin':
#         return redirect(url_for('login'))
#     post = BlogPost.query.get_or_404(post_id)
#     post.status = 'Approved'
#     db.session.commit()
#     # flash('Post approved successfully!', 'success')
#     return redirect(url_for('admin_dashboard'))

# @app.route('/delete_post/<int:post_id>')
# def delete_post(post_id):
#     if 'user_id' not in session or session.get('role') != 'admin':
#         return redirect(url_for('login'))
#     post = BlogPost.query.get_or_404(post_id)
#     db.session.delete(post)
#     db.session.commit()
#     return redirect(url_for('admin_dashboard'))

# @app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
# def edit_post(post_id):
#     if 'user_id' not in session or session.get('role') != 'admin':
#         return redirect(url_for('login'))
#     post = BlogPost.query.get_or_404(post_id)
#     if request.method == 'POST':
#         post.title = request.form['title']
#         post.category = request.form['category']
#         post.content = request.form['content']
#         db.session.commit()
#         return redirect(url_for('admin_dashboard'))
#     return render_template('edit_post.html', post=post)

# def generate_slug(title):
#     return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

# @app.route('/add_post', methods=['GET', 'POST'])
# def add_post():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     if request.method == 'POST':
#         title = request.form['title']
#         slug = request.form['slug']
#         category = request.form['category']
#         content = request.form['content']
#         image_file = request.files['image']
#         image_filename = None
#         if image_file and image_file.filename != '':
#             image_filename = secure_filename(image_file.filename)
#             image_path = os.path.join('static/uploads', image_filename)
#             image_file.save(image_path)

#         new_post = BlogPost(
#             title=title,
#             slug=slug,
#             category=category,
#             content=content,
#             image_filename=image_filename,
#             status='Pending'
#         )
#         db.session.add(new_post)
#         db.session.commit()
#         flash('Your post has been submitted for review!', 'info')
#         return redirect(url_for('index'))

#     return render_template('add_post.html')

# # ✅ Create DB + Admin with email if not exists
# with app.app_context():
#     db.create_all()
#     if not User.query.filter_by(username="admin").first():
#         admin = User(email="admin@example.com", username="admin", password="admin123", role="admin")
#         db.session.add(admin)
#         db.session.commit()

# if __name__ == '__main__':
#     app.run(debug=True)
#######################################################################################
################################################################################################
################################################################################################
# import os
# from datetime import datetime
# from flask import Flask, render_template, request, redirect, url_for, flash, session
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.utils import secure_filename
# from werkzeug.security import generate_password_hash, check_password_hash
# from dotenv import load_dotenv
# import markdown
# import re

# # Load .env variables
# load_dotenv()

# app = Flask(__name__, instance_relative_config=True)

# # Ensure instance folder exists
# os.makedirs(app.instance_path, exist_ok=True)

# # Configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'blog.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.secret_key = 'secret-key'



# # Upload folder
# UPLOAD_FOLDER = os.path.join('static', 'uploads')
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# db = SQLAlchemy(app)

# # ------------------------
# # Models
# # ------------------------
# class BlogPost(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(150), nullable=False)
#     slug = db.Column(db.String(150), unique=True, nullable=False)
#     category = db.Column(db.String(100), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     image_filename = db.Column(db.String(100), nullable=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     comments = db.relationship('Comment', backref='post', lazy=True)
#     status = db.Column(db.String(20), default='Pending')

# class Comment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
#     name = db.Column(db.String(100), nullable=False)
#     message = db.Column(db.Text, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(150), unique=True, nullable=False)
#     username = db.Column(db.String(100), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)  # longer for hash
#     role = db.Column(db.String(10), nullable=False)  # 'admin' or 'user'

# # ------------------------
# # Routes
# # ------------------------
# @app.route('/')
# def index():
#     posts = BlogPost.query.filter_by(status='Approved').order_by(BlogPost.created_at.desc()).all()
#     return render_template('index.html', posts=posts)

# @app.route('/new', methods=['GET', 'POST'])
# def new_post():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#     if session.get('role') != 'user':
#         return "Only users can create posts."

#     if request.method == 'POST':
#         title = request.form['title']
#         slug = request.form['slug']
#         category = request.form['category']
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
#         flash('Your post has been submitted for review!', 'info')
#         return redirect(url_for('index'))

#     return render_template('new_post.html')

# @app.route('/post/<slug>', methods=['GET', 'POST'])
# def post_detail(slug):
#     post = BlogPost.query.filter_by(slug=slug).first_or_404()
#     if request.method == 'POST':
#         name = request.form['name']
#         message = request.form['message']
#         comment = Comment(post_id=post.id, name=name, message=message)
#         db.session.add(comment)
#         db.session.commit()
#         return redirect(url_for('post_detail', slug=slug))

#     content_html = markdown.markdown(post.content)
#     comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc()).all()
#     return render_template('post.html', post=post, content_html=content_html, comments=comments)

# @app.route('/category/<category_name>')
# def posts_by_category(category_name):
#     posts = BlogPost.query.filter_by(category=category_name).order_by(BlogPost.created_at.desc()).all()
#     return render_template('category.html', posts=posts, category=category_name)

# # Signup
# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         email = request.form['email']
#         username = request.form['username']
#         password = request.form['password']

#         if User.query.filter_by(email=email).first():
#             flash("Email already registered!", "danger")
#             return redirect(url_for('signup'))
#         if User.query.filter_by(username=username).first():
#             flash("Username already exists!", "danger")
#             return redirect(url_for('signup'))

#         hashed_password = generate_password_hash(password)
#         new_user = User(email=email, username=username, password=hashed_password, role='user')
#         db.session.add(new_user)
#         db.session.commit()
#         flash("Account created! Please login.", "success")
#         return redirect(url_for('login'))

#     return render_template('signup.html')

# # Login with Email + Password
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         user = User.query.filter_by(email=email).first()

#         if user and check_password_hash(user.password, password):
#             session['user_id'] = user.id
#             session['role'] = user.role
#             if user.role == 'admin':
#                 return redirect(url_for('admin_dashboard'))
#             else:
#                 return redirect(url_for('index'))
#         else:
#             flash("Invalid email or password!", "danger")

#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('login'))

# @app.route('/admin')
# def admin_dashboard():
#     if 'user_id' not in session or session.get('role') != 'admin':
#         return redirect(url_for('login'))
#     posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
#     return render_template('admin_dashboard.html', posts=posts)

# @app.route('/approve_post/<int:post_id>')
# def approve_post(post_id):
#     if 'user_id' not in session or session.get('role') != 'admin':
#         return redirect(url_for('login'))
#     post = BlogPost.query.get_or_404(post_id)
#     post.status = 'Approved'
#     db.session.commit()
#     return redirect(url_for('admin_dashboard'))

# @app.route('/delete_post/<int:post_id>')
# def delete_post(post_id):
#     if 'user_id' not in session or session.get('role') != 'admin':
#         return redirect(url_for('login'))
#     post = BlogPost.query.get_or_404(post_id)
#     db.session.delete(post)
#     db.session.commit()
#     return redirect(url_for('admin_dashboard'))

# @app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
# def edit_post(post_id):
#     if 'user_id' not in session or session.get('role') != 'admin':
#         return redirect(url_for('login'))
#     post = BlogPost.query.get_or_404(post_id)
#     if request.method == 'POST':
#         post.title = request.form['title']
#         post.category = request.form['category']
#         post.content = request.form['content']
#         db.session.commit()
#         return redirect(url_for('admin_dashboard'))
#     return render_template('edit_post.html', post=post)

# def generate_slug(title):
#     return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

# @app.route('/add_post', methods=['GET', 'POST'])
# def add_post():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     if request.method == 'POST':
#         title = request.form['title']
#         slug = request.form['slug']
#         category = request.form['category']
#         content = request.form['content']
#         image_file = request.files['image']
#         image_filename = None
#         if image_file and image_file.filename != '':
#             image_filename = secure_filename(image_file.filename)
#             image_path = os.path.join('static/uploads', image_filename)
#             image_file.save(image_path)

#         new_post = BlogPost(
#             title=title,
#             slug=slug,
#             category=category,
#             content=content,
#             image_filename=image_filename,
#             status='Pending'
#         )
#         db.session.add(new_post)
#         db.session.commit()
#         flash('Your post has been submitted for review!', 'info')
#         return redirect(url_for('index'))

#     return render_template('add_post.html')

# # Create DB + Secure Admin from .env
# with app.app_context():
#     db.create_all()
#     admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
#     admin_username = os.getenv("ADMIN_USERNAME", "admin")
#     admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

#     if not User.query.filter_by(email=admin_email).first():
#         hashed_admin_pass = generate_password_hash(admin_password)
#         admin = User(email=admin_email, username=admin_username, password=hashed_admin_pass, role="admin")
#         db.session.add(admin)
#         db.session.commit()

# if __name__ == '__main__':
    # app.run(debug=True)
#*********************************************************
###################################################################3
#***************************************************************



import os
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

# Ensure instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret-key'

# Upload folder
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # <-- Added
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy=True)
    status = db.Column(db.String(20), default='Pending')
    # views = db.Column(db.Integer, default=0)


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
    password = db.Column(db.String(200), nullable=False)  # longer for hash
    role = db.Column(db.String(10), nullable=False)  # 'admin' or 'user'
    posts = db.relationship('BlogPost', backref='author', lazy=True)  # <-- Added

# ------------------------
# Routes
# ------------------------
# @app.route('/')
# def index():
#     posts = BlogPost.query.filter_by(status='Approved').order_by(BlogPost.created_at.desc()).all()
#     return render_template('index.html', posts=posts)

#####################################app route with category########################3
@app.route('/')
def index():
    categories = ["Technology", "Lifestyle", "Travel", "Food", "Health"]  # ya DB se fetch karo
    posts = BlogPost.query.filter_by(status='Approved').order_by(BlogPost.created_at.desc()).all()
    return render_template('index.html', posts=posts, categories=categories)
########################################ends###########################################3

# @app.route('/new', methods=['GET', 'POST'])
# def new_post():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#     if session.get('role') != 'user':
#         return "Only users can create posts."
    
    

#     if request.method == 'POST':
#         title = request.form['title']
#         slug = request.form['slug']
#         category = request.form['category']
#         content = request.form['content']
#         image = request.files['image']

#         image_filename = None
#         if image and image.filename != '':
#             image_filename = secure_filename(image.filename)
#             image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

#         post = BlogPost(
#             user_id=session['user_id'],  # <-- Added
#             title=title,
#             slug=slug,
#             category=category,
#             content=content,
#             image_filename=image_filename
#         )
#         db.session.add(post)
#         db.session.commit()

#         # Send submission email
#         user_email = User.query.get(session['user_id']).email
#         send_post_submission_email(user_email, title)

#         flash('Your post has been submitted for review!', 'info')
#         return redirect(url_for('index'))

    # return render_template('new_post.html')



@app.route('/new', methods=['GET', 'POST'])
def new_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'user':
        return "Only users can create posts."

    # Pre-defined categories list
    categories = ["Technology", "Health", "Travel", "Food", "Education"]

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
            user_id=session['user_id'],
            title=title,
            slug=slug,
            category=category,
            content=content,
            image_filename=image_filename
        )
        db.session.add(post)
        db.session.commit()

        # Send submission email
        user_email = User.query.get(session['user_id']).email
        send_post_submission_email(user_email, title)

        flash('Your post has been submitted for review!', 'info')
        return redirect(url_for('index'))

    # Pass categories list to template
    return render_template('new_post.html', categories=categories)


@app.route('/post/<slug>', methods=['GET', 'POST'])
def post_detail(slug):
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
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

# Signup
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

# Login with Email + Password
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

    # Send approval email
    user = User.query.get(post.user_id)
    if user:
        send_post_approval_email(user.email, post.title)

    return redirect(url_for('admin_dashboard'))


@app.route('/reject_post/<int:post_id>')
def reject_post(post_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    post = BlogPost.query.get_or_404(post_id)

    # Email send to user
    user = User.query.get(post.user_id)
    if user:
        send_post_rejection_email(user.email, post.title)

    # Optional: delete or mark as rejected
    db.session.delete(post)
    db.session.commit()

    flash("Post rejected and user notified.", "info")
    return redirect(url_for('admin_dashboard'))


# @app.route('/delete_post/<int:post_id>')
# def delete_post(post_id):
#     if 'user_id' not in session or session.get('role') != 'admin':
#         return redirect(url_for('login'))
#     post = BlogPost.query.get_or_404(post_id)
#     db.session.delete(post)
#     db.session.commit()
#     return redirect(url_for('admin_dashboard'))

@app.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    post = BlogPost.query.get_or_404(post_id)

    # Email send before deleting
    user = User.query.get(post.user_id)
    if user:
        send_post_deletion_email(user.email, post.title)

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))
####################################3333

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

def generate_slug(title):
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        slug = request.form['slug']
        category = request.form['category']
        content = request.form['content']
        image_file = request.files['image']
        image_filename = None
        if image_file and image_file.filename != '':
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join('static/uploads', image_filename)
            image_file.save(image_path)

        new_post = BlogPost(
            user_id=session['user_id'],  # <-- Added
            title=title,
            slug=slug,
            category=category,
            content=content,
            image_filename=image_filename,
            status='Pending'
        )
        db.session.add(new_post)
        db.session.commit()

        # Send submission email
        user_email = User.query.get(session['user_id']).email
        send_post_submission_email(user_email, title)

        flash('Your post has been submitted for review!', 'info')
        return redirect(url_for('index'))

    return render_template('add_post.html')

# Create DB + Secure Admin from .env
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

if __name__ == '__main__':
    app.run(debug=True)
