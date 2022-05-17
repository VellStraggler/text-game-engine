class Person():
    def __init__(self,name):
        self.name = name

guy = Person("James")
print(id(guy))