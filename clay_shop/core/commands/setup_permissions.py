from django.core.management.base import BaseCommand
from users.services.auth_service import AuthService


class Command(BaseCommand):
    help = "Создает группы 3 трех ролей: покупатель, продавец, админ"

    def handle(self, *args, **options):
        AuthService.setup_default_groups()
        self.stdout.write(self.style.SUCCESS("Группы успешно созданы"))
