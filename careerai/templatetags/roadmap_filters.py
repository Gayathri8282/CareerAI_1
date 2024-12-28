from django import template

register = template.Library()

@register.filter
def completed_count(tasks):
    return sum(1 for task in tasks if task.completed)

@register.filter
def remaining_count(tasks):
    return sum(1 for task in tasks if not task.completed) 