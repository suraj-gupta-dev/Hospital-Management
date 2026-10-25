from appointments.models import BookingSettings


def run():
    setting = BookingSettings.objects.first()
    print(setting.closed_from)
    print(setting.closed_from.date())
    print(setting.closed_from.time())
    print(setting.closed_from.isoformat())
    print(setting.closed_from.isocalendar())