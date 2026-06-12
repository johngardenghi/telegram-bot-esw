import mysql.connector
from mysql.connector import Error

class AdministracaoService:
    pass

    def __init__(self, administrador_estagio_dao):
        self.administrador_estagio_dao = administrador_estagio_dao

    def eh_admin(self, user_id):
        return self.administrador_estagio_dao.checa_admin(user_id)

    def usuarios_admin(self):
        return self.administrador_estagio_dao.usuarios_admin()
