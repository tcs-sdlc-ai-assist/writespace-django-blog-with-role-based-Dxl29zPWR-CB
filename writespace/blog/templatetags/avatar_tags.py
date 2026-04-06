from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def avatar(user):
    if user.is_staff:
        emoji = '👑'
        bg_class = 'bg-purple-600'
    else:
        emoji = '📖'
        bg_class = 'bg-blue-600'

    html = (
        f'<span class="{bg_class} inline-flex items-center justify-center'
        f' w-8 h-8 rounded-full text-white text-sm" title="{user.username}">'
        f'{emoji}</span>'
    )
    return mark_safe(html)