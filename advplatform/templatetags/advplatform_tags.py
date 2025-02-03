from django import template

register = template.Library()

@register.filter
def format_price(value):
    try:
        value = int(value)  # تبدیل به عدد صحیح
        return f"{value:,}".replace(",", ".") + " تومان"
    except (ValueError, TypeError):
        return "نامعتبر"
