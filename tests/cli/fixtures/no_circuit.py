"""A valid Python file with no Circuit subclass — tests the
'no candidates' error path."""


def hello() -> str:
    return 'world'


class NotACircuit:
    pass
