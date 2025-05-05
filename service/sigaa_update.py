import mysql.connector
from mysql.connector import Error
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.select import Select
import re
import time

class SIGAAUpdate:

    @staticmethod
    async def run_update(db_pool):
        print("Comecando a rotina de atualizacao")
        result = ""
        try:
            options = Options()
            options.add_argument("--headless")  # Adiciona o argumento para headless
            options.add_argument("--no-sandbox")  # Evita problemas de permissões (opcional)

            print("Abrindo o driver do Firefox")
            driver = webdriver.Firefox (options=options, service=Service("/usr/local/bin/geckodriver"))

            print("Abrindo o SIGAA")
            driver.get("https://sig.unb.br/sigaa")

            # Faz o login
            time.sleep(10)
            print("Fazendo o login")
            driver.find_element (By.XPATH, '//*[@id="username"]').clear()
            driver.find_element (By.XPATH, '//*[@id="username"]').send_keys (os.environ.get("ESWBOT_SIGAA_USER"))
            driver.find_element (By.XPATH, '//*[@id="password"]').clear()
            driver.find_element (By.XPATH, '//*[@id="password"]').send_keys (os.environ.get("ESWBOT_SIGAA_PASS"))
            driver.find_element (By.XPATH, '//*[@id="login-form"]/button').click()

            # Clica no "Ciente"
            time.sleep(10)
            print("Clicando em Ciente")
            driver.find_element (By.XPATH, '//*[@id="sigaa-cookie-consent"]/button').click()

            # Clica no vinculo de coordenador da CESG
            time.sleep(10)
            print("Escolhendo o vinculo")
            driver.find_element (By.XPATH, '//*[@id="tdTipo"]/a').click()

            # Clica na Central de Estagios
            time.sleep(10)
            print("Acessando Central de Estagios")
            driver.find_element (By.XPATH, '//*[@id="modulos"]/ul[1]/li[15]/a').click()

            # Clica em Gerenciar Estagios
            time.sleep(10)
            print("Acessando Gerenciar Estagios")
            driver.find_element (By.XPATH, '//*[@id="geral"]/ul/li[3]/ul/li[1]/a').click()

            # Filtra por ATIVOS
            time.sleep(10)
            print("Selecionando apenas filtro de Estagios Ativos")
            driver.find_element (By.XPATH, '//*[@id="form:checkStatus"]').click()
            Select(driver.find_element (By.XPATH, '//*[@id="form:statusStagio"]')).select_by_value("7")

            try:
                # conn = mysql.connector.connect(
                #     host=os.environ.get("ESWBOT_DB_HOST"),
                #     user=os.environ.get("ESWBOT_DB_USER"),
                #     password=os.environ.get("ESWBOT_DB_PASS"),
                #     database='eswunb'
                # )
                conn = db_pool.get_connection()

                if conn.is_connected():
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM orientador_estagio ORDER BY nome")

                    colunas = [desc[0] for desc in cursor.description]
                    ind_nome = colunas.index('nome')
                    ind_id = colunas.index('id')

                    for linha in cursor.fetchall():
                        # Preenche o nome do orientador
                        driver.find_element (By.XPATH, '//*[@id="form:orientador"]').clear()
                        driver.find_element (By.XPATH, '//*[@id="form:orientador"]').send_keys(linha[ind_nome])

                        # Clica em Buscar
                        driver.find_element (By.XPATH, '//*[@id="form:btBuscar"]').click()

                        time.sleep(5)

                        # Recupera o total de Estagios Encontrados
                        try:
                            caption = driver.find_element (By.XPATH, '//*[@id="form"]/table[2]/caption').text
                            total_orientandos = int(re.search(r"\((\d+)\)", caption).group(1))
                        except NoSuchElementException:
                            total_orientandos = 0

                        print(f"{linha[ind_nome]}: {total_orientandos}")
                        result = result + f"{linha[ind_nome]}: {total_orientandos}\n"

                        # Atualiza o total de orientandos no banco de dados
                        queryUpdate = "UPDATE orientador_estagio SET total_alunos_ativos = %s WHERE id = %s"
                        valores = (total_orientandos, linha[ind_id])
                        cursor.execute(queryUpdate, valores)
                        conn.commit()

                    result = result + "\nOs dados no banco foram atualizados com sucesso."

            except Error as e:
                result = f"Erro ao conectar ou consultar o MySQL: {e}"
                print(result)
    
            finally:
                # Fechamento da conexão e do cursor
                if conn.is_connected():
                    cursor.close()
                    conn.close()

                driver.quit()


        except Exception as e:
            result = f"Houve um erro na atualização do SIGAA: {e}"
            print(result)


        finally:
            return result
