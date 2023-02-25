class PaycomException(Exception):
    code = 0
    message = ""

    ERRORS_CODES = {
        "NOT_ALLOWED_METHOD": -32300,
        "JSON_PARSE": -32700,
        "WRONG_REQUEST_PARAMS": -32600,
        "METHOD_NOT_EXIST": -32601,
        "UNAUTHENTICATED": -32504,
        "SYSTEM_ERROR": -32400,
        "CANNOT_PERFORM_OPERATION": -31008,

        "AMOUNTS_NOT_EQUAL": -31001,
        "TRANSACTION_NOT_FOUND": -31003,
        "ORDER_NOT_FOUND": -31050,
        "ORDER_WAITING": -31099,
        "ORDER_ALREADY_PAYED": -31051,
        "ORDER_CANCELLED": -31052
    }
    ERROR_MESSAGES = {
        "UNAUTHENTICATED": {
            "ru": "Не авторизован",
            "uz": "Avtorizasiyadan o'tmagan",
            "en": "Unauthenticated",
        },
        "AMOUNTS_NOT_EQUAL": {
            "ru": "Суммы не совпадают",
            "uz": "To'lov summalari mos kelmadi",
            "en": "Amounts not equal"
        },
        "CANNOT_PERFORM_OPERATION": {
            "ru": "Невозможно выполнить операцию.",
            "uz": "Operasiyani bajarib bo'lmadi",
            "en": "Can't perform operation"
        },
        "TRANSACTION_NOT_FOUND": {
            "ru": "Транзакция не найдена",
            "uz": "Tranzaksiya topilmadi",
            "en": "Transaction not found"
        },
        "NOT_ALLOWED_METHOD": {
            "ru": "Метод не доступен",
            "uz": "Metoddan foydalanish mumkin emas ",
            "en": "Not allowed method",
        },
        "JSON_PARSE": {
            "ru": "Ошибка при парсинге JSON",
            "uz": "JSON ni parse qilishdagi xatolik",
            "en": "Json parse error"
        },
        "WRONG_REQUEST_PARAMS": {
            "ru": "Были переданы не правильные параметры",
            "uz": "Noto'g'ri parametrlar jo'natildi",
            "en": "Wrong request params"
        },
        "METHOD_NOT_EXIST": {
            "ru": "Метод не найден",
            "uz": "Metod topilmadi",
            "en": "Method not exists"
        },
        "SYSTEM_ERROR": {
            "ru": "Системная ошибка",
            "uz": "Tizim xatoligi",
            "en": "System error"
        },
        "ORDER_NOT_FOUND": {
            "ru": "Заказ не найден",
            "uz": "Buyurtma topilmadi",
            "en": "Order not found"
        },
        "ORDER_ALREADY_PAYED": {
            "ru": "Заказ уже проплачен",
            "uz": "Buyurtma to'langan",
            "en": "Order already payed"
        },
        "ORDER_CANCELLED": {
            "ru": "Заказ отменен",
            "uz": "Buyurtma bekor qilingan",
            "en": "Order cancelled"
        },
        "ORDER_WAITING": {
            "uz": "Buyurtma tolovi amalga oshirilyapti",
            "ru": "Платеж на этот данный момент В процессе",
            "en": "Order payment is already being proccessштп"

        }
    }

    def __init__(self, code):
        self.code = code
        self.message = self.ERROR_MESSAGES[code]
