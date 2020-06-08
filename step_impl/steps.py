from step_impl.helpers.Base_Test import Base_Test

from getgauge.python import step
from getgauge.python import data_store as ds

class Pet_Tests(Base_Test):

    @step("create pet <name> <age> <owner>")
    def create_new_pet(self, name, age, owner):
        r = ds.spec.api.tutorial5.post(body={
            'name': name,
            'age': age,
            'owner': owner
        })
        ds.spec.pet_id = r.json()['pet_id']
        assert r.status_code == 201

    @step("check if pet was created")
    def assert_new_pet(self):
        r = ds.spec.api.tutorial5.get()
        assert r.status_code == 200
        pets = r.json()
        assert len(pets) > 0
        assert ds.spec.pet_id in [pet['pet_id'] for pet in pets]

    @step("update last pet <name> <age> <owner>")
    def updated_last_created_pet(self, name, age, owner):
        id = ds.spec.pet_id
        r = ds.spec.api.tutorial5(id).put(body={
            'name': name,
            'age': age,
            'owner': owner
        })
        assert r.status_code == 200
        r = r.json()
        assert r['name'] == name, f"name was {r['name']}, expected: {name}"
        assert r['age'] == int(age), f"age was {r['age']}, expected: {age}"
        assert r['owner'] == owner, f"owner was {r['owner']}, expected: {owner}"

    @step("delete last created pet")
    def delete_last_pet(self):
        r = ds.spec.api.tutorial5.delete(ds.spec.pet_id)
        assert r.status_code == 204
