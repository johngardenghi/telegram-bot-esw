class OrientadorEstagio:
    def __init__(self, id=None, nome=None, disponivel=None, total_alunos_ativos=None, indisponivel_inicio=None, indisponivel_fim=None, email=None):
        self.id = id
        self.nome = nome
        self.disponivel = disponivel
        self.total_alunos_ativos = total_alunos_ativos
        self.indisponivel_inicio = indisponivel_inicio
        self.indisponivel_fim = indisponivel_fim
        self.email = email

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            nome=data.get("nome"),
            disponivel=data.get("disponivel"),
            total_alunos_ativos=data.get("total_alunos_ativos"),
            indisponivel_inicio=data.get("indisponivel_inicio"),
            indisponivel_fim=data.get("indisponivel_fim"),
            email=data.get("email")
        )
