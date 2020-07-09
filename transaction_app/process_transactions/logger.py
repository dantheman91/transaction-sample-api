import json

from .models import ItemLog


class APILogger:

    def __init__(self):
        self.request_and_response_logs = []

    def log_request(self, request):
        self.add_to_logging({
            'request': {
                'request_data': request.data,
                'request_path': request.get_full_path()
            }
        })

    def log_response(self, response_data, http_code):
        self.add_to_logging({
            'response': response_data,
            'http_code': http_code
        })
        print(self.request_and_response_logs)
        try:
            requests_and_responses = json.dumps(self.request_and_response_logs)
        # If attempting to convert to json fails, just write to db and log error.
        except Exception as error:
            print(f'Error converting to JSON: {error}')
            requests_and_responses = self.request_and_response_logs
        log = ItemLog(request_and_response_body=requests_and_responses)
        try:
            log.save()
        except Exception as e:
            print('Unable to save to database')
            print(e)

    def add_to_logging(self, logging_object):
        print(logging_object)
        print(self.request_and_response_logs)
        self.request_and_response_logs.append(logging_object)