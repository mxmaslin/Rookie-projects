import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_PATH = os.path.join(BASE_DIR, 'bullion/static')

STATICFILES_DIRS = (
    STATIC_PATH,
)

# Host for sending e-mail.
EMAIL_HOST = 'smtp.yandex.ru'

# Port for sending e-mail.
EMAIL_PORT = 465

# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = 'zapzarap@yandex.ru'
EMAIL_HOST_PASSWORD = 'mymomisabitch'
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
