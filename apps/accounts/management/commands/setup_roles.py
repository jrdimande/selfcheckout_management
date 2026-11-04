from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.accounts.permissions import ADMIN_GROUP, OPERATOR_GROUP


class Command(BaseCommand):
    help = "Cria os grupos Administrador e Operador."

    def handle(self, *args, **opts):
        for name in (ADMIN_GROUP, OPERATOR_GROUP):
            _, created = Group.objects.get_or_create(name=name)
            self.stdout.write(f"{name}: {'criado' if created else 'já existia'}")
