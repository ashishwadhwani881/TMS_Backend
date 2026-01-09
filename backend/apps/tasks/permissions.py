from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils import timezone
import pytz

class TaskPermission(BasePermission):

    def has_permission(self, request, view):
        role = request.user.role

        
        if role == "AUDITOR":
            return request.method in SAFE_METHODS

        return True

    def has_object_permission(self, request, view, obj):
        role = request.user.role

        
        if role == "AUDITOR":
            return request.method in SAFE_METHODS

        
        if role == "DEVELOPER":
            return obj.assigned_to == request.user

        
        return True




class TimeBasedTaskPermission(BasePermission):
   

    def has_object_permission(self, request, view, obj):

        
        if request.method in SAFE_METHODS:
            return True

        user = request.user

        
        if user.role == "AUDITOR":
            return False

        
        if user.role == "MANAGER":
            return True

        
        if user.role == "DEVELOPER":

            
            if obj.priority == "critical":
                return True

            
            try:
                user_tz = pytz.timezone(user.timezone)
            except Exception:
                return False  

            local_time = timezone.now().astimezone(user_tz)
            current_hour = local_time.hour

            
            return 9 <= current_hour < 18

        return False
