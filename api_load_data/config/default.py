PROPAGATE_EXCEPTIONS = True
# Database configuration
USER_DB = 'postgres'
PASS_DB = 'root'
URL_DB = 'localhost'
NAME_DB = 'challenge'

SQLALCHEMY_DATABASE_URI = f'postgresql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SHOW_SQLALCHEMY_LOG_MESSAGES = False
ERROR_404_HELP = False