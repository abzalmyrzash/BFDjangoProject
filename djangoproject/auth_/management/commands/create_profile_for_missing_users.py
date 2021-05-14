from django.core.management.base import BaseCommand
from auth_.models import CustomUser as User, Profile


class Command(BaseCommand):
    help = 'Create profile for users that do not have it'

    def handle(self, *args, **options):
        for user in User.objects.all():
            try:
                print(user.profile)
            except:
                Profile.objects.create(user=user)
                self.stdout.write("Created profile for %s" % user)
