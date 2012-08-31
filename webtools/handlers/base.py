import tornado.web

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def session(self):
        return self.application.session_engine

    def on_finish(self):
        if self.session and self.session.is_modified:
            self.session.save()

        super(BaseHandler, self).on_finish()
