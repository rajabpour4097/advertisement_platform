from django import template
import jdatetime



register = template.Library()

@register.filter(name='jalali_timedate')
def jalali_timedate(value):
    if value:  # مطمئن شویم که فیلد دارای مقدار است
        jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        return f"{jalali_date.year}-{jalali_date.month:02}-{jalali_date.day:02} {jalali_date.hour:02}:{jalali_date.minute:02}:{jalali_date.second:02}"
    return None

@register.filter
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})

@register.filter
def is_participant(campaign, user):
    return campaign.list_of_participants.filter(id=user.id).exists()
