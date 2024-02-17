import os


class LoginCredentials:
    def __init__(self):
        self.__username = os.environ.get('pictory.user.name')
        self.__password = os.environ.get('pictory.user.pass')

    def get_username(self) -> str:
        return self.__username

    def get_password(self) -> str:
        return self.__password
