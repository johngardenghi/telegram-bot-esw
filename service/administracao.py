from dao import AdministradorEstagioDAO

import mysql.connector
from mysql.connector import Error

class Administracao:

    @staticmethod
    def eh_admin(db_pool, user_id):
        eh_admin = False

        try:
            conn = db_pool.get_connection()
            administradorEstagioDAO = AdministradorEstagioDAO(conn)
            eh_admin = administradorEstagioDAO.checa_admin(user_id)

        except Error as e:
            print (f"Erro: {e}")
    
        finally:
            if conn.is_connected():
                conn.close()

            return eh_admin
