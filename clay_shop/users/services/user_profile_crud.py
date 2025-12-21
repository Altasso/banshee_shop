from django.core.exceptions import ValidationError

from users.models import User, UserProfile


class UserProfileCrud:

    @staticmethod
    def get_or_create_profile(user: User) -> UserProfile:
        profile, created = UserProfile.objects.get_or_create(user=user)
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
