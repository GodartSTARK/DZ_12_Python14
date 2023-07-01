from collections import UserDict
from datetime import datetime
import re
import json


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def __iter__(self):
        return self.iterator()

    def iterator(self, n=1):
        keys = list(self.data.keys())
        num_records = len(keys)
        current_index = 0

        while current_index < num_records:
            yield [self.data[keys[i]] for i in range(current_index, min(current_index + n, num_records))]
            current_index += n
        
    def save_to_file(self, filename):
        data = {
            'records': [
                {
                    'name': record.name.value,
                    'phones': [phone.value for phone in record.phones],
                    'birthday': record.birthday.value if record.birthday else None
                }
                for record in self.data.values()
            ]
        }
        with open(filename, 'w') as file:
            json.dump(data, file)

    def load_from_file(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            self.data = {}
            for record_data in data['records']:
                record = Record(Name(record_data['name']), Birthday(record_data['birthday']))
                for phone_value in record_data['phones']:
                    record.add_phone(Phone(phone_value))
                self.add_record(record)

    def search_contacts(self, query):
        results = []
        for record in self.data.values():
            if (
                query in record.name.value
                or any(query in phone.value for phone in record.phones)
                or (record.birthday and query in record.birthday.value)
            ):
                results.append(record)
        return results


class Record:
    def __init__(self, name, birthday=None):
        self.name = name
        self.phones = []
        self.birthday = birthday

    def add_phone(self, phone):
        if isinstance(phone, Phone):
            self.phones.append(phone)
        else:
            raise ValueError("Invalid phone object")

    def remove_phone(self, phone):
        if phone in self.phones:
            self.phones.remove(phone)
        else:
            raise ValueError("Phone not found")

    def edit_phone(self, old_phone, new_phone):
        if old_phone in self.phones:
            index = self.phones.index(old_phone)
            self.phones[index] = new_phone
        else:
            raise ValueError("Phone not found")

    def set_birthday(self, birthday):
        if isinstance(birthday, Birthday):
            self.birthday = birthday
        else:
            raise ValueError("Invalid birthday object")

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.date.today()
            next_birthday = datetime.date(today.year, self.birthday.month, self.birthday.day)
            if today > next_birthday:
                next_birthday = datetime.date(today.year + 1, self.birthday.month, self.birthday.day)
            days_left = (next_birthday - today).days
            return days_left
        else:
            return None

    @property
    def name_value(self):
        return self.name.value

    @property
    def birthday_value(self):
        return self.birthday.value if self.birthday else None

    @birthday_value.setter
    def birthday_value(self, value):
        if value is None or isinstance(value, Birthday):
            self.birthday = value
        else:
            raise ValueError("Invalid birthday object")


class Field:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value


class Name(Field):
    pass


class Phone(Field):
    @Field.value.setter
    def value(self, new_value):
        if self.validate_phone(new_value):
            self._value = new_value
        else:
            raise ValueError("Invalid phone number")

    @staticmethod
    def validate_phone(value):
        pattern = r"^\+\d{1,3}\d{9}$"
        return re.match(pattern, value) is not None


class Birthday(Field):
    @Field.value.setter
    def value(self, new_value):
        if self.validate_birthday(new_value):
            self._value = new_value
        else:
            raise ValueError("Invalid birthday")

    @staticmethod
    def validate_birthday(value):
        pattern = r"^\d{2}\.\d{2}\.\d{4}$"
        return re.match(pattern, value) is not None
