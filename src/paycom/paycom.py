from django.conf import settings
import json
from .exceptions import PaycomException
from paycom.behaviors import check_perform_transaction
from paycom.behaviors import create_transaction
from paycom.behaviors import perform_transaction
from paycom.behaviors import cancel_transaction
from paycom.behaviors import check_transaction
from paycom.behaviors import get_statement
import base64
from .utils import time_now_in_ms


class Paycom(object):
    methods_dict = {
        'CheckPerformTransaction': 'check_perform_transaction',
        'CreateTransaction': 'create_transaction',
        'PerformTransaction': 'perform_transaction',
        'CancelTransaction': 'cancel_transaction',
        'CheckTransaction': 'check_transaction',
        'GetStatement': 'get_statement'
    }

    def __init__(self, request):
        self.key = settings.PAYCOM_SETTINGS["PAYCOM_API_KEY"]
        self.login = settings.PAYCOM_SETTINGS["PAYCOM_API_LOGIN"]
        self.request = request
        body = json.loads(request.body.decode('utf-8'))
        self.method = body['method']
        self.params = body['params']

    def authorize(self):
        if 'HTTP_AUTHORIZATION' not in self.request.META:
            raise PaycomException(
                "UNAUTHENTICATED"
            )

        basic = self.request.META['HTTP_AUTHORIZATION']
        password = str(basic.replace("Basic", "")).strip()
        decoded = base64.b64decode(password)
        # TODO there should be error encode decode without encode
        if self.generate_pair_login_pass().encode() != decoded:
            raise PaycomException(
                "UNAUTHENTICATED"
            )

        return True

    def generate_pair_login_pass(self):
        return self.login + ":" + self.key

    def launch(self):

        self.authorize()

        if self.method == "CheckPerformTransaction":
            return self.check_perform_transaction()
        elif self.method == "CreateTransaction":
            return self.create_transaction()
        elif self.method == "PerformTransaction":
            return self.perform_transaction()
        elif self.method == "CancelTransaction":
            return self.cancel_transaction()
        elif self.method == "CheckTransaction":
            return self.check_transaction()
        elif self.method == "GetStatement":
            return self.get_statement()

    def check_perform_transaction(self):
        behavior = check_perform_transaction(self.params)
        if behavior:
            return {
                "result": {
                    "allow": True
                }
            }

    def create_transaction(self):
        transaction = create_transaction(self.params)
        return {
            "result": {
                "create_time": transaction.create_time,
                "transaction": str(transaction.pk),
                "state": transaction.state,
            }
        }

    def perform_transaction(self):
        transaction = perform_transaction(self.params)
        return {
            "result": {
                "transaction": str(transaction.id),
                "perform_time": transaction.perform_time,
                "state": transaction.state,
            }
        }

    def cancel_transaction(self):
        transaction = cancel_transaction(self.params)
        return {
            "result": {
                "transaction": str(transaction.id),
                "cancel_time": transaction.cancel_time,
                "state": transaction.state,
            }
        }

    def check_transaction(self):
        transaction = check_transaction(self.params)
        if transaction.reason == 0:
            reason = None
        else:
            reason = transaction.reason
        return {
            "result": {
                "create_time": transaction.create_time,
                "perform_time": transaction.perform_time,
                "cancel_time": transaction.cancel_time,
                "transaction": str(transaction.pk),
                "state": transaction.state,
                "reason": reason,
            }
        }

    def get_statement(self):
        items = get_statement(self.params)
        return {
            "result": items
        }

    def change_password(self):
        pass
