from random import choice, shuffle
from string import ascii_letters, ascii_lowercase, ascii_uppercase, digits


def generate_password(length: int) -> str:

    password = [choice(ascii_uppercase), choice(ascii_lowercase), choice(digits)]
    print(password)
    remaining_length = length - 3
    password += [choice(ascii_letters + digits) for _ in range(remaining_length)]

    shuffle(password)

    return "".join(password)
