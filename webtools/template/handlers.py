# -*- coding: utf-8 -*-

class ResponseHandlerMixin(object):
    def get_template(self, template_name):
        return self.application.jinja_env.get_template(template_name)

    def render(self, template, context={}):
        template = self.get_template(template)
        context = self._populate_context_form_ctxprocessors(context)

        for chuck in template.generate(context):
            self.write(chuck)

    def render_to_string(self, template, context={}):
        template = self.get_template(template)
        context = self._populate_context_form_ctxprocessors(context)
        return template.render(context)

    def _populate_context_form_ctxprocessors(self, context):
        ctx = {}
        ctx.update(context)

        for ctx_processor in self.context_processors:
            ctx.update(ctx_processor(self))

        return ctx
