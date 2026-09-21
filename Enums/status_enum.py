import enum

class Status(str,enum.Enum):
    open = "open"
    in_progress = "in progress"
    closed = "closed"