from inspect import getargspec


def func1(arg=None):
    print("Hey matey")
print(getargspec(func1))