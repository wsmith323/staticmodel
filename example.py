from constantmodel import ConstantModel


class Base(ConstantModel):
    _attr_names = 'code', 'name', 'description'

    def talk(self, greeting='Hello'):
        print('{greeting}. My name is {name}. Pleased to meet you.'.format(
            greeting=greeting, name=self.name))

    @classmethod
    def converse(cls, turn_taken=None):
        if turn_taken is None:
            turn_taken = set()

        decendent_classes = set()

        for decendent in cls.all():
            if decendent.code not in turn_taken:
                turn_taken.add(decendent.code)
                print('Hello. My name is {c.__name__}. What is yours?'.format(c=cls))
                decendent.talk()

            if decendent.__class__ is not cls:
                decendent_classes.add(decendent.__class__)

        for decendent_class in decendent_classes:
            decendent_class.converse(turn_taken=turn_taken)


class FarmAnimal(Base):
    _attr_names = 'code', 'name', 'description', 'extra'
    SUB_1_VAL_1 = ('s1v1', 'sub_1_val_1', 'Subclass 1, Value 1', 'stuff1')
    SUB_1_VAL_2 = ('s1v2', 'sub_1_val_2', 'Subclass 1, Value 2', 'stuff2')

    def talk(self, greeting="Help! Save me! They are going to kill me"):
        super().talk(greeting=greeting)


class HousePet(Base):
    _attr_names = Base._attr_names + ('extra',)
    SUB_2_VAL_1 = ('s2v1', 'sub_2_val_1', 'Subclass 2, Value 1', 'stuff1')
    SUB_2_VAL_2 = ('s2v2', 'sub_2_val_2', 'Subclass 2, Value 2', 'stuff2')

    def talk(self, greeting='My human will be home any moment'):
        super().talk(greeting=greeting)


class Cow(FarmAnimal, attr_names=FarmAnimal._attr_names[:-1]):
    SUB_3_VAL_1 = ('s3v1', 'sub_3_val_1', 'Subclass 3, Value 1', 'stuff1')
    SUB_3_VAL_2 = ('s3v2', 'sub_3_val_2', 'Subclass 3, Value 2', 'stuff2')

    def talk(self, greeting='Moo'):
        super().talk(greeting=', '.join(greeting for i in range(2)))


class Cat(HousePet, index_attr_names=HousePet._index_attr_names[:-1]):
    SUB_4_VAL_1 = ('s4v1', 'sub_4_val_1', 'Subclass 4, Value 1', 'stuff1')
    SUB_4_VAL_2 = ('s4v2', 'sub_4_val_2', 'Subclass 4, Value 2', 'stuff2')

    def talk(self, greeting='Meow'):
        print('{greeting}. You bore me.'.format(greeting=greeting))
