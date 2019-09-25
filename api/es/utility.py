def is_ascii(s: str):
    return all(ord(char) < 128 for char in s)
