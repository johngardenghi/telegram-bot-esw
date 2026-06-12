from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)
from service import ConfigManager

AGUARDANDO_RAIO = 1

async def atualizar_raio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    administracao_service = context.application.bot_data["administracao_service"]
    if not administracao_service.eh_admin(update.message.from_user.id):
        await update.message.reply_text("Você não tem privilégios para executar esta atualização.")
        return ConversationHandler.END

    await update.message.reply_text(
        f"Informe o novo valor do raio (atual = {ConfigManager.get_raio()}).\n\n"
        "Para cancelar, envie /cancelar."
    )

    return AGUARDANDO_RAIO

async def receber_novo_raio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    texto = update.message.text.strip()

    try:
        novo_raio = int(texto)
    except ValueError:
        await update.message.reply_text(
            "Valor inválido. Informe apenas um número inteiro.\n\n"
            "Exemplo: 5, 10 ou 20"
        )
        return AGUARDANDO_RAIO

    if novo_raio <= 0:
        await update.message.reply_text(
            "O raio precisa ser um número inteiro maior que zero. Informe outro valor."
        )
        return AGUARDANDO_RAIO

    ConfigManager.set_raio(novo_raio)

    await update.message.reply_text(
        f"Raio atualizado com sucesso para {novo_raio}."
    )

    return ConversationHandler.END

async def cancelar_atualizacao_raio(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text("Atualização do raio cancelada.")
    return ConversationHandler.END


def get_atualizar_raio_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CommandHandler("atualiza_raio", atualizar_raio)
        ],
        states={
            AGUARDANDO_RAIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_novo_raio)]
        },
        fallbacks=[
            CommandHandler("cancelar", cancelar_atualizacao_raio)
        ],
    )
