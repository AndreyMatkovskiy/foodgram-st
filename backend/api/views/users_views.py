from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from djoser.views import UserViewSet as DjoserUserViewSet
from users.models import User, Subscription
from ..serializers.users_serializers import (
    UserSerializer,
    SubscriptionSerializer
)
from api.paginations import Pagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import base64
from django.core.files.base import ContentFile


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    pagination_class = Pagination

    def get_permissions(self):
        if self.action == 'me':
            return [permissions.IsAuthenticated()]
        if self.action in [
            'subscribe',
            'unsubscribe',
            'avatar',
            'delete_avatar'
        ]:
            return [permissions.IsAuthenticated()]
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        following_ids = Subscription.objects.filter(
            follower=request.user
        ).values_list('following', flat=True)
        authors = User.objects.filter(id__in=following_ids).order_by('id')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit and recipes_limit.isdigit():
            recipes_limit = int(recipes_limit)
        else:
            recipes_limit = None
        page = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={
                'request': request,
                'recipes_limit': recipes_limit
            }
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        author = self.get_object()
        subscription = Subscription.objects.filter(
            follower=request.user,
            following=author
        ).first()
        if request.method == 'POST':
            if request.user.id == author.id:
                return Response(
                    {"error": "Нельзя подписаться на самого себя"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if subscription:
                return Response(
                    {"error": "Подписка уже существует"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(
                follower=request.user,
                following=author
            )
            serializer = SubscriptionSerializer(
                author,
                context={
                    'request': request,
                    'recipes_limit': request.query_params.get('recipes_limit')
                }
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not subscription:
            return Response(
                {"error": "Подписка не найдена"},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        parser_classes=[MultiPartParser, FormParser, JSONParser]
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            if 'avatar' not in request.data:
                return Response(
                    {"error": "Поле 'avatar' обязательно"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            avatar_file = request.data['avatar']
            if isinstance(avatar_file, str) and avatar_file.startswith(
                'data:image'
            ):
                format, imgstr = avatar_file.split(';base64,')
                ext = format.split('/')[-1]
                avatar_file = ContentFile(
                    base64.b64decode(imgstr),
                    name=f'avatar.{ext}'
                )
            user.avatar = avatar_file
            user.save()
            return Response(
                {"avatar": user.avatar.url},
                status=status.HTTP_200_OK
            )
        if user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
