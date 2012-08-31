
def auth(handler):
    if not handler.application.session_engine:
        return {}

    if not handler.application.auth_backends:
        return {}

    return {'user': handler.get_current_user()}
