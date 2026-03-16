import unittest
import json
from app import create_app
from models import db, User, Company

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test company
        self.company = Company(
            name="Test Company",
            company_type="vendor",
            contact_email="test@company.com"
        )
        db.session.add(self.company)
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_health_check(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_register_success(self):
        response = self.client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'field_contractor',
            'company_id': self.company.id
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['username'], 'newuser')
    
    def test_register_duplicate_username(self):
        # Create first user
        self.client.post('/api/auth/register', json={
            'username': 'duplicate',
            'email': 'first@test.com',
            'password': 'password123',
            'first_name': 'First',
            'last_name': 'User',
            'role': 'field_contractor'
        })
        
        # Try to create second with same username
        response = self.client.post('/api/auth/register', json={
            'username': 'duplicate',
            'email': 'second@test.com',
            'password': 'password123',
            'first_name': 'Second',
            'last_name': 'User',
            'role': 'field_contractor'
        })
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_register_duplicate_email(self):
        # Create first user
        self.client.post('/api/auth/register', json={
            'username': 'user1',
            'email': 'same@test.com',
            'password': 'password123',
            'first_name': 'First',
            'last_name': 'User',
            'role': 'field_contractor'
        })
        
        # Try to create second with same email
        response = self.client.post('/api/auth/register', json={
            'username': 'user2',
            'email': 'same@test.com',
            'password': 'password123',
            'first_name': 'Second',
            'last_name': 'User',
            'role': 'field_contractor'
        })
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_register_invalid_email(self):
        response = self.client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'not-an-email',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'field_contractor'
        })
        self.assertEqual(response.status_code, 400)
    
    def test_register_missing_fields(self):
        response = self.client.post('/api/auth/register', json={
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 400)
    
    def test_login_success(self):
        # First register a user
        self.client.post('/api/auth/register', json={
            'username': 'loginuser',
            'email': 'login@test.com',
            'password': 'password123',
            'first_name': 'Login',
            'last_name': 'User',
            'role': 'field_contractor'
        })
        
        # Then login
        response = self.client.post('/api/auth/login', json={
            'username': 'loginuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)
        self.assertIn('user', data)
    
    def test_login_invalid_password(self):
        # Register user
        self.client.post('/api/auth/register', json={
            'username': 'loginfail',
            'email': 'loginfail@test.com',
            'password': 'password123',
            'first_name': 'Login',
            'last_name': 'Fail',
            'role': 'field_contractor'
        })
        
        # Try wrong password
        response = self.client.post('/api/auth/login', json={
            'username': 'loginfail',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)
    
    def test_login_nonexistent_user(self):
        response = self.client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 401)
    
    def test_refresh_token(self):
        # Register and login
        self.client.post('/api/auth/register', json={
            'username': 'refreshuser',
            'email': 'refresh@test.com',
            'password': 'password123',
            'first_name': 'Refresh',
            'last_name': 'User',
            'role': 'field_contractor'
        })
        
        login_response = self.client.post('/api/auth/login', json={
            'username': 'refreshuser',
            'password': 'password123'
        })
        refresh_token = json.loads(login_response.data)['refresh_token']
        
        # Use refresh token
        response = self.client.post('/api/auth/refresh', 
            headers={'Authorization': f'Bearer {refresh_token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
    
    def test_get_current_user(self):
        # Register and login
        self.client.post('/api/auth/register', json={
            'username': 'meuser',
            'email': 'me@test.com',
            'password': 'password123',
            'first_name': 'Current',
            'last_name': 'User',
            'role': 'field_contractor',
            'company_id': self.company.id
        })
        
        login_response = self.client.post('/api/auth/login', json={
            'username': 'meuser',
            'password': 'password123'
        })
        access_token = json.loads(login_response.data)['access_token']
        
        # Get current user
        response = self.client.get('/api/auth/me',
            headers={'Authorization': f'Bearer {access_token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'meuser')
        self.assertEqual(data['first_name'], 'Current')
        self.assertEqual(data['last_name'], 'User')
        self.assertEqual(data['role'], 'field_contractor')
        self.assertEqual(data['company_id'], self.company.id)

if __name__ == '__main__':
    unittest.main()