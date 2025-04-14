from dao import OrientadorEstagioDAO, SolicitacaoEstagioDAO
from database.connection import DatabasePool
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext, ConversationHandler, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from telegram.warnings import PTBUserWarning
from warnings import filterwarnings
from email.mime.text import MIMEText
import os
import smtplib

VERF, NOME = range(2)

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

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

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

async def inicia_conversa(update:Update, context: CallbackContext):
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

        conn.close()
    
    # Se não houver solicitação prévia de orientador, inicia o processo de indicacao
    # 1. Faz confimações de autoverificação
    # 2. Solicita o nome do aluno e indica o orientador
    else:
        context.user_data["conn"] = conn

        keyboard = [
            [InlineKeyboardButton("Sim", callback_data="possui_TCE"),
             InlineKeyboardButton("Não", callback_data="nao_possui_TCE")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Você já possui um Termo de Compromisso de Estágio?", reply_markup=reply_markup)

        return VERF
        
async def verificar_estagio(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()  # Confirma que a ação foi processada
    
    if query.data == "possui_TCE":
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("Sim", callback_data="inicio_futuro"),
            InlineKeyboardButton("Não", callback_data="nao_inicio_futuro")]])
        await query.edit_message_text("A UnB não assina Termos de Compromisso de Estágio com início que já passou.\n\nA data de início de estágio é futura?", reply_markup=reply_markup)
    
    elif query.data == "nao_possui_TCE":
        await query.edit_message_text("Então, antes providencie um Termo de Compromisso de Estágio. Se a empresa não possui um modelo, você pode encontrar um modelo em https://deg.unb.br/documentos-e-modelos. Preencha o documento e solicite a assinatura de todas as partes antes de solicitar a da UnB. Lembre-se que a data de início do estágio deve ser futura e recomendamos que o documento seja encaminhado para assinatura do(a) professor(a) orientador(a) com antecedência de 10 dias do início do estágio. Quando tiver o documento, me chame novamente que eu indico o(a) professor(a) orientador(a).")
        return ConversationHandler.END
    
    elif query.data == "inicio_futuro":
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("Sim", callback_data="horario_adequado"),
            InlineKeyboardButton("Não", callback_data="nao_horario_adequado")]])
        await query.edit_message_text("Para realizar o estágio, você precisa de tempo. Embora pareça óbvio, o horário do estágio não pode chocar com o horário das disciplinas e se o estágio for presencial, você precisa cumprir sua jornada diária de forma corrida, recomendavelmente em horário comercial e considerar o tempo de deslocamento ao seu estágio. O Termo de Compromisso precisa refletir fielmente o que foi combinado com a empresa com relação a isso: se o horário é flexível, se o estágio é remoto, etc.\n\nO horário do estágio está adequado com relação ao seu horário de aulas, e isto consta no seu Termo de Compromisso de Estágio?", reply_markup=reply_markup)
    
    elif query.data == "nao_inicio_futuro":
        await query.edit_message_text("Então, por favor, solicite à empresa que refaça o Termo de Compromisso de Estágio para o seu estágio iniciar numa data futura. Nós recomendamos que o documento seja encaminhado para assinatura do(a) professor(a) orientador(a) com 10 dias de antecedência do início do estágio. Quando tiver a nova versão do TCE com data de início futura, pode me chamar novamente que eu indico o(a) professor(a) orientador(a).")
        return ConversationHandler.END
    
    elif query.data == "horario_adequado":
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("Sim", callback_data="tce_assinado"),
            InlineKeyboardButton("Não", callback_data="tce_nao_assinado")]])
        await query.edit_message_text("O Termo de Compromisso precisa estar assinado por você, pelo representante da empresa e pelo supervisor de estágio na empresa.\n\nTodos já assinaram seu Termo de Compromisso de Estágio e falta apenas do(a) professor(a) orientador(a)?", reply_markup=reply_markup)
    
    elif query.data == "nao_horario_adequado":
        await query.edit_message_text("Então, por favor, solicite à empresa que adeque seus horários no Termo de Compromisso de Estágio. Estágio em regime remoto pode ajudar a adequar sua carga horária e isso precisa constar explicitamente no termo. Quando tiver a nova versão do TCE, pode me chamar novamente que eu indico o(a) professor(a) orientador(a).")
        return ConversationHandler.END

    elif query.data == "tce_assinado":
        conn = context.user_data["conn"]
        orientadorEstagioDAO = OrientadorEstagioDAO(conn)
        orientadorEstagio = orientadorEstagioDAO.seleciona_orientadores_disponiveis()

        # Se não houver orientador disponível, apenas notifica e encerra
        if orientadorEstagio is None:
            await query.edit_message_text("Infelizmente, não há orientadores disponíveis no momento. Por favor, procure a coordenação do curso pelo e-mail engsoftware@unb.br ou procure a secretaria da FCTE.")
        
        # Se houver orientador disponível, solicita o nome (função get_nome), salva a solicitação e encaminha orientações
        else:
            context.user_data["orientador"] = orientadorEstagio
            await query.edit_message_text("Por favor, qual o seu nome?")
            return NOME
    
    elif query.data == "tce_nao_assinado":
        await query.edit_message_text("Então, por favor, solicite que os responsáveis assinem antes de encaminhar o TCE para assinatura do(a) professor(a) orientador(a). Quando tiver o documento assinado, pode me chamar novamente que eu indico o(a) professor(a) orientador(a).")
        return ConversationHandler.END

async def encaminhar_instrucoes(update: Update, context: CallbackContext) -> int:
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

# Configuração do bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Configura comandos e mensagens
    orientador_estagio_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, inicia_conversa)],
        states={VERF: [CallbackQueryHandler(verificar_estagio)],
                NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, encaminhar_instrucoes)]},
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    app.add_handler(CommandHandler('start', inicia_conversa))
    app.add_handler(orientador_estagio_handler)

    print("Bot está funcionando!")
    app.run_polling()