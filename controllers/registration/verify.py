from utils.constants import MIN_LOGIN_LENGTH, MAX_LOGIN_LENGTH, MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH


def verify_login(login: str) -> bool:
    return MIN_LOGIN_LENGTH <= len(login) <= MAX_LOGIN_LENGTH


def verify_password(password: str) -> bool:
    return MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH
