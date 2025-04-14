from models.administrador_estagio import AdministradorEstagio

class AdministradorEstagioDAO:
    def __init__(self, conn):
        self.conn = conn

    def checa_admin(self, telegram_id):
        cursor = self.conn.cursor(dictionary=True)

        query = "SELECT * FROM administrador_estagio WHERE telegram_id = %s;"
        cursor.execute(query, (telegram_id,))
        result = cursor.fetchone()
        if result:
            return True
        else:
            return False
