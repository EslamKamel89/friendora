from rest_framework.throttling import SimpleRateThrottle


class LikeThrottle(SimpleRateThrottle):
    scope = "like"


class FollowThrottle(SimpleRateThrottle):
    scope = "follow"
