# Bot do Telegram para atribuição de orientadores de estágio

Este bot é destinado para atribuição de orientadores de estágio do curso de Engenharia de Software.

Os pacotes necessários para seu funcionamento estão em requirements.txt.

## Gerenciamento seguro de credenciais com `systemd`

O bot utiliza o mecanismo de credenciais do `systemd` para armazenar informações sensíveis, como:

- token do Telegram;
- senha de aplicativo do Gmail;
- senha do banco de dados;
- usuário e senha do SIGAA.

As credenciais são criptografadas com o comando `systemd-creds` e carregadas pelo serviço por meio da diretiva `LoadCredentialEncrypted=`.

Dessa forma, senhas e tokens não precisam ser armazenados diretamente no arquivo:

```text
/etc/systemd/system/eswunb-bot.service
```

> [!WARNING]
> Nunca coloque senhas, tokens ou outros segredos no repositório Git ou diretamente no arquivo `.service`.

### 1. Verificar o suporte do `systemd`

Verifique a versão instalada do `systemd`:

```bash
systemctl --version
```

Verifique também se o comando `systemd-creds` está disponível:

```bash
systemd-creds --version
```

Este procedimento considera um serviço de sistema instalado em:

```text
/etc/systemd/system/eswunb-bot.service
```

Não se trata de um serviço de usuário configurado com `systemctl --user`.

### 2. Criar o diretório de credenciais criptografadas

As credenciais criptografadas serão armazenadas no diretório:

```text
/etc/credstore.encrypted/
```

Crie o diretório com acesso restrito ao usuário `root`:

```bash
sudo install \
    -d \
    -m 0700 \
    -o root \
    -g root \
    /etc/credstore.encrypted
```

Para conferir as permissões:

```bash
ls -ld /etc/credstore.encrypted
```

O resultado deverá ser semelhante a:

```text
drwx------ 2 root root ... /etc/credstore.encrypted
```

### 3. Criar as credenciais criptografadas

Para evitar que senhas e tokens apareçam no histórico do terminal, crie temporariamente a seguinte função no Bash:

```bash
encrypt_credential() {
    local name="$1"
    local value

    IFS= read -r -s -p "Informe o valor de ${name}: " value
    printf '\n'

    printf '%s' "$value" |
        sudo systemd-creds encrypt \
            --name="$name" \
            - \
            "/etc/credstore.encrypted/${name}.cred"

    unset value
}
```

Em seguida, utilize a função para criar cada credencial:

```bash
encrypt_credential telegram_token
encrypt_credential gmail_user
encrypt_credential gmail_password
encrypt_credential db_password
encrypt_credential sigaa_user
encrypt_credential sigaa_password
```

A função solicitará o valor de cada credencial sem exibi-lo no terminal.

Ao final, o diretório deverá conter arquivos semelhantes aos seguintes:

```text
/etc/credstore.encrypted/
├── db_password.cred
├── gmail_password.cred
├── gmail_user.cred
├── sigaa_password.cred
├── sigaa_user.cred
└── telegram_token.cred
```

Ajuste o proprietário e as permissões dos arquivos:

```bash
sudo chown root:root /etc/credstore.encrypted/*.cred
sudo chmod 600 /etc/credstore.encrypted/*.cred
```

Confira o resultado:

```bash
sudo ls -l /etc/credstore.encrypted/
```

Os arquivos `.cred` contêm os dados criptografados. Os valores originais não devem ser salvos em arquivos de texto.

> [!IMPORTANT]
> Uma credencial criptografada pode ficar vinculada à máquina na qual foi criada. Em caso de migração para outro servidor, gere novamente os arquivos `.cred`.

### 4. Configurar o serviço

Edite o arquivo do serviço:

```bash
sudo nano /etc/systemd/system/eswunb-bot.service
```

Exemplo de configuração:

```ini
[Unit]
Description=ESW/UnB Telegram Bot Service
Wants=network-online.target
After=network-online.target

[Service]
Type=simple

User=john
Group=john

WorkingDirectory=/home/john/Documentos/telegram-bot-esw/

Environment="PYTHONUNBUFFERED=1"
Environment="ESWBOT_DB_HOST=localhost"
Environment="ESWBOT_DB_USER=root"

LoadCredentialEncrypted=telegram_token:/etc/credstore.encrypted/telegram_token.cred
LoadCredentialEncrypted=gmail_user:/etc/credstore.encrypted/gmail_user.cred
LoadCredentialEncrypted=gmail_password:/etc/credstore.encrypted/gmail_password.cred
LoadCredentialEncrypted=db_password:/etc/credstore.encrypted/db_password.cred
LoadCredentialEncrypted=sigaa_user:/etc/credstore.encrypted/sigaa_user.cred
LoadCredentialEncrypted=sigaa_password:/etc/credstore.encrypted/sigaa_password.cred

ExecStart=/home/john/venv/eswunb_bot/bin/python3 /home/john/Documentos/telegram-bot-esw/bot.py

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Configurações que não são sensíveis, como endereço e usuário do banco de dados, podem continuar sendo declaradas com `Environment=`:

```ini
Environment="ESWBOT_DB_HOST=localhost"
Environment="ESWBOT_DB_USER=root"
```

Senhas, tokens e outros valores sensíveis devem ser carregados com `LoadCredentialEncrypted=`:

```ini
LoadCredentialEncrypted=telegram_token:/etc/credstore.encrypted/telegram_token.cred
```

O formato dessa diretiva é:

```text
LoadCredentialEncrypted=nome_da_credencial:caminho_do_arquivo_criptografado
```

Depois de alterar o arquivo `.service`, recarregue a configuração do `systemd`:

```bash
sudo systemctl daemon-reload
```

Reinicie o serviço:

```bash
sudo systemctl restart eswunb-bot.service
```

Verifique o estado:

```bash
sudo systemctl status --no-pager eswunb-bot.service
```

Em caso de erro, consulte os logs:

```bash
sudo journalctl \
    -u eswunb-bot.service \
    -n 100 \
    --no-pager
```
