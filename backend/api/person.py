#!/usr/bin/env python3
from models import Person


def get(uuid) -> tuple:
    person = Person.query.get_or_404(uuid)
    return person.dump(), 200


def update(uuid, person) -> tuple:
    obj = Person.query.get_or_404(uuid)
    obj.update(**person)
    obj.save()
    return obj.dump(), 200


def delete(uuid) -> tuple:
    obj = Person.query.get_or_404(uuid)
    obj.delete()
    return {}, 200
