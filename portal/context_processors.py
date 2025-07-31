from .models import UserProfile
from django.contrib.auth.models import AnonymousUser
def user_role(request):
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            return {'role': profile.role}
        except UserProfile.DoesNotExist:
            return {'role': None}
    return {'role': None}