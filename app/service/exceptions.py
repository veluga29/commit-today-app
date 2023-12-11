class UserAlreadyExists(Exception):
    ...


class UserNotFound(Exception):
    ...


class PasswordNotMatch(Exception):
    ...


class InvalidToken(Exception):
    ...


class DailyTodoAlreadyExists(Exception):
    ...


class TodoRepoNotFound(Exception):
    ...


class DailyTodoNotFound(Exception):
    ...


class DailyTodoTaskNotFound(Exception):
    ...
