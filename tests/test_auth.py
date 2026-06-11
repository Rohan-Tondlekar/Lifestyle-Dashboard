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

        assert user.password_hash != 'mypassword'
        assert user.check_password('mypassword')
        assert not user.check_password('wrongpassword')

    def test_user_authentication_properties(self, user):
        assert user.is_authenticated is True
        assert user.is_active is True
        assert user.is_anonymous is False


class TestLoginRoute:
    def test_login_page_loads(self, client):
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Sign In' in response.data or b'username' in response.data.lower()

    def test_login_with_invalid_credentials(self, client):
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'anypassword'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Invalid' in response.data or b'invalid' in response.data.lower()

    def test_login_with_valid_credentials(self, client, user):
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)

        assert response.status_code == 200


class TestLogoutRoute:
    def test_logout_requires_login(self, client):
        response = client.get('/auth/logout', follow_redirects=False)
        assert response.status_code == 302


class TestRouteProtection:
    def test_dashboard_redirects_to_login_when_not_authenticated(self, client):
        response = client.get('/', follow_redirects=False)
        assert response.status_code == 302
        assert 'login' in response.location.lower()

    def test_workouts_requires_login(self, client):
        response = client.get('/workouts/', follow_redirects=False)
        assert response.status_code == 302
        assert 'login' in response.location.lower()

    def test_nutrition_requires_login(self, client):
        response = client.get('/nutrition/', follow_redirects=False)
        assert response.status_code == 302
        assert 'login' in response.location.lower()
