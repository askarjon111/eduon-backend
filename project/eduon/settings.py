import os
from datetime import timedelta
from celery.schedules import crontab
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SECRET_KEY = '(@s5no*3@a7s-h5rb+*sy0e(#zwdhliu96zo@22qmn)utsc9y8'

from corsheaders.defaults import default_methods

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
LOGGING_CONFIG = None
# Application definition
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

INSTALLED_APPS = [
    'adminlte3',
    'adminlte3_theme',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home.apps.HomeConfig',
    'backoffice.apps.BackofficeConfig',
    'rest_framework',
    'rest_framework_simplejwt',
    'paycomuz',
    'clickuz',
    'simplejwt',
    'paycom',
    'uniredpay',
    'corsheaders',
    'quiz',
    'rest_framework.authtoken',
    'django_filters',
    'background_task',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'eduon.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'eduon.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'backoffice',
#         'USER': 'backoffice',
#         'PASSWORD': 'Pa$$w0rd',
#         'HOST': '127.0.0.1',
#         'PORT': '3306',
#    }
# }


CLICK_SETTINGS = {
    'service_id': '16632',
    'merchant_id': '12015',
    'secret_key': 'imOUAe56q2Zr8r',
    'merchant_user_id': '17661'
}

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'OPTIONS': {
                'read_default_file': '/var/www/eduon_backend/project/mysql.cnf',
            },
        }
    }

# if DEBUG:
#     DATABASES = {
#         'default': {
#             "ENGINE": 'django.db.backends.sqlite3',
#             "NAME": os.path.join(BASE_DIR, "db.sqlite3")
#         }
#     }
# else:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.mysql',
#             'OPTIONS': {
#                 'read_default_file': '/var/www/eduon_backend/project/mysql.cnf',
#             },
#         }
#     }

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'uz-UZ'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_L10N = True

USE_TZ = True
# CKEDITOR_UPLOAD_PATH = "uploads/"
# CKEDITOR_IMAGE_BACKEND = 'pillow'
# CKEDITOR_CONFIGS = {
#     'default': {
#         'toolbar': 'full',
#         'height': 600,
#         'width': "100%",
#     },
# }

PAYCOM_SETTINGS = {
    # "PAYCOM_API_KEY": "DVFmMkVmK9115Q&YV0&y?VPMHKub%&sYJvTq",
    "PAYCOM_API_KEY": "ZrTHJGJW05KjFX73IUWArAfyDDOscxO#e8MZ",
    "PAYCOM_API_LOGIN": "Paycom",
    "PAYCOM_ENV": False,  # test host
    "TOKEN": "token",  # token
    "SECRET_KEY": "password",  # password
    "ACCOUNTS": {
        "KEY_1": "order_id",
        "KEY_2": None  # or "type"
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'simplejwt.permissions.JwtPermission',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'simplejwt.authentication.JWTAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    "EXCEPTION_HANDLER": "eduon.utils.custom_exception_handler",
    'DEFAULT_FILTER_BACKENDS': 
        [
            'django_filters.rest_framework.DjangoFilterBackend',
        ],
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=200),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=15),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}
DJANGORESIZED_DEFAULT_SIZE = [1920, 1080]
DJANGORESIZED_DEFAULT_QUALITY = 75
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_FORCE_FORMAT = 'JPEG'
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {'JPEG': ".jpg"}
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/


CORS_ALLOW_CREDENTIALS = True

CORS_ORIGIN_WHITELIST = [
    # Front end
    "https://eduon.uz",
    "https://speaker.eduon.uz",
    "http://157.230.10.27:3001",
    # Islom front end
    "http://192.168.100.247:3000",
    "http://192.168.100.247:3001",
    "http://192.168.100.36:3000",
    "http://192.168.100.36:3001",
    "http://192.168.43.115:3000",
    "http://192.168.43.115:3001",
    "http://192.168.100.199:3000",
    "http://192.168.100.199:3001",
    # Ibrohim
    "http://192.168.10.203:3000",
    "http://192.168.10.203:3001",
    # ASKAR
    "http://192.168.1.40:8000",
    "http://192.168.1.40:5000"
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_URLS_REGEXES = [
    r'^/api1234/.*$',
    r'^/api-web/.*$',
]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_METHODS = list(default_methods) + [
    'POKE',
]
# CORS_ORIGIN_WHITELIST = [
#     "http://127.0.0.1:8000",
# ]
CORS_PREFLIGHT_MAX_AGE = 86400

# CORS_ORIGIN_WHITELIST = (
#    "http://142.93.60.60/"
# )
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SMS_EMAIL = 'ulugbekr2028@gmail.com'
SMS_SECRET_KEY = 'VUp0VI4q7Q3c7xffTgfSbVnbLZiStjP5nK4QHnNx'
SMS_BASE_URL = 'http://notify.eskiz.uz'
SMS_TOKEN = ''
SMS_TOKEN_GLOBAL = ''
SMS_CLIENT_ID = "R0lTd27bfzySEYrf"
SMS_SECRET_KEY_GLOBAL = 'QvvCvbrDMjYXbTMiV1VQ9jfODtVYFiiP'
SMS_BASE_URL_GLOBAL = 'https://auth.sms.to'
SMS_REGISTER_TEXT = 'Assalomu alaykum Eduon.uz saytimizga xush kelibsiz! Tasdiqlash kodi: '
SMS_ACCEPT_TEXT = 'Tabriklaymiz!!! Moderator tomonidan EduOn spiker akauntingiz faollashtirildi. https://speaker.eduon.uz/'
SMS_REJECT_TEXT = "Sizning profilingiz ma'lum sabablarga ko'ra aktivlashtirilmadi! https://speaker.eduon.uz/"

UNICOIN_LOGIN = "eduon"
UNICOIN_PASSWORD = "SDqwd$se6l8Gp4ASMWmmhTxwO98Fiub9"
UNICOIN_HOST_UZCARD = "https://core.unired.uz/api/v1/unired"
UNICOIN_HOST_HUMO = "https://core.unired.uz/api/v1/humo"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'info@eduon.uz'
EMAIL_HOST_PASSWORD = 'ksscweqfnzljohty'

UNIRED_LOGIN = "Eduon"
UNIRED_PASSWORD = "Nr9WAVeS1TjV"
UNIRED_WALLET_URL = "https://wallet.unired.uz"
UNIRED_ACCOUNT_BALANCE = ""

UZCARD_MERCHANT_ID = '90489428'
UZCARD_TERMINAL_ID = '92415924'

HUMO_MERCHANT_ID = '011860000118613'
HUMO_TERMINAL_ID = '23610C9U'


CRONJOBS = [
    ('* * * * *', 'backoffice.cron.set_discount_to_random_courses',
     '>> /home/work/EduOnBack/project/cron.log'),
    ('* * * * *', 'backoffice.cron.delete_discount',
     '>> /home/work/EduOnBack/project/cron.log'),
    ('* * * * *', 'backoffice.cron.test_cron_function',
     '>> /home/work/EduOnBack/project/cron.log')
]

# CELERY STUFF
# BROKER_URL = 'redis://localhost:6379'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Tashkent'
CELERY_BEAT_SCHEDULE = {
    "set_discount_to_random_courses": {
        "task": "set_discount_to_random_courses",
        "schedule": crontab(hour=13, day_of_week=0)
    },
    "delete_discount_task": {
        "task": "delete_discount_task",
        "schedule": crontab()
    },
    "print_test": {
        "task": "print_test",
        "schedule": crontab()
    }
}