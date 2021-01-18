#!/usr/bin/env python3
from models import Person


def list() -> list:
    people = Person.get_all()
    return [person.dump() for person in people]


def add(person: dict) -> tuple:
    obj = Person.load(**person)
    obj.save()
    return obj.dump()
