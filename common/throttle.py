from rest_framework.throttling import SimpleRateThrottle


class LikeThrottle(SimpleRateThrottle):
    scope = "like"

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class FollowThrottle(SimpleRateThrottle):
    scope = "follow"

    def get_cache_key(self, request, view):
        return self.get_ident(request)
