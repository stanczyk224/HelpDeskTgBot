import enum

class Role(str, enum.Enum):
    admin = 'admin'
    user = 'user'
