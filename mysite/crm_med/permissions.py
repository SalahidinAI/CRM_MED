from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin'


class IsReceptionist(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'receptionist'


class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'doctor'

