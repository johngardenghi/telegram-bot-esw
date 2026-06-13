import os

from telegram import BotCommand, BotCommandScopeChat
from telegram.ext import Application, ApplicationBuilder
from telegram.warnings import PTBUserWarning
from warnings import filterwarnings

from dao import (
    AdministradorEstagioDAO,
    OrientadorEstagioDAO,
    SolicitacaoEstagioDAO
)

from service import (
    AdministracaoService,
    OrientadorService,
    CredentialManager,
    SIGAAUpdate,
    SolicitacaoEstagioService
)

from handlers.atualiza_alunos_handler import get_atualiza_alunos_handler
from handlers.orientador_estagio_handler import (
    get_orientador_estagio_handler,
    get_lista_orientadores_disponiveis_handler,
    get_lista_orientadores_afastados_handler,
    get_lista_orientadores_inativos_handler
)
from handlers.raio_handler import get_atualizar_raio_handler

from database.connection import DatabasePool

# Comandos do bot
def comandos_publicos() -> list[BotCommand]:
    return [
        BotCommand("start", "Iniciar indicação de professor orientador de estágio"),
    ]

def comandos_administrador() -> list[BotCommand]:
    return [
        BotCommand("start", "Iniciar indicação de professor orientador de estágio"),
        BotCommand("atualiza_alunos", "Atualizar os totais de alunos por orientador da comissão"),
        BotCommand("atualiza_raio", "Atualizar os totais de alunos por orientador da comissão"),
        BotCommand("orientadores_disponiveis", "Lista os orientadores que estão disponíveis para indicação na data de hoje"),
        BotCommand("orientadores_afastados", "Lista os orientadores que estão indisponíveis para indicação na data de hoje"),
        BotCommand("orientadores_inativos", "Lista os orientadores que não fazem mais parte da comissão"),
    ]

async def configurar_comandos(application: Application):
    await application.bot.set_my_commands(comandos_publicos())

    administracao_service = application.bot_data["administracao_service"]

    for telegram_id in administracao_service.usuarios_admin():
        await application.bot.set_my_commands(
            comandos_administrador(),
            scope=BotCommandScopeChat(chat_id=telegram_id),
        )

# Configuração do bot
def main():
    app = ApplicationBuilder().token(CredentialManager.read_credential("telegram_token")).post_init(configurar_comandos).build()
    filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

    # -----------------------------------------
    # Configuração do banco de dados e serviços
    # -----------------------------------------
    DB_HOST = os.environ.get("ESWBOT_DB_HOST")
    DB_USER = os.environ.get("ESWBOT_DB_USER")
    DB_PASS = CredentialManager.read_credential("db_password")
   
    db_config = {
        'host': DB_HOST,
        'user': DB_USER,
        'password': DB_PASS,
        'database': 'eswunb'
    }

    # Cria o pool de conexões do BD
    db_pool = DatabasePool(db_config)

    # Cria os DAOs, instancia os serviços e guarda no espaço de dados do bot
    administrador_estagio_dao = AdministradorEstagioDAO(db_pool)
    orientador_estagio_dao = OrientadorEstagioDAO(db_pool)
    solicitacao_estagio_dao = SolicitacaoEstagioDAO(db_pool)

    app.bot_data["administracao_service"] = AdministracaoService(administrador_estagio_dao)
    app.bot_data["orientador_service"] = OrientadorService(orientador_estagio_dao)
    app.bot_data["solicitacao_estagio_service"] = SolicitacaoEstagioService(solicitacao_estagio_dao)
    app.bot_data["sigaa_update_service"] = SIGAAUpdate(orientador_estagio_dao)

    # Conversas administrativas mais específicas
    app.add_handler(get_atualizar_raio_handler())
    app.add_handler(get_atualiza_alunos_handler())

    # Comandos administrativos simples
    app.add_handler(get_lista_orientadores_disponiveis_handler())
    app.add_handler(get_lista_orientadores_afastados_handler())
    app.add_handler(get_lista_orientadores_inativos_handler())

    # Conversa principal e mais abrangente por último
    app.add_handler(get_orientador_estagio_handler())

    print("Bot está funcionando!")
    app.run_polling()

if __name__ == "__main__":
    main()
