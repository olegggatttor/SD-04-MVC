class BoardDoesNotExistException(Exception):
    pass


class UserDoesNotExistException(Exception):
    pass


class SameUserException(Exception):
    pass


class PipelineIsUsedInOtherBoards(Exception):
    pass


class PipelineDoesNotExistException(Exception):
    pass


class PipelineIsUsedException(Exception):
    pass


class TagDoesNotExistException(Exception):
    pass


class TagIsUsedException(Exception):
    pass


class TaskListDoesNotExistException(Exception):
    pass


class TaskDoesNotExistException(Exception):
    pass


class TagIsAlreadyOnTask(Exception):
    pass
