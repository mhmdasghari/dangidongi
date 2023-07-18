from typing import List, Dict

from pydantic import BaseModel, conint


class User(BaseModel):
    username: str


class PairUserRelation(BaseModel):
    creditor: User
    debtor: User
    balance: int


class Expense(BaseModel):
    value: conint(gt=0)
    spender: User
    is_calculated: bool = False
    # exclude_users: Optional[List[User]]


class Group:
    def __init__(self, name, users):
        self.name: str = name
        self._expenses: List[Expense] = []
        self._users: List[User] = users
        self._map: Dict[str, PairUserRelation] = {}
        self.generate_pairs_of_users()

    def generate_pairs_of_users(self):
        for creditor_user in self._users:
            for debtor_user in self._users:
                if creditor_user != debtor_user:
                    key = f"{creditor_user.username}-{debtor_user.username}"
                    reverse_key = f"{debtor_user.username}-{creditor_user.username}"
                    if self._map.get(key) is None and self._map.get(reverse_key) is None:
                        self._map[key] = PairUserRelation(creditor=creditor_user, debtor=debtor_user, balance=0)

    def update_balances(self):
        for expense in self._expenses[-1::-1]:
            if expense.is_calculated is False:
                share_amount = expense.value // len(self._users)
                for key, rel in self._map.items():
                    if expense.spender.username in key:
                        if rel.creditor.username == expense.spender.username:
                            rel.balance += share_amount
                        else:
                            rel.balance -= share_amount
                expense.is_calculated = True

    def get_balances(self) -> List[str]:
        list_of_strs = []
        for rel in self._map.values():
            if rel.balance > 0:
                list_of_strs.append(f"{rel.debtor.username} must give {rel.balance} to {rel.creditor.username}")
            else:
                list_of_strs.append(f"{rel.creditor.username} must give {-1 * rel.balance} to {rel.debtor.username}")
        return list_of_strs

    def add_expense(self, expense: Expense) -> None:
        self._expenses.append(expense)
        self.update_balances()

    def add_expenses(self, expenses: List[Expense]) -> None:
        for expense in expenses:
            self.add_expense(expense)

    # def print_expenses(self):
    #     for expense in self._expenses:
    #         print(expense)

    # def add_user(self):
    #     pass
    #
    # def add_users(self):
    #     pass
    #
    # def remove_user(self):
    #     pass


if __name__ == "__main__":
    mmd = User(username="mmd")
    ali = User(username="ali")
    reza = User(username="reza")

    g = Group(name="g1", users=[mmd, ali, reza])

    g.add_expenses(
        [Expense(spender=mmd, value=100000), Expense(spender=ali, value=150000), Expense(spender=mmd, value=100000)])

    print(*g.get_balances(), sep="\n")
