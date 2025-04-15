from datetime import datetime
from flask_login import UserMixin
import uuid

# In-memory database for users
users_db = {}
# In-memory database for resources
resources_db = {}
# In-memory database for resource requests
resource_requests_db = {}

class User(UserMixin):
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.shared_resources = []
        self.resource_requests = []
        self.allocated_resources = []
        self.created_at = datetime.now()
        self.last_login = datetime.now()
        
    def get_id(self):
        return str(self.id)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'shared_resources': self.shared_resources,
            'resource_requests': self.resource_requests,
            'allocated_resources': self.allocated_resources,
            'created_at': self.created_at,
            'last_login': self.last_login
        }
        
class Resource:
    def __init__(self, id, user_id, resource_type, amount, availability=True):
        self.id = id
        self.user_id = user_id
        self.resource_type = resource_type  # CPU, Memory, Storage
        self.amount = amount  # CPU cores, GB of RAM/storage
        self.availability = availability
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.allocated_to = None
        self.allocation_time = None
        
    def allocate(self, user_id):
        self.availability = False
        self.allocated_to = user_id
        self.allocation_time = datetime.now()
        self.updated_at = datetime.now()
        
    def deallocate(self):
        self.availability = True
        self.allocated_to = None
        self.allocation_time = None
        self.updated_at = datetime.now()
        
    def update(self, resource_type=None, amount=None, availability=None):
        if resource_type:
            self.resource_type = resource_type
        if amount:
            self.amount = amount
        if availability is not None:
            self.availability = availability
        self.updated_at = datetime.now()
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resource_type': self.resource_type,
            'amount': self.amount,
            'availability': self.availability,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'allocated_to': self.allocated_to,
            'allocation_time': self.allocation_time
        }
        
class ResourceRequest:
    def __init__(self, id, user_id, resource_type, amount, duration=None, status="pending"):
        self.id = id
        self.user_id = user_id
        self.resource_type = resource_type
        self.amount = amount
        self.duration = duration  # Duration in hours, None for indefinite
        self.status = status  # pending, approved, rejected, completed
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.approved_at = None
        self.completed_at = None
        self.allocated_resource_id = None
        
    def approve(self, resource_id):
        self.status = "approved"
        self.approved_at = datetime.now()
        self.updated_at = datetime.now()
        self.allocated_resource_id = resource_id
        
    def reject(self):
        self.status = "rejected"
        self.updated_at = datetime.now()
        
    def complete(self):
        self.status = "completed"
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resource_type': self.resource_type,
            'amount': self.amount,
            'duration': self.duration,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'approved_at': self.approved_at,
            'completed_at': self.completed_at,
            'allocated_resource_id': self.allocated_resource_id
        }
        
# Sample user for testing (you can remove this in production)
test_user = User(
    id=1,
    username="testuser",
    email="test@example.com",
    password_hash="$2b$12$WRpx0d1eXZ9MYgP9jLFE0eXHcn1ULzZh.xs6XKSFtGdwH3aQeAUX2"  # Password: testpassword
)
users_db[1] = test_user
