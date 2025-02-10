from advplatform.models import CustomUser



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
