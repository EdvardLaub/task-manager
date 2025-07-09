from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'task-manager-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://task_manager_user:changeme123@localhost/task_manager')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(20), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Task {self.title}>'

# Helper function for login requirement
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        
        # Validation
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to next page if specified
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye, {username}! You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    tasks = Task.query.filter_by(user_id=user_id).order_by(Task.created_at.desc()).all()
    
    # Calculate statistics
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.completed])
    pending_tasks = total_tasks - completed_tasks
    
    # Get recent tasks (last 10)
    recent_tasks = tasks[:10]
    
    return render_template('dashboard.html', 
                         tasks=recent_tasks,
                         total_tasks=total_tasks,
                         completed_tasks=completed_tasks,
                         pending_tasks=pending_tasks)

@app.route('/tasks')
@login_required
def tasks():
    user_id = session['user_id']
    
    # Filter options
    filter_status = request.args.get('status', 'all')
    filter_priority = request.args.get('priority', 'all')
    
    query = Task.query.filter_by(user_id=user_id)
    
    if filter_status == 'completed':
        query = query.filter_by(completed=True)
    elif filter_status == 'pending':
        query = query.filter_by(completed=False)
    
    if filter_priority != 'all':
        query = query.filter_by(priority=filter_priority)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    
    return render_template('tasks.html', 
                         tasks=tasks,
                         current_status=filter_status,
                         current_priority=filter_priority)

@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        priority = request.form['priority']
        
        if not title:
            flash('Task title is required.', 'error')
            return render_template('add_task.html')
        
        task = Task(
            title=title,
            description=description,
            priority=priority,
            user_id=session['user_id']
        )
        
        try:
            db.session.add(task)
            db.session.commit()
            flash(f'Task "{title}" added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to add task. Please try again.', 'error')
    
    return render_template('add_task.html')

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Check if task belongs to current user
    if task.user_id != session['user_id']:
        flash('Access denied. You can only edit your own tasks.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        priority = request.form['priority']
        
        if not title:
            flash('Task title is required.', 'error')
            return render_template('edit_task.html', task=task)
        
        task.title = title
        task.description = description
        task.priority = priority
        task.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash(f'Task "{title}" updated successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update task. Please try again.', 'error')
    
    return render_template('edit_task.html', task=task)

@app.route('/toggle_task/<int:task_id>', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if task.user_id != session['user_id']:
        return jsonify({'error': 'Access denied'}), 403
    
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        status = 'completed' if task.completed else 'pending'
        return jsonify({
            'success': True, 
            'completed': task.completed,
            'message': f'Task marked as {status}'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update task'}), 500

@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if task.user_id != session['user_id']:
        flash('Access denied. You can only delete your own tasks.', 'error')
        return redirect(url_for('dashboard'))
    
    title = task.title
    try:
        db.session.delete(task)
        db.session.commit()
        flash(f'Task "{title}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete task. Please try again.', 'error')
    
    return redirect(url_for('dashboard'))

# API Routes
@app.route('/api/tasks')
@login_required
def api_tasks():
    user_id = session['user_id']
    tasks = Task.query.filter_by(user_id=user_id).all()
    
    return jsonify([{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'completed': task.completed,
        'priority': task.priority,
        'created_at': task.created_at.isoformat(),
        'updated_at': task.updated_at.isoformat()
    } for task in tasks])

@app.route('/api/stats')
@login_required
def api_stats():
    user_id = session['user_id']
    tasks = Task.query.filter_by(user_id=user_id).all()
    
    total = len(tasks)
    completed = len([t for t in tasks if t.completed])
    pending = total - completed
    
    priority_counts = {
        'high': len([t for t in tasks if t.priority == 'high']),
        'medium': len([t for t in tasks if t.priority == 'medium']),
        'low': len([t for t in tasks if t.priority == 'low'])
    }
    
    return jsonify({
        'total_tasks': total,
        'completed_tasks': completed,
        'pending_tasks': pending,
        'priority_breakdown': priority_counts
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected'
    })

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Initialize database
def init_db():
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
