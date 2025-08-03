from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_role == 'admin'


class IsReceptionist(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_role == 'receptionist'


class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_role == 'doctor'


class DoctorRetrieve(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.id
