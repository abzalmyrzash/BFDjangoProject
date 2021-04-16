from .models import CustomUser as User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    # reputation = serializers.IntegerField(read_only=True)
    password = serializers.CharField(max_length=200, write_only=True)

    def create(self, validated_data):
        print(validated_data)
        user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_superuser=validated_data['is_superuser'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'reputation',
                  'date_joined', 'is_superuser')
        # fields = '__all__'