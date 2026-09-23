import enum

class NotificationKind(str, enum.Enum):
    author = "author"
    group = "group"
    admin = "admin"