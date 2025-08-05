from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 🔌 Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 🔧 Initialize database
db = SQLAlchemy(app)

# 📦 BlogPost model
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    image = db.Column(db.String(200), nullable=False)
    para1 = db.Column(db.Text, nullable=False)
    para2 = db.Column(db.Text, nullable=False)

# 🧱 Create tables (if not exist)
with app.app_context():
    db.create_all()

# 🏠 Home page route
@app.route('/')
def home():
    posts = BlogPost.query.all()
    return render_template('home.html', posts=posts)

# 📄 Slug detail page
@app.route('/post/<slug>')
def post(slug):
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    return render_template('post.html', post=post)

# ➕ Add new post (form page)
@app.route('/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        slug = request.form['slug']
        image = request.form['image']
        para1 = request.form['para1']
        para2 = request.form['para2']

        new_post = BlogPost(
            title=title,
            slug=slug,
            image=image,
            para1=para1,
            para2=para2
        )
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('new_post.html')

# 🚀 Run the app
if __name__ == '__main__':
    app.run(debug=True)


