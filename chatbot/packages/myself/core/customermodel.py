from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from chatbot.model import Model

"""
{
	"customer_id" : str
	"currency": "EUR",
    "cart": [
        {"product_id": str},
        {"product_id": str},
        ....
    ]
}
"""


class CustomerModel(Model):
    def __init__(self, config):
        super().__init__(config)

    def add_customer(self, customer_info: dict):
        if not isinstance(customer_info, dict):
            raise InvalidCustomerInfoError("Provided customer info is invalid.")

        for value in tuple(customer_info.values()):
            if value is None:
                raise InvalidCustomerInfoError("One of the customer info is empty.")

        if self.db_type == "MONGODB":
            customers = self.db.customers
            unique_identifier = "customer_id"

            if "customers" not in self.db.list_collection_names():
                try:
                    customers.create_index([(unique_identifier, ASCENDING)], name=unique_identifier, unique=True)
                except Exception as error:
                    raise Exception(f"Failed to create index \"{unique_identifier}\". {type(error).__name__} {error}")
            else:
                try:
                    customers.insert_one({
                        unique_identifier: customer_info.get("customer_id"),
                        "currency": customer_info.get("currency"),
                        "cart": []
                    })
                except DuplicateKeyError:
                    print(f"A customer with id {customer_info.get('customer_id')} already exists.")
        else:
            raise UnsupportedDBTypeError

    def remove_customer(self, customer_id):
        if self.db_type == "MONGODB":
            customers = self.db.customers
            customers.delete_one({
                "customer_id": customer_id
            })
        else:
            raise UnsupportedDBTypeError

    def update_customer(self, customer_id, field, new_value):
        if self.db_type == "MONGODB":
            customers = self.db.customers

            customer_query = {"customer_id": customer_id}
            new_assignment = {"$set": {field: new_value}}

            customers.update_one(customer_query, new_assignment)
        else:
            raise UnsupportedDBTypeError

    def get_customer(self, customer_id):
        if self.db_type == "MONGODB":
            customers = self.db.customers

            customer_query = {"customer_id": customer_id}
            return customers.find_one(customer_query)
        else:
            raise UnsupportedDBTypeError

    def get_customers(self):
        if self.db_type == "MONGODB":
            customers = self.db.customers

            return list(customers.find())
        else:
            raise UnsupportedDBTypeError


class InvalidCustomerInfoError(BaseException):
    """Raised when a customer info is invalid"""


class UnsupportedDBTypeError(BaseException):
    """Raised if the current database type is not (yet) supported"""
