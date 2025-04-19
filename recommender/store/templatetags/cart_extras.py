from django import template

register = template.Library()

@register.simple_tag
def preserve_filters(request):
    return request.GET.urlencode()