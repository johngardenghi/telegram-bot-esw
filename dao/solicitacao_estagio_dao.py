from models.solicitacao_estagio import SolicitacaoEstagio
from datetime import datetime

class SolicitacaoEstagioDAO:
    def __init__(self, conn):
        self.conn = conn
    
    def insere_solicitacao(self, orientador, aluno, telegram_id):
        cursor = self.conn.cursor(dictionary=True)

        query = "INSERT INTO solicitacao_estagio (orientador, aluno, telegram_id, data_hora) VALUES (%s, %s, %s, %s);"
        cursor.execute(query, (orientador, aluno, telegram_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.conn.commit()

        cursor.close()

    def verifica_solicitacao_ativa(self, telegram_id):
        cursor = self.conn.cursor(dictionary=True)

        query = "SELECT * FROM solicitacao_estagio WHERE telegram_id = %s AND data_hora >= NOW() - INTERVAL 1 MONTH;"
        cursor.execute(query, (telegram_id,))

        result = cursor.fetchone()
        if result:
            return SolicitacaoEstagio.from_dict(result)
        else:
            return None