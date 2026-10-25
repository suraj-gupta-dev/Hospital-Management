import re

from django.http import JsonResponse
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed

from .models import BookingSettings


class BookingClosureMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        # One-time config: compile regexes once, not per request.
        self.protected_paths = [
            re.compile(r"^/api/appointments/?$")
        ]

        self.protected_methods = {"POST"}
        self.staff_role = {"HA", "REC"}

    def __call__(self, request):
        # Runs BEFORE the view.
        blocked = self._check_booking_closer(request)

        if blocked is not None:
            return blocked

        response = self.get_response(request)

        return response

    def _check_booking_closer(self, request):
        if request.method not in self.protected_methods:
            return None

        if not any(p.match(request.path) for p in self.protected_paths):
            return None

        user = self._resolve_user(request)

        role = getattr(user, "role", None)
        
        if role in self.staff_role:
            return None

        print(role, BookingSettings.is_closed_now())
        if role == "PAT" and BookingSettings.is_closed_now():
            return JsonResponse({
                    "code": "BOOKING_CLOSED",
                    "message": "Appointment booking is temporarily closed.",
                }, status=403)
        
        return None


    """
    request.user in middleware is only populated for session-based auth (AuthenticationMiddleware).
    If your DRF API uses JWT (SimpleJWT) or DRF TokenAuthentication,
    request.user is AnonymousUser at middleware time — DRF authenticates inside the view.
    So in that case your middleware will see everyone as anonymous and the check will never fire.
    """
    def _resolve_user(self, request):
        user = getattr(request, "user", None)

        if user and user.is_authenticated:
            return user
        # try:
        #     result = JWTAuthentication().authenticate(request)
        #     return result[0] if result else None
        # except (InvalidToken, AuthenticationFailed):
        #     return None