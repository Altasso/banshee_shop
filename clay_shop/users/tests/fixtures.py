import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "TestPassword123!",
        "role": "customer",
    }


@pytest.fixture
def create_user(db):
    def _create_user(**kwargs):
        defaults = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "TestPassword123!",
            "role": "customer",
        }
        defaults.update(kwargs)
        password = defaults.pop("password", "TestPassword123!")
        user = User.objects.create_user(**defaults)
        user.set_password(password)
        user.save()
        return user
    return _create_user

@pytest.fixture
def sample_user(create_user):
    return create_user(
        username='sampleuser',
        email='sample@example.com',
        first_name='Sample',
        last_name='User'
    )

@pytest.fixture
def multiple_user(create_user):
    users = []
    for i in range(5):
        user = create_user(
            username=f'user{i}',
            email=f'user{i}',
            first_name=f'First{i}',
            last_name=f'Last{i}',
        )
        users.append(user)
    return users
