from datetime import datetime, timezone
from home.models import PaymentHistory
from paycom.models import Transaction
from paycom.exceptions import PaycomException
from paycom.serializers import TransactionSerializer


def get_order(params):
    order_id = params['account'].get('order_id', False)
    try:
        return PaymentHistory.objects.get(id=order_id)
    except PaymentHistory.DoesNotExist:
        raise PaycomException("ORDER_NOT_FOUND")


def get_transaction(params):
    try:
        return Transaction.objects.get(transaction_id=params.get("id", False))
    except Transaction.DoesNotExist:
        raise PaycomException("TRANSACTION_NOT_FOUND")


def transaction_status(params):
    order_id = params['account'].get('order_id', False)
    try:
        transaction = Transaction.objects.get(order_id=order_id)  # ---> this may change also
        if transaction.state == 2:
            raise PaycomException("ORDER_ALREADY_PAYED")
        elif transaction.state == -1:
            raise PaycomException("ORDER_CANCELLED")
        else:
            raise PaycomException("ORDER_WAITING")
    except Transaction.DoesNotExist:
        pass


def check_prices(params):
    order = get_order(params)  # ---> i may change this
    payed_amount = params.get('amount', False)
    if order.summa*100 != payed_amount:
        raise PaycomException("AMOUNTS_NOT_EQUAL")
    return True


def new_transaction(params):
    try:
        return Transaction.objects.get(transaction_id=params.get("id", False))
    except Transaction.DoesNotExist:
        check_perform_transaction(params)

        current_timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
        transaction_id = params.get("id", False)
        state = 1
        time = params.get("time", False)
        amount = params.get("amount", False)
        order_id = params['account'].get("order_id", False)
        account = PaymentHistory.objects.get(id=order_id).user.id
        transaction = Transaction.objects.create(transaction_id=transaction_id, state=state, time=time, amount=amount,
                                                 account=account, order_id=order_id, create_time=current_timestamp)
        return transaction


def check_time_limit(time):
    current_timestamp = datetime.now(timezone.utc).timestamp()
    if time - current_timestamp >= Transaction.TIMEOUT_LIMIT:
        raise PaycomException("CANNOT_PERFORM_OPERATION")
    return True


def check_perform_transaction(params):
    get_order(params)  # ---> this may change
    check_prices(params)
    # check if given order has already transaction or cancelled transaction
    transaction_status(params)
    return True


def create_transaction(params):
    # create new transaction
    transaction = new_transaction(params)

    # check the state of transaction
    if transaction.state == 1:
        if transaction.is_timeout():
            transaction.state = -1
            transaction.reason = 4
            transaction.save()
            raise PaycomException("CANNOT_PERFORM_OPERATION")
        else:
            return transaction
    else:
        raise PaycomException("CANNOT_PERFORM_OPERATION")


def perform_transaction(params):
    current_timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    transaction = get_transaction(params)
    if transaction.state == 1:
        if transaction.is_timeout():
            transaction.state = -1
            transaction.reason = 4
            transaction.save()
            raise PaycomException("CANNOT_PERFORM_OPERATION")
        else:
            transaction.perform_time = current_timestamp
            transaction.state = 2
            payment = PaymentHistory.objects.get(id=transaction.order_id)
            payment.status = 2
            user = payment.user
            user.cash += payment.summa
            payment.save()
            user.save()
            transaction.save()
            return transaction
    elif transaction.state == 2:
        return transaction
    else:
        raise PaycomException("CANNOT_PERFORM_OPERATION")


def cancel_transaction(params):
    """User can not cancel transaction"""
    raise PaycomException("CANNOT_PERFORM_OPERATION")


def check_transaction(params):
    transaction = get_transaction(params)
    return transaction


def get_statement(params):
    start_time = params.get("from", False)
    end_time = params.get("to", False)
    transactions = Transaction.between(from_date=start_time, to_date=end_time)
    serializer = TransactionSerializer(transactions, many=True)
    return serializer.data
