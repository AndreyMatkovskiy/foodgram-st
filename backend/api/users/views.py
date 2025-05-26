from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from djoser.views import UserViewSet
from users.models import User, Subscription
from .serializers import UserSerializer


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        author = self.get_object()
        Subscription.objects.get_or_create(
            user=request.user,
            author=author
        )
        return Response(status=201)

    @action(detail=True, methods=['delete'],
            permission_classes=[IsAuthenticated])
    def unsubscribe(self, request, id=None):
        author = self.get_object()
        Subscription.objects.filter(user=request.user, author=author).delete()
        return Response(status=204)
