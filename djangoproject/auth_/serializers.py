from .models import CustomUser as User, Profile
from rest_framework import serializers
from datetime import date
from utils.constants import MINIMUM_AGE, GENDERS
import phonenumbers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'is_private')


class UserFullSerializer(UserSerializer):
    password = serializers.CharField(max_length=200, write_only=True)

    def create(self, validated_data):
        print(validated_data)
        user = User.objects.create(
            username=validated_data['username'],
            is_superuser=validated_data['is_superuser'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('email', 'password', 'date_joined', 'is_superuser',
                                               'is_staff', 'is_private')
        # fields = '__all__'



class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    def validate_birth_date(self, value):
        today = date.today()
        age = today.year - value.year
        # if user didn't have birthday this year, subtract 1 from age
        if value.month > today.month or (value.month == today.month and value.day > today.day):
            age -= 1

        if value.year < 1900 or age < MINIMUM_AGE:
            raise serializers.ValidationError('Invalid birth date')
        return value

    def validate_gender(self, value):
        for gender in GENDERS:
            if gender[0] == value:
                return value
        raise serializers.ValidationError('Invalid gender')

    def validate_phone(self, value):
        try:
            number = phonenumbers.parse(value)
        except:
            raise serializers.ValidationError('Invalid phone number')
        else:
            if not phonenumbers.is_possible_number(number):
                raise serializers.ValidationError('Invalid phone number')
        return value

    class Meta:
        model = Profile
        fields = ('id', 'user', 'first_name', 'middle_name', 'last_name', 'avatar', 'birth_date', 'gender',
                  'location', 'bio', 'phone')