class AdministradorEstagio:
    def __init__(self, id=None, telegram_id=None):
        self.id = id
        self.telegram_id = telegram_id

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            telegram_id=data.get("telegram_id")
        )

