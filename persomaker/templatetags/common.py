from django import template
register = template.Library()


class SetVarNode(template.Node):

    def __init__(self, var_name, var_value):
        self.var_name = var_name
        self.var_value = var_value

    def render(self, context):
        try:
            value = template.Variable(self.var_value).resolve(context)
        except template.VariableDoesNotExist:
            value = ""
        context[self.var_name] = value

        return u""

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.tag(name='set')
def set_var(parser, token):
    """
    {% set some_var = '123' %}
    """
    parts = token.split_contents()
    if len(parts) < 4:
        raise template.TemplateSyntaxError("'set' tag must be of the form: {% set <var_name> = <var_value> %}")

    return SetVarNode(parts[1], parts[3])


@register.simple_tag(takes_context=True)
def url_active(context, *args, **kwargs):
    if 'request' not in context:
        return ''

    request = context['request']
    if request.resolver_match.url_name in args:
        return kwargs['success'] if 'success' in kwargs else 'active'
    else:
        return ''
