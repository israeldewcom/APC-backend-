from rest_framework import generics, permissions
from rest_framework.response import Response
from django.core.cache import cache
from apps.posts.models import Post
from apps.posts.serializers import PostSerializer

class TrendingHashtagsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        trending = cache.get('trending_hashtags', [])
        return Response(trending)

class RecommendedPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        followed = user.following.all()
        return Post.objects.filter(author__in=followed).order_by('-created_at')[:20]
