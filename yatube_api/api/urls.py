from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import PostViewSet, GroupViewSet, CommentViewSet, FollowViewSet

PREFIX = 'v1/'

router = DefaultRouter()
router.register(f'{PREFIX}posts', PostViewSet, basename='posts')
router.register(f'{PREFIX}groups', GroupViewSet)
router.register(
    f'{PREFIX}posts/(?P<post_id>[^/.]+)/comments',
    CommentViewSet,
    basename='post-comments'
)
router.register(f'{PREFIX}follow', FollowViewSet, basename='follow')


urlpatterns = [
    path('', include(router.urls)),
    path(f'{PREFIX}', include('djoser.urls')),
    path(f'{PREFIX}', include('djoser.urls.jwt')),
]
