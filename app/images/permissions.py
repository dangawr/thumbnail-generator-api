from rest_framework import permissions


class TempLinkUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.user.tier.temporary_link)
