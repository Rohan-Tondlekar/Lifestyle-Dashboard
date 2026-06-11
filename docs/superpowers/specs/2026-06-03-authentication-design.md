# Authentication System Design

> **For agentic workers:** This spec is complete and ready for implementation planning.

**Goal:** Protect all dashboard routes with login authentication before users can access personal health data.

**Architecture:** Single-admin Flask-Login system with username/password stored in Supabase PostgreSQL. Session-based authentication expires when browser closes. All routes except `/auth/*` require `@login_required` decorator.

**Tech Stack:** Flask-Login, Werkzeug security, Flask-WTF (CSRF), SQLAlchemy ORM, Supabase PostgreSQL

---

## User Flow

```
Visitor arrives at any URL
  ↓
Not logged in? → Redirect to /auth/login
  ↓
Login page renders with form (username, password)
  ↓
User submits valid credentials
  ↓
Password verified via bcrypt hash comparison
  ↓
Session created (user stored in Flask session)
  ↓
Redirect to dashboard (or requested page)
  ↓
User can access all content
  ↓
User clicks "Logout" in navbar
  ↓
Session destroyed → Redirect to /auth/login
```

---

## Database Schema

**Table: `users`** (in Supabase PostgreSQL, `lifestyle` schema)

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(80) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Initial data (password hashed via Python before insert)
INSERT INTO users (username, password_hash) 
VALUES ('rohan', '<bcrypt-hash-of-password>');
```

**Fields:**
- `id` — Auto-increment primary key
- `username` — Unique username for login (case-sensitive)
- `password_hash` — Bcrypt hash (never store plaintext)
- `created_at` — Account creation timestamp

---

## Backend Components

### 1. User Model (`models/user.py`)

Extends SQLAlchemy + Flask-Login `UserMixin`:
- `id`, `username`, `password_hash` attributes
- `set_password(password)` method — hashes password via `generate_password_hash()`
- `check_password(password)` method — verifies via `check_password_hash()`
- Implements Flask-Login interface (`get_id()`, `is_active`, `is_authenticated`, `is_anonymous`)

### 2. Login Manager Setup (`app.py`)

In `create_app()`:
```python
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # Redirect to /auth/login if not authenticated
```

Provide `@login_manager.user_loader` callback to load user from session.

### 3. Auth Routes (`routes/auth.py`)

**POST /auth/login**
- Accept username, password from form
- Query `User` by username
- Verify password with `check_password()`
- If valid: call `login_user(user)` to create session, redirect to `/` (or next page)
- If invalid: render login page with error message

**GET /auth/logout**
- Call `logout_user()` to destroy session
- Redirect to `/auth/login`

**GET /auth/login**
- Render login form (if not already logged in, redirect to dashboard)

### 4. Route Protection

All existing blueprint routes decorated with `@login_required`:
- `dashboard_bp`, `workouts_bp`, `nutrition_bp`, `supplements_bp`, `hair_bp`, `skin_bp`, `shopping_bp`, `schedule_bp`, `myths_bp`

Unauthenticated request → automatic redirect to login page.

---

## Frontend Components

### 1. Login Page (`templates/auth/login.html`)

**Layout:**
- Centered card with Lifestyle Dashboard branding
- Username input field
- Password input field  
- Login button
- Error message display (invalid credentials)
- Matches existing dark/light theme (Tailwind CSS)

**Form:**
- POST to `/auth/login`
- CSRF token (via Flask-WTF)
- Password input type (masked)

### 2. Navbar Update (`templates/base.html`)

Add logout button in header:
- Visible only when user is logged in (`{% if current_user.is_authenticated %}`)
- Link to `GET /auth/logout`
- Positioned in top-right corner

---

## Security

**Password Security:**
- Passwords hashed with Werkzeug's `generate_password_hash()` (PBKDF2 + salt, 150,000 iterations)
- Never store plaintext
- `check_password()` safely compares hashes

**Session Security:**
- Session cookie HTTP-only (JavaScript can't access)
- Session expires when browser closes (no persistent token)
- CSRF token on login form (Flask-WTF)
- Secret key required in `.env` (Flask session encryption)

**Route Protection:**
- `@login_required` decorator on all data routes
- Attempts to access protected routes redirect to login

**Error Handling:**
- Don't reveal whether username exists (generic "Invalid credentials" message)
- Log failed login attempts (optional, for future audit trail)

---

## Environment Variables

No new env vars required. Existing variables used:
- `SECRET_KEY` — Session encryption (already in `.env`)
- `DATABASE_URL` — User table queries (already in `.env`)

---

## Testing

**Unit tests:**
- `test_user_password_hashing()` — `set_password()` and `check_password()` work correctly
- `test_login_invalid_username()` — Non-existent user denied
- `test_login_invalid_password()` — Wrong password denied
- `test_login_valid()` — Correct credentials create session
- `test_logout()` — Session destroyed after logout

**Integration tests:**
- `test_redirect_to_login_when_not_authenticated()` — Visiting `/` redirects to `/auth/login`
- `test_dashboard_accessible_after_login()` — Can access `/` after login
- `test_logout_redirects_to_login()` — `/auth/logout` redirects and clears session
- `test_csrf_protection_on_login()` — Missing CSRF token rejected

**Manual verification:**
- Open app in fresh browser → redirected to login
- Login with valid credentials → session created, dashboard visible
- Logout → redirected to login
- Browser restart → no persistent session (expires)

---

## Deployment Notes

**Supabase:**
- Create `users` table and insert admin user before deploying
- Password hashed locally in Python, then inserted via psycopg3

**Railway:**
- No config changes needed (uses DATABASE_URL and SECRET_KEY from env)
- Auto-redeploy on git push works as before

**Local Development:**
- SQLite `dev.db` can have a test user added manually
- Or use `flask shell` to create user: `User.set_password()` and `db.session.add()`

---

## Future Extensions

These are NOT included in this spec, but possible enhancements:
- Password reset via email
- Multiple user accounts (remove "single admin" constraint)
- User activity audit log
- Two-factor authentication
- Session timeout (e.g., logout after 30 min inactivity)

---

## Success Criteria

✓ Visiting any URL redirects to login if not authenticated  
✓ Valid username/password creates session  
✓ Session persists across page navigation  
✓ Session expires when browser closes  
✓ Logout destroys session  
✓ All existing data routes are protected  
✓ Login page matches app theme (dark/light toggle)  
✓ No password stored in plaintext  
✓ CSRF protection on login form  
✓ All tests pass  
