from django.db import transaction

from users.models import User, UserAddress


class UserAddressCrud:
    @staticmethod
    def get_user_address(user: User) -> UserAddress:
        return UserAddress.objects.filter(user_id=user).order_by("-is_default", "title")

    @staticmethod
    def get_address_by_id(address_id: int) -> UserAddress | None:
        try:
            return UserAddress.objects.get(id=address_id)
        except UserAddress.DoesNotExist:
            return None

    @staticmethod
    def get_default_address(user: User) -> UserAddress | None:
        try:
            return UserAddress.objects.get(user_id=user, is_default=True)
        except UserAddress.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def create_address(user: User, data: dict) -> UserAddress:
        is_default = data.get("is_default", False)

        if is_default:
            UserAddress.objects.filter(user_id=user, is_default=True).update(
                is_default=False
            )

        if not UserAddress.objects.filter(user_id=user).exists():
            is_default = True

        address = UserAddress.objects.create(
            user_id=user,
            title=data.get("title"),
            address=data.get("address"),
            is_default=is_default,
        )
        return address

    @staticmethod
    @transaction.atomic
    def update_address(address_id: int, data: dict) -> UserAddress | None:
        address = UserAddressCrud.get_address_by_id(address_id)
        if not address:
            return None

        if "title" in data:
            address.title = data["title"]
        if "address" in data:
            address.address = data["address"]

        if data.get("is_default") and not address.is_default:
            UserAddress.objects.filter(user_id=address.user_id, is_default=True).update(
                is_default=False
            )
            address.is_default = True

        address.save()
        return address

    @staticmethod
    @transaction.atomic
    def set_default_address(address_id: int) -> UserAddress | None:
        address = UserAddressCrud.get_address_by_id(address_id)
        if not address:
            return None

        UserAddress.objects.filter(user_id=address.user_id, is_default=True).update(
            is_default=False
        )

        address.is_default = True
        address.save()

        return address

    @staticmethod
    def delete_address(address_id: int) -> bool:
        address = UserAddressCrud.get_address_by_id(address_id)
        if not address:
            return False
        was_default = address.is_default
        user = address.user_id
        address.delete()

        if was_default:
            first_address = UserAddress.objects.filter(user_id=user).first()
            if first_address:
                first_address.is_default = True
                first_address.save()

        return True

    @staticmethod
    def validate_address_owner(address: UserAddress, user: User) -> bool:
        return address.user_id.id == user.id
