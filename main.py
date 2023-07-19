from typing import List, Dict, Optional

from pydantic import BaseModel, conint, field_validator
from pydantic_core.core_schema import FieldValidationInfo


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
    exclude_users: Optional[List[User]] = []

    @field_validator('exclude_users')
    def spender_not_in_exclude_users(cls, v, info: FieldValidationInfo):
        if 'spender' in info.data and info.data['spender'] in v:
            raise ValueError('spender cannot be excluded')
        return v


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
                share_amount = expense.value // (len(self._users) - len(expense.exclude_users))
                for key, rel in self._map.items():
                    if expense.spender.username in key and \
                            all(map(lambda user: user.username not in key, expense.exclude_users)):
                        if rel.creditor.username == expense.spender.username:
                            rel.balance += share_amount
                        else:
                            rel.balance -= share_amount
                expense.is_calculated = True

    def get_balances(self) -> List[str]:
        list_of_strs = []
        for rel in self._map.values():
            if rel.balance > 0:
                list_of_strs.append(
                    f"{rel.debtor.username.ljust(15)} must give    {'{0:,}'.format(rel.balance).ljust(10)} to {rel.creditor.username}")
            else:

                list_of_strs.append(
                    f"{rel.creditor.username.ljust(15)} must give    {'{0:,}'.format(-1 * rel.balance).ljust(10)} to {rel.debtor.username}")
        return sorted(list_of_strs)

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
    mehdi = User(username="mehdi")
    mojix = User(username="mojix")
    pesar_amme = User(username="pesar_amme")

    g = Group(name="g1", users=[mmd, mehdi, mojix, pesar_amme])

    g.add_expenses(
        [
            Expense(spender=mmd, value=78_000),
            Expense(spender=mmd, value=28_000),
            Expense(spender=mmd, value=329_000),
            Expense(spender=mmd, value=33_000),
            Expense(spender=mmd, value=22_000, exclude_users=[mojix, pesar_amme]),
            Expense(spender=mmd, value=150_000, exclude_users=[mojix, pesar_amme]),
            Expense(spender=mmd, value=142_000, exclude_users=[mojix, pesar_amme]),
            Expense(spender=mehdi, value=250_000),
            Expense(spender=mehdi, value=40_000),
            Expense(spender=mehdi, value=27_000),
            Expense(spender=mehdi, value=35_000, exclude_users=[mojix, pesar_amme]),
            Expense(spender=mojix, value=120_000),
        ])

    print(*g.get_balances(), sep="\n")
