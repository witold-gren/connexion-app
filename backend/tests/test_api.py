import json
import uuid
import unittest
import flask_testing

from app import create_app
from extensions import db
import models


class ApiTests(flask_testing.TestCase):
    response_error = {
        'detail': None,
        'status': 400,
        'title': 'Bad Request',
        'type': 'validation'}

    connexion_error = {
        'detail': None,
        'status': 400,
        'title': 'Bad Request',
        'type': 'about:blank'}

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

    # default page
    def test_get_default_http_response(self):
        response = self.client.get("/", content_type='application/json')
        self.assert404(response)

    # add person
    def test_add_new_person(self):
        response = self.client.post("/people", data=json.dumps(self.person), content_type='application/json')
        self.assert200(response)
        self.assertDictContainsSubset(response.json, self.person)

    def test_add_new_person_without_age(self):
        self.response_error['detail'] = 'No `age` provided'
        person = self.person.copy()
        del person['age']
        response = self.client.post("/people", data=json.dumps(person), content_type='application/json')
        self.assert400(response)
        self.assertDictContainsSubset(response.json, self.response_error)

    def test_add_new_person_with_incorrect_age(self):
        self.connexion_error['detail'] = "'20' is not of type 'integer' - 'age'"
        person = self.person.copy()
        person['age'] = '20'
        response = self.client.post("/people", data=json.dumps(person), content_type='application/json')
        self.assert400(response)
        self.assertDictContainsSubset(response.json, self.connexion_error)

    def test_add_new_person_without_sex(self):
        self.response_error['detail'] = 'No `sex` provided'
        person = self.person.copy()
        del person['sex']
        response = self.client.post("/people", data=json.dumps(person), content_type='application/json')
        self.assert400(response)
        self.assertDictContainsSubset(response.json, self.response_error)

    def test_add_new_person_with_incorrect_sex(self):
        self.connexion_error['detail'] = "'20' is not one of ['male', 'female', 'other'] - 'sex'"
        person = self.person.copy()
        person['sex'] = '20'
        response = self.client.post("/people", data=json.dumps(person), content_type='application/json')
        self.assert400(response)
        self.assertDictContainsSubset(response.json, self.connexion_error)

    def test_add_new_person_without_fare(self):
        self.response_error['detail'] = 'No `fare` provided'
        person = self.person.copy()
        del person['fare']
        response = self.client.post("/people", data=json.dumps(person), content_type='application/json')
        self.assert400(response)
        self.assertDictContainsSubset(response.json, self.response_error)

    def test_add_new_person_with_incorrect_fare(self):
        self.connexion_error['detail'] = "'20' is not of type 'number' - 'fare'"
        person = self.person.copy()
        person['fare'] = '20'
        response = self.client.post("/people", data=json.dumps(person), content_type='application/json')
        self.assert400(response)
        self.assertDictContainsSubset(response.json, self.connexion_error)

    def test_add_new_person_without_name(self):
        self.response_error['detail'] = 'No `name` provided'
        person = self.person.copy()
        del person['name']
        response = self.client.post("/people", data=json.dumps(person), content_type='application/json')
        self.assert400(response)
        self.assertDictContainsSubset(response.json, self.response_error)

    def test_add_new_person_with_incorrect_type_name(self):
        self.connexion_error['detail'] = "1 is not of type 'string' - 'name'"
        person = self.person.copy()
        person['name'] = 1
        response = self.client.post("/people", data=json.dumps(person), content_type='application/json')
        self.assert400(response)
        self.assertDictContainsSubset(response.json, self.connexion_error)

    def test_add_new_person_with_incorrect_lenght_name(self):
        self.response_error['detail'] = "To long value for `name`. Max 100 chars."
        person = self.person.copy()
        person['name'] = ''.join('.' for x in range(101))
        response = self.client.post("/people", data=json.dumps(person), content_type='application/json')
        self.assert400(response)
        self.assertDictContainsSubset(response.json, self.response_error)

    def test_add_new_person_without_survived(self):
        person = self.person.copy()
        del person['survived']
        person_response = self.person.copy()
        person_response['survived'] = False
        response = self.client.post("/people", data=json.dumps(person), content_type='application/json')
        self.assert200(response)
        self.assertDictContainsSubset(response.json, person_response)

    def test_add_new_person_with_incorrect_survived(self):
        self.connexion_error['detail'] = "1 is not of type 'boolean' - 'survived'"
        person = self.person.copy()
        person['survived'] = 1
        response = self.client.post("/people", data=json.dumps(person), content_type='application/json')
        self.assert400(response)
        self.assertDictContainsSubset(response.json, self.connexion_error)

    def test_add_new_person_without_passengerClass(self):
        self.response_error['detail'] = 'No `passengerClass` provided'
        person = self.person.copy()
        del person['passengerClass']
        response = self.client.post("/people", data=json.dumps(person), content_type='application/json')
        self.assert400(response)
        self.assertDictContainsSubset(response.json, self.response_error)

    def test_add_new_person_with_incorrect_passengerClass(self):
        self.connexion_error['detail'] = "'20' is not of type 'integer' - 'passengerClass'"
        person = self.person.copy()
        person['passengerClass'] = '20'
        response = self.client.post("/people", data=json.dumps(person), content_type='application/json')
        self.assert400(response)
        self.assertDictContainsSubset(response.json, self.connexion_error)

    def test_add_new_person_without_siblingsOrSpousesAboard(self):
        self.response_error['detail'] = 'No `siblingsOrSpousesAboard` provided'
        person = self.person.copy()
        del person['siblingsOrSpousesAboard']
        response = self.client.post("/people", data=json.dumps(person), content_type='application/json')
        self.assert400(response)
        self.assertDictContainsSubset(response.json, self.response_error)

    def test_add_new_person_with_incorrect_siblingsOrSpousesAboard(self):
        self.connexion_error['detail'] = "'20' is not of type 'integer' - 'siblingsOrSpousesAboard'"
        person = self.person.copy()
        person['siblingsOrSpousesAboard'] = '20'
        response = self.client.post("/people", data=json.dumps(person), content_type='application/json')
        self.assert400(response)
        self.assertDictContainsSubset(response.json, self.connexion_error)

    def test_add_new_person_without_parentsOrChildrenAboard(self):
        self.response_error['detail'] = 'No `parentsOrChildrenAboard` provided'
        person = self.person.copy()
        del person['parentsOrChildrenAboard']
        response = self.client.post("/people", data=json.dumps(person), content_type='application/json')
        self.assert400(response)
        self.assertDictContainsSubset(response.json, self.response_error)

    def test_add_new_person_with_incorrect_parentsOrChildrenAboard(self):
        self.connexion_error['detail'] = "'20' is not of type 'integer' - 'parentsOrChildrenAboard'"
        person = self.person.copy()
        person['parentsOrChildrenAboard'] = '20'
        response = self.client.post("/people", data=json.dumps(person), content_type='application/json')
        self.assert400(response)
        self.assertDictContainsSubset(response.json, self.connexion_error)

    # list person
    def test_list_people(self):
        response = self.client.get("/people", content_type='application/json')
        self.assert200(response)
        self.assertIsInstance(response.json, list)

    def test_list_people_return_correct_object(self):
        models.Person.load(**self.person).save()
        response = self.client.get("/people", content_type='application/json')
        self.assertEqual(len(response.json), 1)
        self.assertDictContainsSubset(response.json[0], self.person)

    # get person
    def test_get_person(self):
        obj = models.Person.load(**self.person)
        obj.save()
        response = self.client.get(f"/people/{str(obj.uuid)}", content_type='application/json')
        self.assert200(response)
        self.assertDictContainsSubset(response.json, obj.dump())

    def test_get_incorrect_person(self):
        models.Person.load(**self.person).save()
        response = self.client.get(f"/people/{uuid.uuid4()}", content_type='application/json')
        self.assert404(response)

    # put person
    def test_update_person(self):
        obj = models.Person.load(**self.person)
        obj.save()
        response = self.client.put(f"/people/{str(obj.uuid)}", data=json.dumps({'name': 'Alex'}), content_type='application/json')
        self.assert200(response)
        self.assertEqual(response.json['name'], 'Alex')
        obj.refresh()
        self.assertDictContainsSubset(response.json, obj.dump())

    def test_update_incorrect_person(self):
        models.Person.load(**self.person).save()
        response = self.client.get(f"/people/{uuid.uuid4()}", content_type='application/json')
        self.assert404(response)

    def test_update_person_with_empty_data(self):
        obj = models.Person.load(**self.person)
        obj.save()
        response = self.client.get(f"/people/{obj.uuid}", data={}, content_type='application/json')
        self.assert200(response)
        self.assertDictContainsSubset(response.json, obj.dump())

    # delete person
    def test_delete_person(self):
        obj = models.Person.load(**self.person)
        obj.save()
        response = self.client.delete(f"/people/{str(obj.uuid)}", content_type='application/json')
        self.assert200(response)

    def test_delete_incorrect_person(self):
        models.Person.load(**self.person).save()
        response = self.client.get(f"/people/{str(uuid.uuid4())}", content_type='application/json')
        self.assert404(response)


if __name__ == '__main__':
    unittest.main()
