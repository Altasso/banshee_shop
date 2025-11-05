from django.core.exceptions import ValidationError

from users.models import User, UserProfile


class UserProfileCrud:
    @staticmethod
    def get_profile(user: User) -> UserProfile | None:
        try:
            return user.profile
        except UserProfile.DoesNotExist:  # type: ignore
            return None

    @staticmethod
    def get_or_create_profile(user: User) -> UserProfile:
        profile, created = UserProfile.objects.get_or_create(user=user)
        return profile

    @staticmethod
    def create_profile(user: User, data: dict) -> UserProfile:
        if hasattr(user, "profile"):
            raise ValidationError("Профиль уже существует")
        profile = UserProfile.objects.create(
            user=user,
            phone=data.get("phone"),
            date_of_birth=data.get("date_of_birth"),
            preferred_delivery_method=data.get("preferred_delivery_method"),
        )
        return profile

    @staticmethod
    def update_profile(user: User, data: dict) -> UserProfile:
        profile = UserProfileCrud.get_or_create_profile(user)
        if "phone" in data:
            profile.phone = data["phone"]
        if "date_of_birth" in data:
            profile.date_of_birth = data["date_of_birth"]
        if "preferred_delivery_method" in data:
            profile.preferred_delivery_method = data["preferred_delivery_method"]

        profile.save()
        return profile

    @staticmethod
    def delete_profile(user: User) -> bool:
        try:
            profile = user.profile
            profile.delete()
            return True
        except UserProfile.DoesNotExist:  # type: ignore
            return False
