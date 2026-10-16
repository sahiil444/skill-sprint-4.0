from pydantic import BaseModel

class Address(BaseModel):

    city: str
    state: str
    pin: str

class Patient(BaseModel):

    name: str
    gender: str = 'Male'
    age: int
    address: Address

address_dict = {'city': 'gurgaon', 'state': 'haryana', 'pin': '122001'}

address1 = Address(**address_dict)

patient_dict = {'name': 'nitish', 'age': 35, 'address': address1}

patient1 = Patient(**patient_dict)

temp1 = patient1.model_dump_json(include=['name','age'])
temp2 = patient1.model_dump_json(exclude=['name'])
temp3 = patient1.model_dump()
temp = patient1.model_dump(exclude_unset=True)

print(temp1)
print(type(temp1))

print(temp2)
print(type(temp2))

print(temp3)
print(type(temp3))

print(temp)
print(type(temp))