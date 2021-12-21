from typing import List
from typing import Optional

from fastapi import Request
from controllers.registration.verify import verify_login, verify_password


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("login")
        self.password = form.get("password")

    async def is_valid(self):
        if not self.username or not verify_login(self.username):
            self.errors.append("Invalid username")
        if not self.password or not verify_password(self.password):
            self.errors.append("Wrong password format.")
        if not self.errors:
            return True
        return False
