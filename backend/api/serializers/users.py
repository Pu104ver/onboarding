from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.validators import check_valid_email, check_valid_password


User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "is_active",
            "is_staff",
            "date_joined",
            "password",
        ]

        extra_kwargs = {
            "is_active": {"required": False, "default": True},
            "is_staff": {"required": False, "default": False},
            "password": {"write_only": True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                f"Пользователь с почтой {value} уже существует."
            )
        correct, error = check_valid_email(email=value)
        if not correct:
            raise serializers.ValidationError(error)
        return value

    def validate_password(self, value):
        correct, error = check_valid_password(value)
        if not correct:
            raise serializers.ValidationError(error)
        return value
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.get("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            instance.set_password(password)
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
        ]


class AuthenticationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                msg = "Пользователь с таким email не найден."
                raise serializers.ValidationError(msg, code="authorization")

            if not user.check_password(password):
                msg = "Пароль неверный."
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = "Необходимо указать email и пароль."
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs
