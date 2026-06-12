import os

from models.orientador_estagio import OrientadorEstagio
from service.config_manager import ConfigManager

class OrientadorEstagioDAO:
    def __init__(self, db_pool):
        self.db_pool = db_pool
    
    def get_orientador_by_id(self, id):
        conn = self.db_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM orientador_estagio WHERE id = %s;"
        cursor.execute(query, (id,))
        result = cursor.fetchone()
        if result:
            orientadorEstagio = OrientadorEstagio.from_dict(result)
        else:
            orientadorEstagio = None

        cursor.close()
        conn.close()

        return orientadorEstagio

    def get_orientador_disponivel(self, raio):
        conn = self.db_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        # Seleciona entre os orientadores disponíveis o próximo da fila
        querySorteio = f"""
        SELECT * FROM orientadores_ativos
        WHERE total_alunos_ativos <= ( SELECT MIN(total_alunos_ativos) + {raio} FROM orientadores_ativos ) AND disponivel = 1
        ORDER BY RAND(UNIX_TIMESTAMP())
        LIMIT 1;
        """
        cursor.execute(querySorteio)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return OrientadorEstagio.from_dict(result)
        else:
            return None

    def set_orientadores_disponiveis(self):
        conn = self.db_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("UPDATE orientador_estagio SET disponivel = 1")
        conn.commit()

        cursor.close()
        conn.close()

    def set_orientador_indisponivel(self, id_orientador):
        conn = self.db_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        queryInativa = "UPDATE orientador_estagio SET disponivel = %s WHERE id = %s;"
        valores = (0, id_orientador)
        cursor.execute(queryInativa, valores)
        conn.commit()

        cursor.close()
        conn.close()

    def lista_orientadores(self, query):
        try:
            conn = self.db_pool.get_connection()

            if conn.is_connected():
                cursor = conn.cursor(dictionary=True)
                cursor.execute (query)
                msg = ""
                total = 0
                for linha in cursor.fetchall():
                    total = total + 1
                    msg = msg + f"{total}. {linha['nome']} ({linha['total_alunos_ativos']} alunos)\n"

                if total == 0:
                    msg = "Não há orientadores disponíveis"

        except Error as e:
            msg = f"Erro: {e}"
    
        finally:
            # Fechamento da conexão e do cursor
            if conn.is_connected():
                cursor.close()
                conn.close()

            return [msg]

    def lista_orientadores_disponiveis(self, raio):
        query = f"""
        SELECT * FROM orientadores_ativos
        WHERE total_alunos_ativos <= ( SELECT MIN(total_alunos_ativos) + {raio} FROM orientadores_ativos ) AND disponivel = 1
        """
        msg = 'DISPONIVEIS PARA SORTEIO\n' + self.lista_orientadores(query)[0]

        query = f"""
        SELECT * FROM orientadores_ativos
        WHERE total_alunos_ativos <= ( SELECT MIN(total_alunos_ativos) + {raio} FROM orientadores_ativos ) AND disponivel = 0
        """
        msg = msg + '\nSORTEADOS NESTA RODADA\n' + self.lista_orientadores(query)[0]

        query = f"""
        SELECT * FROM orientadores_ativos
        WHERE total_alunos_ativos > ( SELECT MIN(total_alunos_ativos) + {raio} FROM orientadores_ativos )
        """
        msg = msg + f'\nMAIS ALUNOS QUE O MÁXIMO (raio = {raio})\n' + self.lista_orientadores(query)[0]

        return [msg]

    def lista_orientadores_afastados(self):
        query = """
        SELECT oe.* FROM orientador_estagio oe
        WHERE NOT EXISTS ( SELECT 1 FROM orientadores_ativos oa WHERE oa.id = oe.id ) AND ativo = 1;
        """
        return self.lista_orientadores(query)

    def lista_orientadores_inativos(self):
        query = "SELECT * FROM orientador_estagio WHERE ativo = 0"
        return self.lista_orientadores(query)

