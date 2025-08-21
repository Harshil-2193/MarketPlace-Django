from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={'class': css_class})

@register.filter(name='add_attr')
def add_attr(field, arg):
    """Set a single HTML attribute on a form field widget.

    Usage in templates:
        {{ field|add_attr:'placeholder:jane@example.com' }}
        {{ field|add_attr:'autocomplete:username' }}
    """
    if not isinstance(arg, str) or ':' not in arg:
        return field
    attr_name, attr_value = arg.split(':', 1)
    attr_name = attr_name.strip()
    attr_value = attr_value.strip()
    return field.as_widget(attrs={attr_name: attr_value})