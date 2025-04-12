from dao import OrientadorEstagioDAO, SolicitacaoEstagioDAO
from database.connection import DatabasePool
from datetime import datetime
from models import OrientadorEstagio
from service.sigaa_update import SIGAAUpdate
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext, ConversationHandler, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from email.mime.text import MIMEText
import os
import smtplib

# pip install python-telegram-bot selenium mysql-connector-python

NOME = 1

# Configurações gerais
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# Variáveis de ambiente que devem ser configuradas no servidor
GMAIL_USER = os.environ.get("ESWBOT_GMAIL_USER")
GMAIL_PASSWORD = os.environ.get("ESWBOT_GMAIL_PASSWORD")
TELEGRAM_BOT_TOKEN = os.environ.get("ESWBOT_TOKEN")
DB_HOST = os.environ.get("ESWBOT_DB_HOST")
DB_USER = os.environ.get("ESWBOT_DB_USER")
DB_PASS = os.environ.get("ESWBOT_DB_PASS")

# Configuração do banco de dados
db_config = {
    'host': DB_HOST,
    'user': DB_USER,
    'password': DB_PASS,
    'database': 'eswunb'
}

# Cria o pool de conexões do BD
db_pool = DatabasePool(db_config)

# Função para enviar e-mail
def send_email(aluno, email):
    body = f"""
    <html><body>
    <p>Prezado(a) professor(a),<br><br>
    O(A) estudante <b>{aluno}</b> acabou de receber indicação do seu nome como orientador(a) de estágio via bot do Telegram.<br><br>
    Em breve, ele(a) deve te enviar a documentação por e-mail.<br><br>
    Atenciosamente,<br><br>Comissão de Estágios de ESW.
    </p></body></html>
    """

    try:
        # Configurar o servidor SMTP com SSL
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            msg = MIMEText(body, "html")
            msg["Subject"] = "Indicação para orientação de estágio"
            msg["From"] = GMAIL_USER
            msg["To"] = email
            msg["Reply-To"] = "engsoftware@unb.br"

            # Enviar o e-mail
            server.sendmail(GMAIL_USER, email, msg.as_string())
        return "E-mail enviado com sucesso!"
    except Exception as e:
        return f"Erro ao enviar e-mail: {e}"

async def start(update:Update, context: CallbackContext):
    await update.message.reply_text("Olá, este canal é exclusivo para indicação de professor(a) orientador(a) para estágio do curso de Engenharia de Software da FCTE")

    conn = db_pool.get_connection()

    solicitacaoEstagioDAO = SolicitacaoEstagioDAO(conn)
    orientadorEstagioDAO = OrientadorEstagioDAO(conn)

    telegram_id = update.message.from_user.id
    
    # Verifica se já há uma orientação de estágio indicada para o usuário que está chamando
    solicitacaoEstagio = solicitacaoEstagioDAO.verifica_solicitacao_ativa(telegram_id)

    # Se já houver uma solicitação de orientador pelo usuário em questão, apenas recupera o orientador indicado e reencaminha as instruções
    if solicitacaoEstagio is not None:
        orientadorEstagio = orientadorEstagioDAO.get_orientador_by_id(solicitacaoEstagio.orientador)
        dataSolicitacao = solicitacaoEstagio.data_hora.strftime("%d/%m/%Y às %H:%M")
        await update.message.reply_text(f"Você já fez uma solicitação de orientação de estágio em {dataSolicitacao}, em que te indicamos como orientador(a) o(a) Prof.(a) <b>{orientadorEstagio.nome}</b>", parse_mode="HTML")
        await update.message.reply_text(f"""Neste momento, por favor:\n
            1. Faça o pré-cadastro do estágio pelo SIGAA.
            2. Encaminhe a documentação para o(a) professor(a) pelo e-mail {orientadorEstagio.email}.
            """, parse_mode="HTML")
        await update.message.reply_text("Por favor, só mande a documentação depois que fizer o cadastro do estágio no SIGAA. Há um manual de como fazer isso, entre outras coisas, <a href='https://deg.unb.br/images/Diretorias/DAIA/cesg/arquivos_gerais/manual_estagio_nao_obrigatorio_discentes.pdf'>aqui</a>", parse_mode="HTML")
        await update.message.reply_text("Lembrando que a recomendação é que a documentação seja encaminhada ao professor orientador com uma antecedência de, no mínimo, 10 dias do início do estágio")
        await update.message.reply_text("Para mais informações sobre estágio, acesse https://software.unb.br/ensino/estagio")
    
    # Se não houver solicitação prévia de orientador, sorteia o próximo
    else:
        orientadorEstagio = orientadorEstagioDAO.seleciona_orientadores_disponiveis()

        # Se não houver orientador disponível, apenas notifica e encerra
        if orientadorEstagio is None:
            await update.message.reply_text("Infelizmente, não há orientadores disponíveis no momento. Por favor, procure a coordenação do curso.")
        
        # Se houver orientador disponível, solicita o nome (função get_nome), salva a solicitação e encaminha orientações
        else:
            context.user_data["orientador"] = orientadorEstagio
            context.user_data["conn"] = conn
            await update.message.reply_text("Por favor, qual o seu nome?")
            return NOME

    conn.close()

async def get_nome(update: Update, context: CallbackContext) -> int:
    # Armazena o nome do aluno
    context.user_data['nome'] = update.message.text
    telegram_id = update.message.from_user.id
    orientadorEstagio = context.user_data["orientador"]
    conn = context.user_data["conn"]
    
    # Encaminha o nome do professor orientador, bem como instruções dos próximos passos
    await update.message.reply_text(f"Você pode indicar como orientador(a) o(a) Prof.(a) <b>{orientadorEstagio.nome}</b>", parse_mode="HTML")
    await update.message.reply_text(f"""Neste momento, por favor:\n
        1. Faça o pré-cadastro do estágio pelo SIGAA.
        2. Encaminhe a documentação para o(a) professor(a) pelo e-mail {orientadorEstagio.email}.
        """, parse_mode="HTML")
    await update.message.reply_text("Por favor, só mande a documentação depois que fizer o cadastro do estágio no SIGAA. Há um manual de como fazer isso, entre outras coisas, <a href='https://deg.unb.br/images/Diretorias/DAIA/cesg/arquivos_gerais/manual_estagio_nao_obrigatorio_discentes.pdf'>aqui</a>", parse_mode="HTML")
    await update.message.reply_text("Lembrando que a recomendação é que a documentação seja encaminhada ao professor orientador com uma antecedência de, no mínimo, 10 dias do início do estágio")
    await update.message.reply_text("Para mais informações sobre estágio, acesse https://software.unb.br/ensino/estagio")

    # Registra a solicitação de orientação
    solicitacaoEstagioDAO = SolicitacaoEstagioDAO(conn)
    solicitacaoEstagioDAO.insere_solicitacao(orientadorEstagio.id, context.user_data['nome'], telegram_id)
    conn.close()

    # Encaminha o e-mail ao professor orientador, notificando-o da indicação
    # print(send_email(context.user_data['nome'], orientadorEstagio.email))
    # print(send_email(context.user_data['nome'], "john.gardenghi@unb.br"))
    
    return ConversationHandler.END

# Função para lidar com cancelamento
def cancel(update: Update, context: CallbackContext) -> int:
    if 'conn' in context.user_data:
        context.user_data["conn"].close()
    
    update.message.reply_text("Conversa cancelada.")
    return ConversationHandler.END

# Função para atualizar dados do SIGAA
async def atualizaSIGAA(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Iniciando a atualização")
    result = SIGAAUpdate.run_update()
    await update.message.reply_text(result)

# Configuração do bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Configura comandos e mensagens
    orientador_estagio_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, start)],
        states={NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_nome)]},
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    app.add_handler(orientador_estagio_handler)
    app.add_handler(CommandHandler("atualizaSIGAA", atualizaSIGAA))

    print("Bot está funcionando!")
    app.run_polling()
