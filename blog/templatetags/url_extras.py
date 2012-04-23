from django import template
from django.core.urlresolvers import reverse
import re

register = template.Library()

""" Geturl is meant to act much like the built-in {% url %} tag, but lets you include GET variables.
    The syntax is a bit different to support any number of arguments for a named url, and any number
    of GET variables:

    {% geturl urlname ["viewarg1 viewarg2 ..."] ["getvar1=getval2 getvar2=getval2 ..."] %}

    geturl only takes up to 3 arguments, but the 2nd and 3rd arguments can be space-separated
    lists of variable size (and must be enclosed in double or single quotes).

    The 2nd and 3rd arguments may also be template variables. The tag will try to resolve them as
    template variables first and if it can't, will use the literal values.

    If you want to specify GET variables without url arguments, provide an empty string (e.g. "") as
    the 2nd argument.
"""

class GeturlNode(template.Node):
    def __init__(self, url_name, url_args=None, get_vars=None):
        self.url_name = url_name
        self.url_args = url_args
        self.get_vars = get_vars
    def render(self, context):
        # Process the url arguments
        if len(self.url_args) > 0:
            # We have to check if each argument is a template variable.
            # Checked items will be appended to this list
            final_args = []

            # Assign each argument to be a template variable and try to resolve it
            for arg in self.url_args:
                temp = template.Variable(arg)

                try:
                    varg = temp.resolve(context)
                    final_args.append(varg)
                except template.VariableDoesNotExist:
                    # If we can't resolve it, just use the literal value
                    # Let urlresolvers.reverse() handle the rest
                    final_args.append(arg)
                
            return_string = reverse(self.url_name, args=final_args)
        else:
            return_string = reverse(self.url_name)

        # Process the GET variables
        if len(self.get_vars) > 0:
            return_string += '?'

            for name, value in self.get_vars.items():
                temp = template.Variable(value)

                try:
                    vvar = temp.resolve(context)
                    return_string += name+'='+str(vvar)+'&'
                except template.VariableDoesNotExist:
                    # If it's not a template variable, it shouldn't have a '.'
                    # So if it does, reraise
                    if '.' in value:
                        raise
                    # If here, just use the literal value    
                    return_string += name+'='+value+'&'
            else:
                # At the end of the loop, remove the last '&' character
                return_string = return_string[:-1]

        return return_string

def handle_geturl(parser, token):
    # This includes everything enclosed in {% %}, including the tag's name
    contents = token.split_contents()
    url_name = ""
    url_args = []
    get_vars = {}

    if len(contents) == 1:
        raise template.TemplateSyntaxError("%r tag requires at least one argument" % contents[0])
    if len(contents) > 1:
        url_name = contents[1]
    if len(contents) > 2:
        raw_url_args = contents[2]

        # Check if the 1st argument is enclosed in quotes
        if not (raw_url_args[0] == raw_url_args[-1] and raw_url_args[0] in ('"', "'")):
            raise template.TemplateSyntaxError("%r tag's first argument must be in quotes" % contents[0])

        # If there is text in the quotes, convert it into a list
        if len(raw_url_args[1:-1]) > 0:
            url_args = raw_url_args[1:-1].split()

    if len(contents) > 3:
        raw_get_vars = contents[3]

        # Check if the 2nd argument is enclosed in quotes
        if not (raw_get_vars[0] == raw_get_vars[-1] and raw_get_vars[0] in ('"', "'")):
            raise template.TemplateSyntaxError("%r tag's second argument must be in quotes" % contents[0])

        # Check if the 2nd argument has something enclosed in the quotes
        if len(raw_get_vars[1:-1]) == 0:
            raise template.TemplateSyntaxError("%r tag's second argument was empty" % contents[0])

        # Convert the text enclosed in brackets into a list
        list_get_vars = raw_get_vars[1:-1].split()

        # Ensure each GET argument has the form [variableName=variableValue]
        # Include the '.' on the right side in case we are dealing with a template variable (like forloop.counter)
        regex = re.compile(r'([\w]+)=([\w.]+)')

        for (count, var) in enumerate(list_get_vars):
            match = re.match(regex, var)

            if match is None:
                raise template.TemplateSyntaxError("%r tag's GET variable %d is malformed - expected variableName=variableValue, got %s" % (contents[0], count, var))

            get_vars[match.group(1)] = match.group(2)

    if len(contents) > 4:
        raise template.TemplateSyntaxError("%r tag doesn't take more than 3 arguments" % contents[0])

    return GeturlNode(url_name, url_args, get_vars)

register.tag('geturl', handle_geturl)
