from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(role):
    """Require an authenticated community role before running a view."""
    def decorator(view):
        @login_required(login_url='/login')
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.user.user_type != role:
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapped
    return decorator
