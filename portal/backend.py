from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username = None, password = None, **kwargs):
        
        try:
            user = User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)).first()
        except User.DoesNotExist:
            return None
        
        if user is not None and user.check_password(password):
            return user
        return None
