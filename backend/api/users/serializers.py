from rest_framework import serializers
from users.models import User, Subscription


class UserSerializer(serializers.ModelSerializer):
    user_subscribe = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'user_subscribe',
        ]

    def get_subscribe(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()
