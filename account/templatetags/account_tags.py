from django import template
import jdatetime



register = template.Library()

@register.filter(name='jalali_timedate')
def jalali_timedate(value):
    if value:  # مطمئن شویم که فیلد دارای مقدار است
        jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        return f"{jalali_date.year}-{jalali_date.month:02}-{jalali_date.day:02} {jalali_date.hour:02}:{jalali_date.minute:02}:{jalali_date.second:02}"
    return None

@register.filter(name='jalali_date')
def jalali_date(value):
    if value:
        jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        return f"{jalali_date.year}-{jalali_date.month:02}-{jalali_date.day:02}"
    return None

@register.filter
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})

@register.filter
def is_participant(campaign, user):
    return campaign.list_of_participants.filter(id=user.id).exists()

@register.simple_tag
def get_campaign_participants_count(campaign):
    """
    Returns the number of participants for a campaign
    """
    if campaign.status == 'progressing':
        return campaign.list_of_participants.count()
    return 0

@register.filter
def format_participants_count(count):
    """
    Formats the participants count with proper Persian text
    """
    if count == 0:
        return "بدون شرکت‌کننده"
    return f"{count:,} شرکت‌کننده"


@register.filter
def endswith(value, suffix):
    if isinstance(value, str):
        return value.endswith(suffix)
    return False