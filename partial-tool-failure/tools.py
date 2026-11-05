import json, re

DATA = json.load(open("fixtures.json"))


def lookup_account(account):
    return DATA["accounts"][account.upper()]


def get_discount(account):
    return {"discount": DATA["discounts"][account.upper()]}


def calculate(expression):
    if not re.fullmatch(r"[\d\s.+\-*/()]+", expression):
        raise ValueError("only arithmetic is allowed")
    return {"result": eval(expression)}
