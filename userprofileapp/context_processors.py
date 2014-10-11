
def profile(request):
    if hasattr(request, 'user_profile'):
        user_profile = request.user_profile
    else:
        from userprofileapp.models import AnonymousUserProfile
        user_profile = AnonymousUserProfile()
    return {
        'user_profile': user_profile,
    }