class SolicitacaoEstagio:
    def __init__(self, id=None, orientador=None, aluno=None, telegram_id=None, data_hora=None, email_aluno=None, telefone_aluno=None):
        self.id = id
        self.orientador = orientador
        self.aluno = aluno
        self.telegram_id = telegram_id
        self.data_hora = data_hora
        self.email_aluno = email_aluno
        self.telefone_aluno = telefone_aluno

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            orientador=data.get("orientador"),
            aluno=data.get("aluno"),
            telegram_id=data.get("telegram_id"),
            data_hora=data.get("data_hora"),
            email_aluno=data.get("email_aluno"),
            telefone_aluno=data.get("telefone_aluno")
        )
