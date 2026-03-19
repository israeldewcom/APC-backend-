from django.urls import path
from . import views

urlpatterns = [
    path('trending/hashtags/', views.TrendingHashtagsView.as_view(), name='trending-hashtags'),
    path('feed/', views.RecommendedPostsView.as_view(), name='recommended-feed'),
]
