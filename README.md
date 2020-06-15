# Requirements
python -V 3.8.2

# Start App
- Create a virtual environment using virtualenvwrapper or your preferred virtualenv
  - mkvirtualenv transaction_app or workon transaction_app
- pip install -r requirements.txt
- python manage.py migrate
- python manage.py createsuperuser --email admin@example.com --username admin
- cd transaction_app/
- python manage.py migrate
- python manage.py createsuperuser --email <replace_me> --username admin

