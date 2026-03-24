from rest_framework import generics, permissions
from rest_framework.response import Response
from django.core.cache import cache
from django.db.models import Q
from apps.posts.models import Post
from apps.posts.serializers import PostSerializer
from .models import UserInterest
from .tasks import update_trending_hashtags
from .utils import get_personalized_feed

class TrendingHashtagsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        trending = cache.get('trending_hashtags')
        if trending is None:
            update_trending_hashtags.delay()
            trending = []
        return Response(trending)

class RecommendedPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Use hybrid recommendation (collaborative + content-based)
        feed = get_personalized_feed(user)
        return feed
