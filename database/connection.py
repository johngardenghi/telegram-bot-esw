from mysql.connector import Error, pooling

class DatabasePool:
    def __init__(self, db_config, pool_name="eswbot", pool_size=5):
        self.pool = pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            pool_reset_session=True,
            **db_config
        )

    def get_connection(self):
        return self.pool.get_connection()