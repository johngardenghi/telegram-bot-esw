from models.orientador_estagio import OrientadorEstagio

class OrientadorEstagioDAO:
    def __init__(self, conn):
        self.conn = conn

    def seleciona_orientadores_disponiveis(self):
        cursor = self.conn.cursor(dictionary=True)

        # Seleciona entre os orientadores disponíveis o próximo da fila
        querySorteio = """
            SELECT * FROM (
                SELECT * FROM orientador_estagio
                WHERE CURDATE() NOT BETWEEN indisponivel_inicio AND indisponivel_fim OR
                indisponivel_inicio IS NULL OR
                indisponivel_fim IS NULL
            ) AS orientadores_ativos
            WHERE total_alunos_ativos <= (
                SELECT MIN(total_alunos_ativos) + 5 FROM orientador_estagio
                WHERE CURDATE() NOT BETWEEN indisponivel_inicio AND indisponivel_fim OR
                indisponivel_inicio IS NULL OR
                indisponivel_fim IS NULL
                ) AND disponivel = 1
            ORDER BY RAND(UNIX_TIMESTAMP())
            LIMIT 1;
        """
        cursor.execute(querySorteio)
        result = cursor.fetchone()

        if result:
            orientadorEstagio = OrientadorEstagio.from_dict(result)
        else:
            # Se não houve selecionados, pode ser que os ativos estejam todos 1. Precisa ativar todos novamente
            queryReativa = "UPDATE orientador_estagio SET disponivel = 1;"
            cursor.execute(queryReativa)
            self.conn.commit()

            cursor.execute(querySorteio)
            result = cursor.fetchone()
            if result:
                orientadorEstagio = OrientadorEstagio.from_dict(result)
            else:
                orientadorEstagio = None
        
        if orientadorEstagio is not None:
            queryInativa = "UPDATE orientador_estagio SET disponivel = %s WHERE id = %s;"
            valores = (0, orientadorEstagio.id)
            cursor.execute(queryInativa, valores)
            self.conn.commit()

        cursor.close()

        return orientadorEstagio
    
    def get_orientador_by_id(self, id):
        cursor = self.conn.cursor(dictionary=True)

        query = "SELECT * FROM orientador_estagio WHERE id = %s;"
        cursor.execute(query, (id,))
        result = cursor.fetchone()
        if result:
            orientadorEstagio = OrientadorEstagio.from_dict(result)
        else:
            orientadorEstagio = None

        cursor.close()

        return orientadorEstagio
