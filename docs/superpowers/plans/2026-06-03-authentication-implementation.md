# Authentication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Flask-Login authentication so all dashboard routes require username/password login before access.

**Architecture:** Single-admin system with User model in Supabase PostgreSQL. LoginManager handles session management, route protection via `@login_required` decorator, session expires when browser closes.

**Tech Stack:** Flask-Login, Flask-WTF, Werkzeug security (password hashing), SQLAlchemy ORM

---

## File Structure

**New files:**
- `models/user.py` — User SQLAlchemy model with Flask-Login UserMixin
- `routes/auth.py` — Login (GET/POST), logout routes
- `templates/auth/login.html` — Login form page
- `tests/test_auth.py` — Authentication unit and integration tests

**Modified files:**
- `app.py` — Initialize LoginManager
- `config.py` — Configure session settings
- `templates/base.html` — Add logout button in navbar
- `requirements.txt` — Add Flask-Login, Flask-WTF
- `models/__init__.py` — Import User model
- All route blueprints — Add `@login_required` decorator

**Supabase:**
- Create `users` table
- Insert admin user

---

## Task 1: Add Dependencies

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: View current requirements**

```bash
cd "d:\My Drive\Project\Lifestyle Dashboard"
cat requirements.txt
```

- [ ] **Step 2: Add Flask-Login and Flask-WTF**

Open `requirements.txt` and add these lines (find Flask line and add after it):
```
Flask-Login==0.6.3
Flask-WTF==1.2.1
```

- [ ] **Step 3: Install new packages**

```bash
pip install -r requirements.txt
```

Expected: Both packages install successfully.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "deps: add Flask-Login and Flask-WTF for authentication"
```

---

## Task 2: Create User Model

**Files:**
- Create: `models/user.py`

- [ ] **Step 1: Create user.py with User model**

Create file `models/user.py`:

```python
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from models import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def set_password(self, password: str) -> None:
        """Hash and store password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """Return user ID as string for Flask-Login."""
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __repr__(self):
        return f'<User {self.username}>'
```

- [ ] **Step 2: Verify file was created**

```bash
cat "models/user.py" | head -20
```

Expected: File contains User class with set_password and check_password methods.

- [ ] **Step 3: Commit**

```bash
git add models/user.py
git commit -m "feat: create User model with Flask-Login integration"
```

---

## Task 3: Update Models __init__.py to Export User

**Files:**
- Modify: `models/__init__.py`

- [ ] **Step 1: View current models/__init__.py**

```bash
cat "models/__init__.py"
```

- [ ] **Step 2: Add User import**

Open `models/__init__.py` and update it to:

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models to register them with metadata
from models.user import User  # noqa: F401
from models.body import BodyLog  # noqa: F401
from models.nutrition import MealLog  # noqa: F401
from models.workout import WorkoutLog  # noqa: F401
```

- [ ] **Step 3: Verify import works**

```bash
python -c "from models import User, db; print('User model imported successfully')"
```

Expected: "User model imported successfully"

- [ ] **Step 4: Commit**

```bash
git add models/__init__.py
git commit -m "feat: export User model from models package"
```

---

## Task 4: Configure Session Settings in config.py

**Files:**
- Modify: `config.py`

- [ ] **Step 1: View current config.py**

```bash
cat config.py
```

- [ ] **Step 2: Add session configuration**

Add these lines to the `Config` class in `config.py`:

```python
# Session configuration
SESSION_COOKIE_SECURE = True  # Only send over HTTPS in production
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
PERMANENT_SESSION_LIFETIME = 0  # Session expires when browser closes (in seconds; 0 = until close)
```

Full config should look like (add to existing Config class):

```python
import os
from datetime import timedelta

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///dev.db'
    ).replace('postgres://', 'postgresql://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Session configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 0  # Expires when browser closes
    WTF_CSRF_TIME_LIMIT = None  # No time limit on CSRF tokens
```

- [ ] **Step 3: Verify config is valid Python**

```bash
python -c "from config import Config; print('Config loaded successfully')"
```

Expected: "Config loaded successfully"

- [ ] **Step 4: Commit**

```bash
git add config.py
git commit -m "conf: configure Flask session security settings"
```

---

## Task 5: Initialize LoginManager in app.py

**Files:**
- Modify: `app.py`

- [ ] **Step 1: View current app.py**

```bash
cat app.py
```

- [ ] **Step 2: Update app.py to initialize LoginManager**

Replace the entire `app.py` with:

```python
from flask import Flask
from flask_login import LoginManager

from config import Config
from models import db, User


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config:
        app.config.update(config)

    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirect to login page if not authenticated
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID from database."""
        return User.query.get(int(user_id))

    from models import body, nutrition, workout  # noqa: F401 — registers tables with metadata

    with app.app_context():
        db.create_all()

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.hair import hair_bp
    from routes.myths import myths_bp
    from routes.nutrition import nutrition_bp
    from routes.schedule import schedule_bp
    from routes.shopping import shopping_bp
    from routes.skin import skin_bp
    from routes.supplements import supplements_bp
    from routes.workouts import workouts_bp

    # Register auth blueprint FIRST (before protected routes)
    app.register_blueprint(auth_bp)
    
    # Register all other blueprints (will be protected by @login_required)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(workouts_bp)
    app.register_blueprint(nutrition_bp)
    app.register_blueprint(supplements_bp)
    app.register_blueprint(hair_bp)
    app.register_blueprint(skin_bp)
    app.register_blueprint(shopping_bp)
    app.register_blueprint(myths_bp)

    return app
```

- [ ] **Step 3: Verify app.py syntax**

```bash
python -c "from app import create_app; app = create_app(); print('App created successfully')"
```

Expected: "App created successfully"

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: initialize Flask-Login and configure user_loader"
```

---

## Task 6: Create Auth Routes

**Files:**
- Create: `routes/auth.py`

- [ ] **Step 1: Create auth.py with login/logout routes**

Create file `routes/auth.py`:

```python
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and form handler."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required.', 'error')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash('Invalid username or password.', 'error')
            return redirect(url_for('auth.login'))

        login_user(user)
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('dashboard.index'))

    return render_template('auth/login.html')


@auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    """Logout and destroy session."""
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
```

- [ ] **Step 2: Verify file was created**

```bash
cat routes/auth.py | head -30
```

Expected: File contains login and logout route handlers.

- [ ] **Step 3: Commit**

```bash
git add routes/auth.py
git commit -m "feat: create auth routes (login, logout)"
```

---

## Task 7: Create Login Template

**Files:**
- Create: `templates/auth/login.html`

- [ ] **Step 1: Create auth directory**

```bash
mkdir -p "templates/auth"
```

- [ ] **Step 2: Create login.html template**

Create file `templates/auth/login.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login — Lifestyle Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        // Dark mode toggle
        if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    </script>
</head>
<body class="bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 transition-colors">

<div class="min-h-screen flex items-center justify-center px-4">
    <div class="w-full max-w-md">
        <!-- Branding -->
        <div class="text-center mb-8">
            <h1 class="text-3xl font-bold text-indigo-600 dark:text-blue-400 mb-2">
                Lifestyle Dashboard
            </h1>
            <p class="text-sm text-slate-500 dark:text-slate-400">
                Personal health & fitness tracking
            </p>
        </div>

        <!-- Login Card -->
        <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700 shadow-sm p-8">
            <h2 class="text-xl font-bold text-slate-900 dark:text-slate-100 mb-6">Sign In</h2>

            <!-- Error Messages -->
            {% with messages = get_flashed_messages(category_filter=['error']) %}
                {% if messages %}
                    {% for message in messages %}
                    <div class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-700 dark:text-red-300">
                        {{ message }}
                    </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <!-- Info Messages -->
            {% with messages = get_flashed_messages(category_filter=['info']) %}
                {% if messages %}
                    {% for message in messages %}
                    <div class="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg text-sm text-blue-700 dark:text-blue-300">
                        {{ message }}
                    </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <!-- Login Form -->
            <form method="POST" class="space-y-4">
                <!-- Username -->
                <div>
                    <label for="username" class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                        Username
                    </label>
                    <input
                        type="text"
                        id="username"
                        name="username"
                        required
                        autofocus
                        class="w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-blue-500 transition-colors"
                        placeholder="Enter your username"
                    />
                </div>

                <!-- Password -->
                <div>
                    <label for="password" class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                        Password
                    </label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        required
                        class="w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-blue-500 transition-colors"
                        placeholder="Enter your password"
                    />
                </div>

                <!-- Login Button -->
                <button
                    type="submit"
                    class="w-full mt-6 px-4 py-2.5 bg-indigo-500 dark:bg-blue-600 text-white font-semibold rounded-lg hover:bg-indigo-600 dark:hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-blue-500"
                >
                    Sign In
                </button>
            </form>

            <!-- Footer -->
            <p class="text-xs text-center text-slate-500 dark:text-slate-400 mt-6">
                Personal data is protected. Login required.
            </p>
        </div>
    </div>
</div>

</body>
</html>
```

- [ ] **Step 3: Verify file was created**

```bash
cat "templates/auth/login.html" | head -20
```

Expected: File contains HTML login form with username and password fields.

- [ ] **Step 4: Commit**

```bash
git add templates/auth/login.html
git commit -m "feat: create login page template with dark/light theme support"
```

---

## Task 8: Update Base Template with Logout Button

**Files:**
- Modify: `templates/base.html`

- [ ] **Step 1: View current base.html**

```bash
cat "templates/base.html" | head -50
```

- [ ] **Step 2: Find the navbar section and add logout button**

In `templates/base.html`, find the navbar/header section (usually near the top of the body). Look for something like:

```html
<nav> ... </nav>
```

or a header div. Add this logout button on the right side of the navbar. Find the line with your theme toggle or header content and add this after it (adjust positioning as needed):

```html
{% if current_user.is_authenticated %}
<a href="{{ url_for('auth.logout') }}" 
   class="text-sm px-3 py-1.5 rounded-lg bg-red-500 hover:bg-red-600 text-white transition-colors">
    Logout
</a>
{% endif %}
```

The exact position depends on your current navbar structure. It should be placed in the header area, typically on the right side.

Example: If your navbar looks like this:
```html
<header>
  <h1>Dashboard</h1>
  <button id="theme-toggle">Theme</button>
</header>
```

Update it to:
```html
<header>
  <h1>Dashboard</h1>
  <div class="flex gap-2">
    <button id="theme-toggle">Theme</button>
    {% if current_user.is_authenticated %}
    <a href="{{ url_for('auth.logout') }}" 
       class="text-sm px-3 py-1.5 rounded-lg bg-red-500 hover:bg-red-600 text-white transition-colors">
        Logout
    </a>
    {% endif %}
  </div>
</header>
```

- [ ] **Step 3: Verify the change**

```bash
grep -n "auth.logout" "templates/base.html"
```

Expected: Line number showing logout link was added.

- [ ] **Step 4: Commit**

```bash
git add templates/base.html
git commit -m "feat: add logout button to navbar (visible when logged in)"
```

---

## Task 9: Protect All Routes with @login_required

**Files:**
- Modify: `routes/dashboard.py`, `routes/workouts.py`, `routes/nutrition.py`, `routes/supplements.py`, `routes/hair.py`, `routes/skin.py`, `routes/shopping.py`, `routes/schedule.py`, `routes/myths.py`

- [ ] **Step 1: Update dashboard.py**

Add this import at the top:
```python
from flask_login import login_required
```

Then add `@login_required` decorator to every route. Example:

```python
@dashboard_bp.route('/')
@login_required  # Add this line
def index():
    ...
```

Full example for dashboard.py:

```python
from flask import Blueprint, render_template
from flask_login import login_required

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/')

@dashboard_bp.route('/')
@login_required
def index():
    # ... existing code ...
```

- [ ] **Step 2: Update workouts.py**

Add import and `@login_required` to all routes in `routes/workouts.py`:

```python
from flask_login import login_required

# Then for each route:
@workouts_bp.route('/')
@login_required
def plan():
    ...

@workouts_bp.route('/log', methods=['POST'])
@login_required
def log_set():
    ...

# ... etc for all routes
```

- [ ] **Step 3: Update nutrition.py**

Same pattern — add import and `@login_required` to all routes.

- [ ] **Step 4: Update supplements.py**

Same pattern — add import and `@login_required` to all routes.

- [ ] **Step 5: Update hair.py**

Same pattern — add import and `@login_required` to all routes.

- [ ] **Step 6: Update skin.py**

Same pattern — add import and `@login_required` to all routes.

- [ ] **Step 7: Update shopping.py**

Same pattern — add import and `@login_required` to all routes.

- [ ] **Step 8: Update schedule.py**

Same pattern — add import and `@login_required` to all routes.

- [ ] **Step 9: Update myths.py**

Same pattern — add import and `@login_required` to all routes.

- [ ] **Step 10: Verify all files have the import and decorator**

```bash
grep -r "from flask_login import login_required" routes/
```

Expected: All route files listed.

```bash
grep -r "@login_required" routes/
```

Expected: Multiple @login_required decorators shown.

- [ ] **Step 11: Commit**

```bash
git add routes/
git commit -m "feat: protect all routes with @login_required decorator"
```

---

## Task 10: Create Supabase User Table

**Files:**
- Database: Supabase

- [ ] **Step 1: Open Supabase dashboard**

Go to https://app.supabase.com and log in.

- [ ] **Step 2: Navigate to SQL Editor**

In your Supabase project, click **SQL Editor** on the left sidebar.

- [ ] **Step 3: Create users table**

Click **+ New Query** and paste this SQL:

```sql
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(80) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
```

Click **Run** to execute.

Expected: "Success. No rows returned" message.

- [ ] **Step 4: Verify table was created**

In Supabase, click **Table Editor** on the left. You should see the `users` table listed.

- [ ] **Step 5: Note the schema**

The table is in the default schema (usually `public`). If your DATABASE_URL uses `DB_SCHEMA=lifestyle`, you may need to create the table in that schema instead:

```sql
CREATE SCHEMA IF NOT EXISTS lifestyle;

CREATE TABLE IF NOT EXISTS lifestyle.users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(80) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

Verify which schema your app uses by checking `.env` for `DB_SCHEMA` or looking at SQLAlchemy models to see `__table_args__ = {'schema': 'lifestyle'}`.

---

## Task 11: Insert Initial Admin User

**Files:**
- Database: Supabase

- [ ] **Step 1: Generate password hash locally**

In a Python terminal (in your project's venv):

```python
from werkzeug.security import generate_password_hash
password_hash = generate_password_hash('your-secure-password-here')
print(password_hash)
```

Copy the output hash.

- [ ] **Step 2: Insert user into Supabase**

Go to Supabase SQL Editor and run:

```sql
INSERT INTO users (username, password_hash) 
VALUES ('rohan', '<paste-the-hash-from-step-1>');
```

Replace `<paste-the-hash-from-step-1>` with the actual hash from Step 1.

Expected: "1 row inserted" message.

- [ ] **Step 3: Verify user was inserted**

Click **Table Editor**, then the `users` table. You should see one row with username 'rohan'.

---

## Task 12: Write Authentication Tests

**Files:**
- Create: `tests/test_auth.py`

- [ ] **Step 1: Create test_auth.py**

Create file `tests/test_auth.py`:

```python
import pytest
from werkzeug.security import generate_password_hash

from models import User, db


@pytest.fixture
def user(app):
    """Create a test user."""
    user = User(username='testuser')
    user.set_password('testpass123')
    db.session.add(user)
    db.session.commit()
    return user


class TestUserModel:
    def test_user_password_hashing(self):
        user = User(username='hashtest')
        user.set_password('mypassword')
        
        assert user.password_hash != 'mypassword'  # Hash is not plaintext
        assert user.check_password('mypassword')  # Correct password matches
        assert not user.check_password('wrongpassword')  # Wrong password doesn't match

    def test_user_get_id(self, user):
        user.id = 42
        assert user.get_id() == '42'

    def test_user_authentication_properties(self, user):
        assert user.is_authenticated is True
        assert user.is_active is True
        assert user.is_anonymous is False


class TestLoginRoute:
    def test_login_page_loads(self, client):
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Sign In' in response.data or b'Username' in response.data

    def test_login_with_invalid_username(self, client):
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'anypassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_login_with_invalid_password(self, client, user):
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_login_with_valid_credentials(self, client, user):
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to dashboard

    def test_login_missing_username(self, client):
        response = client.post('/auth/login', data={
            'username': '',
            'password': 'password'
        }, follow_redirects=True)
        
        assert b'required' in response.data.lower()

    def test_login_missing_password(self, client):
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': ''
        }, follow_redirects=True)
        
        assert b'required' in response.data.lower()


class TestLogoutRoute:
    def test_logout_redirects_to_login(self, client, user):
        # First log in
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Then log out
        response = client.get('/auth/logout', follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to login page

    def test_logout_without_login(self, client):
        # Trying to access logout without being logged in should redirect to login
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200


class TestRouteProtection:
    def test_dashboard_redirects_to_login_when_not_authenticated(self, client):
        response = client.get('/', follow_redirects=False)
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_dashboard_accessible_after_login(self, client, user):
        # Log in first
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Now dashboard should be accessible
        response = client.get('/')
        assert response.status_code == 200

    def test_workouts_requires_login(self, client):
        response = client.get('/workouts/', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_nutrition_requires_login(self, client):
        response = client.get('/nutrition/', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.location
```

- [ ] **Step 2: Run tests to ensure they fail first (TDD)**

```bash
pytest tests/test_auth.py -v
```

Expected: Most tests fail because authentication isn't fully wired up yet. This is correct for TDD.

- [ ] **Step 3: Commit test file**

```bash
git add tests/test_auth.py
git commit -m "test: add authentication unit and integration tests"
```

---

## Task 13: Run All Tests

**Files:**
- None (just running existing tests)

- [ ] **Step 1: Run all pytest tests**

```bash
pytest tests/ -v
```

Expected: All tests pass, including the new auth tests and existing tests.

- [ ] **Step 2: If any tests fail, debug**

If a test fails, read the error message and fix the code. Common issues:
- User model not imported correctly → check `models/__init__.py`
- LoginManager not initialized → check `app.py`
- @login_required not applied → check route files
- User table not created → check Supabase

- [ ] **Step 3: Commit once all tests pass**

```bash
git add .
git commit -m "test: all authentication tests passing"
```

---

## Task 14: Manual Testing - Local

**Files:**
- None

- [ ] **Step 1: Start local development server**

```bash
flask --app app:create_app run --debug
```

Expected: Server running on http://127.0.0.1:5000

- [ ] **Step 2: Visit dashboard**

Open http://127.0.0.1:5000 in your browser.

Expected: Redirected to http://127.0.0.1:5000/auth/login

- [ ] **Step 3: Try logging in with wrong credentials**

On login page:
- Username: `testuser` (or any wrong username)
- Password: `wrongpass`

Click "Sign In".

Expected: Error message "Invalid username or password"

- [ ] **Step 4: Try logging in with correct credentials**

- Username: `rohan`
- Password: (the password you set in Task 11)

Click "Sign In".

Expected: Redirected to dashboard. Can now see all content.

- [ ] **Step 5: Verify logout button is visible**

In the navbar, you should see a red "Logout" button.

Click it.

Expected: Redirected to login page. Session is destroyed.

- [ ] **Step 6: Verify session expires on browser close**

Close the browser completely (or clear all cookies).

Open a new browser tab to http://127.0.0.1:5000

Expected: Redirected to login page (session cookie is gone).

- [ ] **Step 7: Test dark/light theme on login page**

On login page, toggle the theme (if there's a toggle).

Expected: Login form switches between dark and light colors.

---

## Task 15: Push to Production

**Files:**
- None (git push deploys via Railway)

- [ ] **Step 1: Verify all commits are made**

```bash
git status
```

Expected: "working tree clean"

- [ ] **Step 2: View recent commits**

```bash
git log --oneline | head -10
```

Expected: See all auth-related commits.

- [ ] **Step 3: Push to remote (triggers Railway auto-deploy)**

```bash
git push origin main
```

Expected: Commits are pushed to GitHub. Railway automatically deploys.

- [ ] **Step 4: Monitor Railway deployment**

Go to https://railway.app, open your project, and watch the deployment.

Expected: Deployment completes in 1-2 minutes. Green checkmark appears.

- [ ] **Step 5: Test live app**

Open https://lifestyle-dashboard.up.railway.app/ (or your Railway URL).

Expected: Redirected to login page.

- [ ] **Step 6: Log in on production**

- Username: `rohan`
- Password: (same as you set)

Expected: Successfully log in and see dashboard on production.

---

## Summary

After completing all tasks:
✓ User model created with password hashing  
✓ Flask-Login initialized with session management  
✓ Login/logout routes working  
✓ Beautiful login page with dark/light theme  
✓ All routes protected with @login_required  
✓ User table created in Supabase  
✓ Admin user inserted  
✓ All tests passing (unit + integration)  
✓ Manual testing complete (local + production)  
✓ Deployed to Railway  

Your Lifestyle Dashboard now requires authentication before accessing any personal data.
