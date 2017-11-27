import os

ADMINS = [('CKM Advisors Pro Bono Team', 'ProBonoTeam@ckmadvisors.com')]
MANAGERS = ADMINS

# # Uncomment and populate with proper connection parameters
# # for enable email sending. EMAIL_HOST_USER should end by @domain.tld
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_USE_SSL = True
# #EMAIL_USE_TLS = True
# EMAIL_HOST = 'mail026-2.exch026.serverdata.net'
# EMAIL_HOST_USER = "iqtoolkit@ckmadvisors.com"
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
# EMAIL_PORT = 465

# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# SERVER_EMAIL = DEFAULT_FROM_EMAIL