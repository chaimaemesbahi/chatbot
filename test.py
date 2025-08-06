from django.db.backends.mysql.base import DatabaseWrapper as BaseDatabaseWrapper

class DatabaseWrapper(BaseDatabaseWrapper):
    def check_database_version_supported(self):
        # Skip the version check
        pass