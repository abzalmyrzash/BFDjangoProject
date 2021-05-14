from django.core.management.base import BaseCommand
from auth_.models import CustomUser as User, Profile


class Command(BaseCommand):
    help = 'Set the same password for all or selected users'

    def add_arguments(self, parser):
        parser.add_argument('password', type=str, help='New password')
        parser.add_argument('user_ids', nargs='+', type=int,
                            help='IDs of users included/excluded (depending on --exclude) for setting password')
        parser.add_argument('--exclude', action='store_true',
                            help='if provided, set password for all users EXCEPT users with given user_ids,'
                                 'otherwise, set password for all users WITH given user_ids')

    def handle(self, *args, **options):
        password = options.get('password')
        user_ids = options.get('user_ids')
        exclude = options.get('exclude')
        users = None

        if not exclude:
            users = User.objects.filter(id__in=user_ids)

        if exclude:
            users = User.objects.exclude(id__in=user_ids)

        for user in users:
            user.set_password(password)
            user.save()
            self.stdout.write('Set password %s for user %s' % (password, user))
