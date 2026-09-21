def is_not_empty(value: str) -> bool:
    return bool(value.strip())

def has_no_digits(value: str) -> bool:
    return not any(char.isdigit() for char in value)

def is_long_enough(value: str, min_length: int) -> bool:
    return len(value.strip()) >= min_length