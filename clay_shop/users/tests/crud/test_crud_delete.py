import pytest

from users.services.user_crud import CrudUser


@pytest.mark.django_db
class TestCrudUserDelete:
    def test_delete_user_success(self, sample_user):
        user_id = sample_user.id
        result = CrudUser.delete_user(user_id)

        assert result is True
        assert CrudUser.get_user_by_id(user_id) is None

    def test_delete_user_not_exists(self):
        result = CrudUser.delete_user(99999)
        assert result is False
