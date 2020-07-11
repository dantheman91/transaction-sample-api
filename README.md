# Requirements
python -V 3.8.2

# Start App
- Start in home directory
- Create a virtual environment using virtualenvwrapper or your preferred virtualenv
  - mkvirtualenv transaction_app or workon transaction_app
- pip install -r requirements.txt
- cd transaction_app/
- python manage.py migrate
- python manage.py createsuperuser --email <replace_me> --username admin
- python manage.py runserver

# Run Tests


# API Paths
### /create_item/:
    post:
        summary: Creates new item with total amount
        Request Headers:
            Content-Type: application/json
        Request Parameters:
            key: amount (required) 
            value: float
            Sample:
                {
                    "amount": "24.00"
                }
        Response Body Sample:
            {
                "item_id": "31e5d8b6-e41c-4a53-84da-a38e75456972",
                "amount": "24.00"
            }
### /create_transation/:
    post:
        summary: Creates new transaction for existing item
        Request Headers:
            Content-Type: application/json
        Request Parameters:
            key: item_id (required) 
            value: uuid
            key: destination (required)
            value: string
            Sample:
                {
                    "item_id": "31e5d8b6-e41c-4a53-84da-a38e75456972",
	                "destination": "bank_of_the_west"
                }
        Response Body Sample:
            {
                "transaction_id": "d3e86792-5b23-4575-9e78-1a4c93104b25",
                "item_id": "79da0b85-8477-4076-af57-93f99a13f07c",
                "destination": "bank_of_the_west",
                "status": "processing",
                "location": "ORIGINATION_BANK"
            }
### /move_item/:
    post:
        summary: Moves transaction for existing item
        Request Headers:
            Content-Type: application/json
        Request Parameters:
            key: item_id (required) 
            value: uuid
            Sample:
                {
                    "item_id": "79da0b85-8477-4076-af57-93f99a13f07c",
                }
        Response Body Sample:
            {
                "item_id": "79da0b85-8477-4076-af57-93f99a13f07c",
                "location": "ROUTABLE",
                "status": "processing"
            }
### /error_item/:
    post:
        summary: Edits transaction for existing item
        Request Headers:
            Content-Type: application/json
        Request Parameters:
            key: item_id (required) 
            value: uuid
            Sample:
                {
                    "item_id": "79da0b85-8477-4076-af57-93f99a13f07c",
                }
        Response Body Sample:
            {
                "item_id": "79da0b85-8477-4076-af57-93f99a13f07c",
                "location": "ROUTABLE",
                "status": "error"
            }

            




