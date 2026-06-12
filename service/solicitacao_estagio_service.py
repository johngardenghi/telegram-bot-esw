class SolicitacaoEstagioService:
    def __init__(self, solicitacao_estagio_dao):
        self.solicitacao_estagio_dao = solicitacao_estagio_dao

    def verifica_solicitacao_ativa(self, user_id):
        return self.solicitacao_estagio_dao.verifica_solicitacao_ativa(user_id)

    def registra_solicitacao(self, solicitacao_estagio):
        self.solicitacao_estagio_dao.insere_solicitacao(solicitacao_estagio)
