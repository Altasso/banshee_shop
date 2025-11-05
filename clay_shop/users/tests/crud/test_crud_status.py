import pytest

from users.services.user_crud import CrudUser


@pytest.mark.django_db
class TestCrudUserActivation:
    def test_activate_user_success(self, sample_user):
        sample_user.is_active = False
        sample_user.save()

        activated_user = CrudUser.activate_user(sample_user.id)

        assert activated_user is not None
        assert activated_user.is_active is True

    def test_active_user_not_exists(self):
        result = CrudUser.activate_user(99999999)
        assert result is None

    def test_deactivate_user_success(self, sample_user):
        assert sample_user.is_active is True

        deactivated_user = CrudUser.deactivate_user(sample_user.id)

        assert deactivated_user is not None
        assert deactivated_user.is_active is False

    def test_deactivate_user_not_exists(self):
        result = CrudUser.deactivate_user(99999999)
        assert result is None
