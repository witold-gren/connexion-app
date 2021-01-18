#!/usr/bin/env python3
import re
import json
import enum
import string
import uuid

from extensions import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates


SNAKE_CASE = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


class SexEnum(enum.Enum):
    male = 'male'
    female = 'female'
    other = 'other'


class PersonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def generate_uuid():
    return str(uuid.uuid4())


class Person(db.Model):
    uuid = db.Column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        primary_key=True,
        default=generate_uuid)
    survived = db.Column(
        db.Boolean,
        default=False)
    passenger_class = db.Column(
        db.Integer,
        nullable=False)
    name = db.Column(
        db.String(100),
        nullable=False)
    sex = db.Column(
        db.Enum(SexEnum),
        nullable=False,
        default=SexEnum.other)
    age = db.Column(
        db.Integer,
        nullable=False)
    siblings_or_spouses_aboard = db.Column(
        db.Integer,
        nullable=False)
    parents_or_children_aboard = db.Column(
        db.Integer,
        nullable=False)
    fare = db.Column(
        db.Float(),
        nullable=False)

    __tablename__ = 'person'

    def __repr__(self):
        return f'<Person {self.name}>'

    def __str__(self):
        return self.name

    def __init__(self, **kwargs):
        self.uuid = kwargs.pop('uuid', None)
        self.survived = kwargs.pop('survived', None)
        self.passenger_class = kwargs.pop('passenger_class', None)
        self.name = kwargs.pop('name', None)
        self.sex = kwargs.pop('sex', None)
        self.age = kwargs.pop('age', None)
        self.siblings_or_spouses_aboard = kwargs.pop('siblings_or_spouses_aboard', None)
        self.parents_or_children_aboard = kwargs.pop('parents_or_children_aboard', None)
        self.fare = kwargs.pop('fare', None)

    @validates('passenger_class')
    def validate_passenger_class(self, key, value):
        if value is None:
            raise AssertionError('No `passengerClass` provided')
        if not isinstance(value, int):
            raise AssertionError('Incorrect type of value for `passengerClass`')
        return value

    @validates('name')
    def validate_name(self, key, value):
        if value is None:
            raise AssertionError('No `name` provided')
        if not isinstance(value, str):
            raise AssertionError('Incorrect type of value for `name`')
        if len(value) > 100:
            raise AssertionError('To long value for `name`. Max 100 chars.')
        return value

    @validates('sex')
    def validate_sex(self, key, value):
        if value is None:
            raise AssertionError('No `sex` provided')
        if not value in [item.value for item in SexEnum]:
            raise AssertionError('Incorrect value for `sex`')
        return value

    @validates('age')
    def validate_age(self, key, value):
        if value is None:
            raise AssertionError('No `age` provided')
        if not isinstance(value, int):
            raise AssertionError('Incorrect type of value for `age`')
        return value

    @validates('siblings_or_spouses_aboard')
    def validate_siblings_or_spouses_aboard(self, key, value):
        if value is None:
            raise AssertionError('No `siblingsOrSpousesAboard` provided')
        if not isinstance(value, int):
            raise AssertionError('Incorrect type of value for `siblingsOrSpousesAboard`')
        return value

    @validates('parents_or_children_aboard')
    def validate_parents_or_children_aboard(self, key, value):
        if value is None:
            raise AssertionError('No `parentsOrChildrenAboard` provided')
        if not isinstance(value, int):
            raise AssertionError('Incorrect type of value for `parentsOrChildrenAboard`')
        return value

    @validates('fare')
    def validate_fare(self, key, value):
        if value is None:
            raise AssertionError('No `fare` provided')
        if not isinstance(value, float):
            raise AssertionError('Incorrect type of value for `fare`')
        return value

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, self.to_snake_case(k)):
                setattr(self, self.to_snake_case(k), v)

    def save(self):
        db.session.add(self)
        db.session.commit()
        self.refresh()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def refresh(self):
        db.session.refresh(self)

    @staticmethod
    def get_all():
        return Person.query.all()

    @staticmethod
    def to_camel_case(snake_str):
        return snake_str[0].lower() + string.capwords(
            snake_str, sep='_').replace('_', '')[1:] if snake_str else snake_str

    @staticmethod
    def to_snake_case(camel_str):
        return SNAKE_CASE.sub(r'_\1', camel_str).lower()

    def dump(self):
        return json.loads(json.dumps(
            dict([(self.to_camel_case(k), v) for k, v in vars(self).items() if not k.startswith('_')]),
            cls=PersonEncoder
        ))

    @classmethod
    def load(cls, **kwargs):
        return cls(**dict([(cls.to_snake_case(k), v) for k, v in kwargs.items()]))
