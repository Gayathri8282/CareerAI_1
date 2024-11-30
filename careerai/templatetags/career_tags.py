from django import template

register = template.Library()

@register.filter
def progress_width(value):
    """Convert a number to a percentage string for CSS width"""
    try:
        return f"{int(value)}%"
    except (ValueError, TypeError):
        return "0%"
