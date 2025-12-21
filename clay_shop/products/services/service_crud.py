from typing import Any

from django.db import transaction
from django.db.models import QuerySet

from products.models import Service


class ServiceCrud:
    @staticmethod
    def get_active_services() -> QuerySet:
        return Service.objects.filter(is_active=True)

    @staticmethod
    def get_all_services() -> QuerySet:
        return Service.objects.all().order_by("name")

    @staticmethod
    def get_service_by_id(service_id: int) -> Service | None:
        try:
            return Service.objects.get(id=service_id, is_active=True)
        except Service.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def create_service(service_data: dict[str, Any]) -> Service:
        return Service.objects.create(**service_data)

    @staticmethod
    @transaction.atomic
    def update_service(service_id: int, service_data: dict[str, Any]) -> Service | None:
        try:
            service = Service.objects.get(id=service_id)
            for key, value in service_data.items():
                setattr(service, key, value)
            service.save()
            return service
        except Service.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def toggle_service_active(service_id: int) -> bool | None:
        try:
            service = Service.objects.get(id=service_id)
            service.is_active = not service.is_active
            service.save()
            return service.is_active
        except Service.DoesNotExist:
            return None

    @staticmethod
    def calculate_total_with_services(base_price: int, service_ids: list[int]) -> int:
        services = Service.objects.filter(id__in=service_ids, is_active=True)
        additional_cost = sum(service.price for service in services)
        return base_price + additional_cost
