from __future__ import annotations

from backend.app.models.video import Video


def evaluate_competitor_videos(videos: list[Video]) -> dict:
    total_views = sum(video.views for video in videos)
    total_engagement = sum(video.likes + video.comments + video.shares for video in videos)
    engagement_rate = total_engagement / total_views if total_views else 0
    return {
        "hook_strength": "HIGH" if engagement_rate >= 0.08 else "MEDIUM" if engagement_rate >= 0.035 else "LOW",
        "retention": "Product appears within first 2 seconds",
        "engagement": round(engagement_rate, 4),
        "comment_sentiment": "curiosity and purchase intent",
        "visual_pattern": [
            "Product appears within first 2 seconds",
            "Human reaction before explanation",
            "Demonstration before features",
        ],
    }
