# -*- coding: utf-8 -*-

class ResponseHandlerMixin(object):
    def get_template(self, template_name):
        return self.application.jinja_env.get_template(template_name)

    def render(self, template, context={}):
        template = self.get_template(template)
        for chuck in template.generate(context):
            self.write(chuck)

    def render_to_string(self, template, context={}):
        template = self.get_template(template)
        return template.render(context)
