from advplatform.models import CustomUser
from notifications.models import Notification




def user_null_field_percentage(request):
    if request.user.is_authenticated:
        try:
            user = CustomUser.objects.get(pk=request.user.id)
            field_count = user.get_field_count()
            null_field_count = user.count_null_fields()
            null_field_count_percent = 0 if null_field_count == 0 else 100 - (null_field_count * 100 / field_count)
            return {'null_field_count_percent': null_field_count_percent}
        except CustomUser.DoesNotExist:
            return {'null_field_count_percent': None}
    return {'null_field_count_percent': None}

def latest_notifications(request):
    if request.user.is_authenticated:
        last_notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')[:3]
    else:
        last_notifications = []
    
    return {'latest_notifications': last_notifications}