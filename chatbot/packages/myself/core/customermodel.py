from chatbot.model import BaseModel


class CustomerModel(BaseModel):
    """
    This model will interact with the "customers" collection which have the following document model :

    {
        "customer_id" : str
        "currency": "EUR",
        "cart": [
            {"product_id": str, "variant_id": str, "quantity": int},
            {"product_id": str, "variant_id": str, "quantity": int},
            ....
        ]
    }
    """
    def __init__(self):
        super().__init__(
            collection="customers",
            base_document={
                "customer_id": "0000000000000000",
                "currency": "EUR",
                "cart": []
            },
            index="customer_id"
        )

    def add_customer(self, customer_id: str, currency: str):
        self.collection.insert_one({
            "customer_id": customer_id,
            "currency": currency,
            "cart": []
        })

    def get_customer(self, customer_id: str):
        return self.collection.find_one({"customer_id": customer_id})

    def get_customers(self):
        return list(self.collection.find())

    def update_customer(self, customer_id: str, **new_assignments):
        customer_query = {"customer_id": customer_id}
        new_value = {
            "$set": {}
        }
        for key, value in new_assignments.items():
            new_value["$set"][key] = value
        self.collection.update_one(customer_query, new_value)

    def remove_customer(self, customer_id: str):
        self.collection.delete_one({"customer_id": customer_id})
