from application.models.users import Users


class UserIsConfirmedException(Exception):
    def __init__(self, message, user: Users):
        super(Exception, self).__init__()
        self.message = message
        self.user = user
