import random
from django.db.models import Q, Count
from apps.posts.models import Post
from apps.users.models import User
from apps.hashtags.models import Hashtag
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def get_personalized_feed(user, limit=20):
    """
    Hybrid recommendation: 
    1. Posts from followed users (collaborative)
    2. Posts with similar hashtags (content-based)
    """
    # Followed posts
    followed_posts = Post.objects.filter(
        author__in=user.following.all(),
        is_blocked=False
    ).order_by('-created_at')[:limit]

    if followed_posts.count() >= limit:
        return followed_posts

    # Content-based: find posts with similar hashtags to user's liked posts
    user_liked_hashtags = Hashtag.objects.filter(
        posts__likes__user=user
    ).annotate(count=Count('posts')).order_by('-count')[:10]

    if user_liked_hashtags:
        similar_posts = Post.objects.filter(
            hashtags__in=user_liked_hashtags,
            is_blocked=False
        ).exclude(author=user).order_by('-created_at')[:limit - followed_posts.count()]
        combined = list(followed_posts) + list(similar_posts)
        # Remove duplicates and randomize a bit
        unique = {p.id: p for p in combined}.values()
        return list(unique)[:limit]

    # Fallback to random popular posts
    popular = Post.objects.filter(is_blocked=False).order_by('-likes_count')[:limit]
    return popular
