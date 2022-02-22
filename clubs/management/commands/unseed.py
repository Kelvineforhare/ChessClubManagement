from django.core.management.base import BaseCommand
from clubs.models import User,Club, Membership

class Command(BaseCommand):
    def __init__(self):
        super().__init__()

    def handle(self, *args, **options):
        User.objects.filter(is_staff=False, is_superuser=False).delete()
        Club.objects.all().delete()
        Membership.objects.all().delete()
        print("Unseeded!")
