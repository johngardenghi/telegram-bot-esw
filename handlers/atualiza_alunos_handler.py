"""
Implementa o handler do comando Telegram para atualização de orientandor por professor orientador via SIGAA.
"""

from service import SIGAAUpdate

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

# Função para atualizar dados do SIGAA
async def atualizaSIGAA(update: Update, context: CallbackContext) -> None:
    administracao_service = context.application.bot_data["administracao_service"]
    sigaa_update_service = context.application.bot_data["sigaa_update_service"]
    if administracao_service.eh_admin(update.message.from_user.id):
        await update.message.reply_text("Iniciando a atualização")
        result = await sigaa_update_service.run_update()
        for msg in result:
            await update.message.reply_text(msg)
    else:
        await update.message.reply_text("Você não tem privilégios para executar esta atualização.")

def get_atualiza_alunos_handler() -> CommandHandler:
    return CommandHandler("atualiza_alunos", atualizaSIGAA)
