from models.solicitacao_estagio import SolicitacaoEstagio

class SolicitacaoEstagioDAO:
    def __init__(self, db_pool):
        self.db_pool = db_pool

    def insere_solicitacao(self, solicitacao_estagio):
        conn = self.db_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "INSERT INTO solicitacao_estagio (orientador, aluno, telegram_id, data_hora, email_aluno, telefone_aluno) VALUES (%s, %s, %s, %s, %s, %s);"
        values = (
            solicitacao_estagio.orientador,
            solicitacao_estagio.aluno,
            solicitacao_estagio.telegram_id,
            solicitacao_estagio.data_hora,
            solicitacao_estagio.email_aluno,
            solicitacao_estagio.telefone_aluno
        )
        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()


    def verifica_solicitacao_ativa(self, telegram_id):
        conn = self.db_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM solicitacao_estagio WHERE telegram_id = %s AND data_hora >= NOW() - INTERVAL 1 MONTH;"
        cursor.execute(query, (telegram_id,))

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return SolicitacaoEstagio.from_dict(result)
        else:
            return None
