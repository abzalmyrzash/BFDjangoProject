from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models import Q
from utils.constants import GENDERS, REQUEST_STATUS_ACCEPTED
from utils.validators import validate_extension, validate_size
# Create your models here.


class CustomUserManager(BaseUserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

    def get_related(self):
        return self.prefetch_related('profile', 'posts', 'comments', 'owns_groups', 'member_of_groups',
                                     'admin_of_groups', 'reactions', 'sent_friendrequests',
                                     'incoming_friendrequests', 'sent_groupjoinrequests', 'sent_groupinvites')

    # def get_friends(self, user_id):
    #     return self.prefetch_related('sent_friendrequests', 'incoming_friendrequests').\
    #         exclude(id=user_id).\
    #         filter((Q(sent_friendrequests__status=REQUEST_STATUS_ACCEPTED) &
    #                 Q(sent_friendrequests__to_user__id=user_id)) |
    #                (Q(incoming_friendrequests=REQUEST_STATUS_ACCEPTED) &
    #                 Q(incoming_friendrequests__from_user__id=user_id)))


class CustomUser(AbstractUser):
    objects = CustomUserManager()
    is_private = models.BooleanField(default=False, verbose_name="Приватность")
    friends = models.ManyToManyField("self", blank=True)
    # delete first_name and last_name because they will be in profile
    first_name = None
    last_name = None


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь",
                                related_name="profile")
    first_name = models.CharField(max_length=50, blank=True, verbose_name="Имя")
    middle_name = models.CharField(max_length=50, blank=True, verbose_name="Отчество")
    last_name = models.CharField(max_length=50, blank=True, verbose_name="Фамилия")
    avatar = models.ImageField(upload_to='avatars',
                               validators=[validate_size, validate_extension],
                               null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    gender = models.SmallIntegerField(choices=GENDERS, null=True, blank=True, verbose_name="Пол")
    location = models.CharField(max_length=255, blank=True, verbose_name="Местоположение")
    bio = models.TextField(max_length=500, blank=True, verbose_name="Биография")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Телефонный номер")

    def __str__(self):
        return self.user.username

    def get_full_name(self, format='fml'):
        """
        :param format: string, consists of characters that determine the format of the full name
                       'f' - first name (e.g. "Abzal")
                       'F' - first name initial (e.g. "A.")
                       'm' - middle name (e.g. "Daurenbekuly")
                       'M' - middle name initial (e.g. "D.")
                       'l' - last name (e.g. "Myrzash")
                       'L' - last name initial (e.g. "M.")
                       profile.get_full_name('fml') returns "Abzal Daurenbekuly Myrzash"
                       profile.get_full_name('lfm') returns "Myrzash Abzal Daurenbekuly"
                       profile.get_full_name('lf') returns "Myrzash Abzal"
                       profile.get_full_name('lFM') returns "Myrzash A. D."
        :return: string, full name formatted in :param format, but if it's blank return @username
        """
        if len(format) == 0:
            raise ValueError("Format must have at least 1 character!")

        full_name = ''
        for char in format:
            if char == 'f':
                if not self.first_name:
                    continue
                full_name += self.first_name
            elif char == 'F':
                if not self.first_name:
                    continue
                full_name += self.first_name[0] + '.'
            elif char == 'm':
                if not self.middle_name:
                    continue
                full_name += self.middle_name
            elif char == 'M':
                if not self.middle_name:
                    continue
                full_name += self.middle_name[0] + '.'
            elif char == 'l':
                if not self.last_name:
                    continue
                full_name += self.last_name
            elif char == 'L':
                if not self.last_name:
                    continue
                full_name += self.last_name[0] + '.'
            else:
                raise ValueError("Format can only contain characters: fFmMlL")
            full_name += ' '

        if full_name == ' ' or full_name == '':  # if full name is empty return username
            return f"@{self.user.username}"

        return full_name[:-1]  # don't include last space
