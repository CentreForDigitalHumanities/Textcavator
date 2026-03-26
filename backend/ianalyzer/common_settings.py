'''
Common settings between development and production environments.
Values here should be imported in settings.py
'''

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'livereload',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'revproxy',
    'users',
    'addcorpus',
    'api',
    'es',
    'corpora',
    'indexing',
    'visualization',
    'download',
    'wordmodels',
    'media',
    'tag',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'djangosaml2.middleware.SamlSessionMiddleware',
]

ROOT_URLCONF = 'ianalyzer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'ianalyzer.wsgi.application'

# DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'password': '3/minute',
        'registration': '5/minute',
        'download': '5/minute',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
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

ACCOUNT_USER_DISPLAY = lambda user: user.username.replace(".", "\u2024")

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Amsterdam'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

# Authentication
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True
AUTH_USER_MODEL = 'users.CustomUser'

REST_AUTH = {
    'USER_DETAILS_SERIALIZER': 'users.serializers.CustomUserDetailsSerializer',
    'REGISTER_SERIALIZER': 'users.serializers.CustomRegistrationSerializer',
    'OLD_PASSWORD_FIELD_ENABLED': True,
    'LOGOUT_ON_PASSWORD_CHANGE': False,
}

LOGO_LINK = 'https://dhstatic.hum.uu.nl/logo-cdh/png/UU_CDH_logo_EN_whiteFC.png'

NLTK_DATA_PATH = os.path.join(BASE_DIR, 'addcorpus', 'stopword_data', 'nltk_data')

DEFAULT_CORPUS_IMAGE = os.path.join(BASE_DIR, 'addcorpus', 'images', 'default.png')

# Celery

CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['json', 'pickle']
