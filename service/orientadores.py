import os

import mysql.connector
from mysql.connector import Error

class Orientadores:

    @staticmethod
    def lista_orientadores(db_pool, query):
        try:
            conn = db_pool.get_connection()

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


    @staticmethod
    async def disponiveis_sorteio(db_pool):
        query = f"""
        SELECT * FROM orientadores_ativos
        WHERE total_alunos_ativos <= ( SELECT MIN(total_alunos_ativos) + {os.environ.get("ESWBOT_RAIO")} FROM orientadores_ativos ) AND disponivel = 1
        """
        msg = Orientadores.lista_orientadores(db_pool, query)[0]

    @staticmethod
    async def disponiveis(db_pool):
        raio = os.environ.get("ESWBOT_RAIO")

        query = f"""
        SELECT * FROM orientadores_ativos
        WHERE total_alunos_ativos <= ( SELECT MIN(total_alunos_ativos) + {raio} FROM orientadores_ativos ) AND disponivel = 1
        """
        msg = 'DISPONIVEIS PARA SORTEIO\n' + Orientadores.lista_orientadores(db_pool, query)[0]

        query = f"""
        SELECT * FROM orientadores_ativos
        WHERE total_alunos_ativos <= ( SELECT MIN(total_alunos_ativos) + {raio} FROM orientadores_ativos ) AND disponivel = 0
        """
        msg = msg + '\nSORTEADOS NESTA RODADA\n' + Orientadores.lista_orientadores(db_pool, query)[0]

        query = f"""
        SELECT * FROM orientadores_ativos
        WHERE total_alunos_ativos > ( SELECT MIN(total_alunos_ativos) + {raio} FROM orientadores_ativos )
        """
        msg = msg + f'\nMAIS ALUNOS QUE O MÁXIMO (raio = {raio})\n' + Orientadores.lista_orientadores(db_pool, query)[0]

        return [msg]

    @staticmethod
    async def afastados(db_pool):
        query = """
        SELECT oe.* FROM orientador_estagio oe
        WHERE NOT EXISTS ( SELECT 1 FROM orientadores_ativos oa WHERE oa.id = oe.id ) AND ativo = 1;
        """
        return Orientadores.lista_orientadores(db_pool, query)

    @staticmethod
    async def inativos(db_pool):
        query = "SELECT * FROM orientador_estagio WHERE ativo = 0"
        return Orientadores.lista_orientadores(db_pool, query)
