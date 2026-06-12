import os

import mysql.connector
from mysql.connector import Error
from service.config_manager import ConfigManager

class OrientadorService:
    def __init__(self, orientador_estagio_dao):
        self.orientador_estagio_dao = orientador_estagio_dao

    def get_orientador_by_id (self, id_orientador):
        return self.orientador_estagio_dao.get_orientador_by_id(id_orientador)

    def indica_orientador(self):
        orientadorEstagio = self.orientador_estagio_dao.get_orientador_disponivel(ConfigManager.get_raio())

        if orientadorEstagio is None:
            # Se não houve selecionados, pode ser que os ativos estejam todos 1. Precisa ativar todos novamente
            self.orientador_estagio_dao.set_orientadores_disponiveis()
            orientadorEstagio = self.orientador_estagio_dao.get_orientador_disponivel(ConfigManager.get_raio())

        if orientadorEstagio is not None:
            self.orientador_estagio_dao.set_orientador_indisponivel(orientadorEstagio.id)

        return orientadorEstagio

    async def disponiveis(self):
        return self.orientador_estagio_dao.lista_orientadores_disponiveis(ConfigManager.get_raio())

    async def afastados(self):
        return self.orientador_estagio_dao.lista_orientadores_afastados()

    async def inativos(self):
        return self.orientador_estagio_dao.lista_orientadores_inativos()
