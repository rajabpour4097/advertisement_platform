from django import template
import jdatetime



register = template.Library()

@register.filter(name='jalali_timedate')
def jalali_timedate(value):
    if value:  # مطمئن شویم که فیلد دارای مقدار است
        jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        return f"{jalali_date.year}-{jalali_date.month:02}-{jalali_date.day:02} {jalali_date.hour:02}:{jalali_date.minute:02}:{jalali_date.second:02}"
    return None

