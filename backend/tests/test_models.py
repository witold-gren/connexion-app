import json
import uuid
import unittest
import flask_testing

from app import create_app
from extensions import db
from models.person import Person, generate_uuid, PersonEncoder, SexEnum


class ModelTests(flask_testing.TestCase):

    def create_app(self):
        application = create_app(config_name="testing")
        return application.app

    def setUp(self):
        """Define test variables and initialize app."""
        self.person = dict(
            uuid='4ac063d5-efc3-4d30-aa99-b7e5fe33b845',
            age=40,
            sex='male',
            fare=7.25,
            name='John Badduch',
            survived=True,
            passengerClass=3,
            siblingsOrSpousesAboard=0,
            parentsOrChildrenAboard=0
        )

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_person_encoder_uuid(self):
        genrated_uuid = uuid.uuid4()
        data = json.loads(json.dumps({'test_uuid': genrated_uuid}, cls=PersonEncoder))
        self.assertDictContainsSubset(data, {'test_uuid': str(genrated_uuid)})

    def test_person_encoder_enum(self):
        genrated_enum = SexEnum.male
        data = json.loads(json.dumps({'test_enum': genrated_enum}, cls=PersonEncoder))
        self.assertDictContainsSubset(data, {'test_enum': genrated_enum.value})

    def test_generate_uuid(self):
        uuid = generate_uuid()
        self.assertEqual(len(uuid), 36)
        uuid_part = uuid.split('-')
        self.assertEqual(len(uuid_part[0]), 8)
        self.assertEqual(len(uuid_part[1]), 4)
        self.assertEqual(len(uuid_part[2]), 4)
        self.assertEqual(len(uuid_part[3]), 4)
        self.assertEqual(len(uuid_part[4]), 12)

    def test_person_model_repr_representation(self):
        person = Person.load(**self.person)
        self.assertEqual(repr(person), f'<Person {person.name}>')

    def test_person_model_str_representation(self):
        person = Person.load(**self.person)
        self.assertEqual(str(person), person.name)

    def test_person_model_init(self):
        person = Person(**dict(
            uuid='4ac063d5-efc3-4d30-aa99-b7e5fe33b845',
            age=40,
            sex='male',
            fare=7.25,
            name='John Badduch',
            survived=True,
            passenger_class=3,
            siblings_or_spouses_aboard=0,
            parents_or_children_aboard=0
        ))
        self.assertEqual(person.uuid, '4ac063d5-efc3-4d30-aa99-b7e5fe33b845')
        self.assertEqual(person.age, 40)
        self.assertEqual(person.sex, 'male')
        self.assertEqual(person.fare, 7.25)
        self.assertEqual(person.name, 'John Badduch')
        self.assertTrue(person.survived)
        self.assertEqual(person.passenger_class, 3)
        self.assertEqual(person.siblings_or_spouses_aboard, 0)
        self.assertEqual(person.parents_or_children_aboard, 0)

    def test_person_model_validate_passenger_class_with_none(self):
        person = Person.load(**self.person)
        with self.assertRaises(AssertionError):
            person.validate_passenger_class('passenger_class', None)

    def test_person_model_validate_passenger_class_incorrect_value(self):
        person = Person.load(**self.person)
        with self.assertRaises(AssertionError):
            person.validate_passenger_class('passenger_class', '1')

    def test_person_model_validate_name(self):
        person = Person.load(**self.person)
        with self.assertRaises(AssertionError):
            person.validate_name('name', None)

    def test_person_model_validate_name_incorrect_value(self):
        person = Person.load(**self.person)
        with self.assertRaises(AssertionError):
            person.validate_name('name', 1)

    def test_person_model_validate_sex(self):
        person = Person.load(**self.person)
        with self.assertRaises(AssertionError):
            person.validate_sex('sex', None)

    def test_person_model_validate_sex_incorrect_value(self):
        person = Person.load(**self.person)
        with self.assertRaises(AssertionError):
            person.validate_sex('sex', 1)

    def test_person_model_validate_age(self):
        person = Person.load(**self.person)
        with self.assertRaises(AssertionError):
            person.validate_age('age', None)

    def test_person_model_validate_age_incorrect_value(self):
        person = Person.load(**self.person)
        with self.assertRaises(AssertionError):
            person.validate_age('age', '1')

    def test_person_model_validate_siblings_or_spouses_aboard(self):
        person = Person.load(**self.person)
        with self.assertRaises(AssertionError):
            person.validate_siblings_or_spouses_aboard('siblings_or_spouses_aboard', None)

    def test_person_model_validate_siblings_or_spouses_aboard_incorrect_value(self):
        person = Person.load(**self.person)
        with self.assertRaises(AssertionError):
            person.validate_siblings_or_spouses_aboard('siblings_or_spouses_aboard', '1')

    def test_person_model_validate_parents_or_children_aboard(self):
        person = Person.load(**self.person)
        with self.assertRaises(AssertionError):
            person.validate_parents_or_children_aboard('parents_or_children_aboard', None)

    def test_person_model_validate_parents_or_children_aboard_incorrect_value(self):
        person = Person.load(**self.person)
        with self.assertRaises(AssertionError):
            person.validate_parents_or_children_aboard('parents_or_children_aboard', '1')

    def test_person_model_validate_fare(self):
        person = Person.load(**self.person)
        with self.assertRaises(AssertionError):
            person.validate_fare('fare', None)

    def test_person_model_validate_fare_incorrect_value(self):
        person = Person.load(**self.person)
        with self.assertRaises(AssertionError):
            person.validate_fare('fare', 1)

    def test_person_model_update_object(self):
        person = Person.load(**self.person)
        person.update(**{'name': 'Alex'})
        self.assertEqual(person.name, 'Alex')

    def test_person_model_update_object_bad_value(self):
        person = Person.load(**self.person)
        person.update(**{'surname': 'Bombs'})
        self.assertFalse(hasattr(person, 'surname'))

    def test_person_model_save_object(self):
        person = Person.load(**self.person)
        person.save()
        self.assertEqual(Person.query.count(), 1)

    def test_person_model_delete_object(self):
        person = Person.load(**self.person)
        person.save()
        self.assertEqual(Person.query.count(), 1)
        person.delete()
        self.assertEqual(Person.query.count(), 0)

    def test_person_model_refresh_object(self):
        person = Person.load(**self.person)
        person.save()
        person.name = 'Tom'
        self.assertEqual(person.name, 'Tom')
        person.refresh()
        self.assertEqual(person.name, self.person['name'])

    def test_person_model_get_all_objects(self):
        person1 = self.person.copy()
        person2 = self.person.copy()
        del person1['uuid']
        del person2['uuid']
        Person.load(**person1).save()
        Person.load(**person2).save()
        self.assertEqual(len(Person.get_all()), 2)

    def test_person_model_to_camel_case(self):
        example1 = Person.to_camel_case('mydata')
        self.assertEqual(example1, 'mydata')
        example2 = Person.to_camel_case('my_data')
        self.assertEqual(example2, 'myData')
        example3 = Person.to_camel_case('my_extra_data')
        self.assertEqual(example3, 'myExtraData')
        example4 = Person.to_camel_case('convert2_dict')
        self.assertEqual(example4, 'convert2Dict')
        example5 = Person.to_camel_case('route53_testing')
        self.assertEqual(example5, 'route53Testing')

    def test_person_model_to_snake_case(self):
        example1 = Person.to_snake_case('mydata')
        self.assertEqual(example1, 'mydata')
        example2 = Person.to_snake_case('myData')
        self.assertEqual(example2, 'my_data')
        example3 = Person.to_snake_case('myExtraData')
        self.assertEqual(example3, 'my_extra_data')
        example4 = Person.to_snake_case('convert2Dict')
        self.assertEqual(example4, 'convert2_dict')
        example5 = Person.to_snake_case('route53Testing')
        self.assertEqual(example5, 'route53_testing')

    def test_person_model_dump_object(self):
        p = Person.load(**self.person)
        data = p.dump()
        self.assertDictContainsSubset(data, self.person)

    def test_person_model_load_object(self):
        person = Person.load(**self.person)
        self.assertEqual(person.uuid, self.person['uuid'])
        self.assertEqual(person.age, self.person['age'])
        self.assertEqual(person.sex, self.person['sex'])
        self.assertEqual(person.fare, self.person['fare'])
        self.assertEqual(person.name, self.person['name'])
        self.assertEqual(person.survived, self.person['survived'])
        self.assertEqual(person.passenger_class, self.person['passengerClass'])
        self.assertEqual(person.siblings_or_spouses_aboard, self.person['siblingsOrSpousesAboard'])
        self.assertEqual(person.parents_or_children_aboard, self.person['parentsOrChildrenAboard'])


if __name__ == '__main__':
    unittest.main()
