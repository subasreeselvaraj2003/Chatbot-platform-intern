from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai

# Configure Gemini API with your key
genai.configure(api_key="AIzaSyCbKYyxpAOwgtyzOi-SrIFfuPmSyGi3MNw")  # <-- Replace with your key

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# -------------------- Models --------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    projects = db.relationship('Project', backref='user', lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    prompts = db.relationship('Prompt', backref='project', lazy=True)

class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(250), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

# -------------------- Flask-Login --------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------- Routes --------------------
@app.route('/')
def home():
    return 'Welcome to Yellow.ai Chatbot! <a href="/signup">Sign Up</a> | <a href="/login">Login</a>'

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return '''
    <form method="POST">
        Email: <input name="email" type="email">
        Password: <input name="password" type="password">
        <input type="submit" value="Sign Up">
    </form>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        return 'Invalid credentials'
    return '''
    <form method="POST">
        Email: <input name="email" type="email">
        Password: <input name="password" type="password">
        <input type="submit" value="Login">
    </form>
    '''

@app.route('/dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user.email}! <a href="/logout">Logout</a> <br> <a href="/projects">Your Projects</a>'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/projects')
@login_required
def projects():
    user_projects = Project.query.filter_by(user_id=current_user.id).all()
    project_list = "<ul>"
    for p in user_projects:
        project_list += f"<li><a href='/chat/{p.id}'>{p.name} (Chat)</a></li>"
    project_list += "</ul>"
    project_list += '''
    <form method="POST" action="/create_project">
        New Project Name: <input name="name">
        <input type="submit" value="Create Project">
    </form>
    <a href='/dashboard'>Back to Dashboard</a>
    '''
    return project_list

@app.route('/create_project', methods=['POST'])
@login_required
def create_project():
    name = request.form['name']
    new_project = Project(name=name, user_id=current_user.id)
    db.session.add(new_project)
    db.session.commit()
    return redirect(url_for('projects'))

@app.route('/project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    prompts = Prompt.query.filter_by(project_id=project.id).all()
    if request.method == 'POST':
        new_prompt = Prompt(text=request.form['prompt'], project_id=project.id)
        db.session.add(new_prompt)
        db.session.commit()
        return redirect(url_for('view_project', project_id=project.id))
    prompt_list = "<ul>"
    for pr in prompts:
        prompt_list += f"<li>{pr.text}</li>"
    prompt_list += "</ul>"
    prompt_list += '''
    <form method="POST">
        New Prompt: <input name="prompt">
        <input type="submit" value="Add Prompt">
    </form>
    <a href='/projects'>Back to Projects</a>
    '''
    return f"<h2>Project: {project.name}</h2>" + prompt_list

# ----------- Gemini Chat Route -----------
@app.route('/chat/<int:project_id>', methods=['GET', 'POST'])
@login_required
def chat(project_id):
    project = Project.query.get_or_404(project_id)
    answer = ""
    if request.method == 'POST':
        user_input = request.form['prompt']
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")  # <-- Use a Gemini model
            response = model.generate_content(user_input)
            answer = response.text if hasattr(response, "text") else str(response)
        except Exception as e:
            answer = f"Error: {str(e)}"
    return f'''
    <h2>Chat with Project: {project.name}</h2>
    <form method="POST">
        Your Prompt: <input name="prompt">
        <input type="submit" value="Send">
    </form>
    <p><b>AI Response:</b> {answer}</p>
    <a href="/projects">Back to Projects</a>
    '''

# -------------------- Run App --------------------
if __name__ == '__main__':
    import os
    with app.app_context():
        db.create_all()
        port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port,debug=True)

