from pydantic import BaseModel, conint
from typing import List, Optional


class User(BaseModel):
    username: str


class Expense(BaseModel):
    value: conint(gt=0)
    spender: User
    exclude_users: Optional[List[User]]


class Group:
    def __init__(self, name, users):
        self.name: str = name
        self._expenses: List[Expense] = []
        self._users: List[User] = users
        self._map = {}

    def generate_pairs_of_users(self):
        pass

    def update_account(self):
        pass

    def print_account(self):
        pass

    def add_expense(self, expense: Expense) -> None:
        pass

    def add_expenses(self, expenses: List[Expense]) -> None:
        for expense in expenses:
            self.add_expense(expense)

    def print_expenses(self):
        pass

    def add_user(self):
        pass

    def add_users(self):
        pass

    def remove_user(self):
        pass
