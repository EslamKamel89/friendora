from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request


class IsOwnerOrReadonly(BasePermission):
    def has_object_permission(self, request: Request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAuthenticatedForUnsafeMethods(BasePermission):
    def has_permission(self, request: Request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


class IsNotPostOwner(BasePermission):
    def has_object_permission(self, request: Request, view, obj):
        return request.user != obj.author


class IsNotStaff(BasePermission):
    def has_permission(self, request, view):  # type: ignore
        if request.method in SAFE_METHODS:
            return True
        return not request.user.is_staff
