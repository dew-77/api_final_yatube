from rest_framework import viewsets, status
from rest_framework import filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated,
    AllowAny
)
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from posts.models import Post, Group, Follow, User
from .permissions import IsAuthor
from .serializers import (
    PostSerializer, CommentSerializer,
    GroupSerializer, FollowSerializer
)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('author')
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthor)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthor)

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        return post.comments.select_related('author')

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(author=self.request.user, post=post)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def list(self, request):
        queryset = self.filter_queryset(
            Follow.objects.filter(user=request.user))
        serializer = FollowSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        following = request.data.get('following')

        if request.user.username == following:
            return Response(
                "Нельзя подписаться на себя!",
                status=status.HTTP_400_BAD_REQUEST)

        try:
            following = User.objects.get(username=following)
        except User.DoesNotExist:
            return Response(
                "Пользователь не найден.", status=status.HTTP_400_BAD_REQUEST)

        if Follow.objects.filter(
                user=request.user, following=following).exists():
            return Response(
                "Вы уже подписаны на этого пользователя.",
                status=status.HTTP_400_BAD_REQUEST
            )

        follow = Follow(user=request.user, following=following)
        follow.save()
        serializer = FollowSerializer(follow)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
