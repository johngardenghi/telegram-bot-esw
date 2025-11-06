import mysql.connector
from mysql.connector import Error
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
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

            wait = WebDriverWait(driver, 10)
            actions = ActionChains(driver)

            print("Abrindo o SIGAA")
            driver.get("https://sig.unb.br/sigaa")

            waitSair = WebDriverWait(driver, 2)
            while True:
                # Faz o login
                wait.until(EC.presence_of_element_located((By.ID, "username")))
                print("Fazendo o login")
                driver.find_element (By.XPATH, '//*[@id="username"]').clear()
                driver.find_element (By.XPATH, '//*[@id="username"]').send_keys (os.environ.get("ESWBOT_SIGAA_USER"))
                driver.find_element (By.XPATH, '//*[@id="password"]').clear()
                driver.find_element (By.XPATH, '//*[@id="password"]').send_keys (os.environ.get("ESWBOT_SIGAA_PASS"))
                driver.find_element (By.XPATH, '//*[@id="login-form"]/button').click()

                # Verifica se deu o erro de bloqueio da conta
                try:
                    waitSair.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/center/a')))
                    driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/center/a').click()
                except:
                    break

            # Clica no "Ciente"
            print("Clicando em Ciente")
            try:
                xpath =  '//*[@id="sigaa-cookie-consent"]/button'
                wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                driver.find_element (By.XPATH, xpath).click()
            except:
                pass

            # Clica no vinculo de supervisor acadêmico
            print("Escolhendo o vinculo")
            xpath = '/html/body/div[2]/div[2]/form/table/tbody/tr/td/table/tbody/tr[4]/td[2]/a'
            wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            driver.find_element (By.XPATH, xpath).click()

            # Clica em "Continuar"
            xpath = '//*[@id="j_id_jsp_933481798_1"]/div/input'
            wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            driver.find_element (By.XPATH, xpath).click()

            # Clica no Portal Coord. Graduação
            print("Acessando Portal Coord. Graduacao")
            xpath = '//*[@id="portais"]/ul/li[5]/a'
            wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            driver.find_element (By.XPATH, xpath).click()

            # Abre o menu "Estagios"
            print("Abrindo o menu Estagios")
            xpath = '//*[@id="menu_coordenador_menuMatriculas_menu"]/table/tbody/tr/td[7]/span[2]'
            wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            menu = driver.find_element (By.XPATH, xpath)
            actions.move_to_element(menu).perform()

            # Clica em "Gerenciar Estagios"
            print("Clicando em Gerenciar Estagios")
            xpath = '//*[@id="cmSubMenuID12"]/table/tbody/tr[4]/td[2]'
            wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
            menu = driver.find_element (By.XPATH, xpath)
            actions.move_to_element(menu).click().perform()

            # Filtra por ATIVOS
            print("Selecionando apenas filtro de Estagios Ativos")
            xpath = '//*[@id="form:checkStatus"]'
            wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            driver.find_element (By.XPATH, xpath).click()
            Select(driver.find_element (By.XPATH, '//*[@id="form:statusStagio"]')).select_by_value("7")

            # Filtra por ENGENHARIA DE SOFTWARE
            # driver.find_element (By.XPATH, '//*[@id="form:checkCurso"]').click()
            # Select(driver.find_element (By.XPATH, '//*[@id="form:curso"]')).select_by_value("414924")

            # Clica em Buscar
            driver.find_element (By.XPATH, '//*[@id="form:btBuscar"]').click()

            # Recupera o total de Estagios Encontrados
            try:
                xpath = '//*[@id="form"]/table[2]/caption'
                wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                caption = driver.find_element (By.XPATH, xpath).text
                total_ativos = int(re.search(r"\((\d+)\)", caption).group(1))
            except NoSuchElementException:
                total_ativos = 0

            print(f"Total de alunos com estágio ativo: {total_ativos}")

            total_alunos_comissao = 0
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

                        # # Desmarca o filtro por curso
                        # driver.find_element (By.XPATH, '//*[@id="form:checkCurso"]').click()

                        # # Clica em Buscar
                        # driver.find_element (By.XPATH, '//*[@id="form:btBuscar"]').click()

                        # time.sleep(5)

                        # # Recupera o total de Estagios Encontrados
                        # try:
                        #     caption = driver.find_element (By.XPATH, '//*[@id="form"]/table[2]/caption').text
                        #     total_orientandos = int(re.search(r"\((\d+)\)", caption).group(1))
                        # except NoSuchElementException:
                        #     total_orientandos = 0

                        # # Marca o filtro por curso
                        # driver.find_element (By.XPATH, '//*[@id="form:checkCurso"]').click()
                        # Select(driver.find_element (By.XPATH, '//*[@id="form:curso"]')).select_by_value("414924")

                        # Clica em Buscar
                        driver.find_element (By.XPATH, '//*[@id="form:btBuscar"]').click()

                        time.sleep(5)

                        # Recupera o total de Estagios Encontrados para ESW
                        try:
                            caption = driver.find_element (By.XPATH, '//*[@id="form"]/table[2]/caption').text
                            total_orientandos_software = int(re.search(r"\((\d+)\)", caption).group(1))
                        except NoSuchElementException:
                            total_orientandos_software = 0

                        total_alunos_comissao = total_alunos_comissao + total_orientandos_software

                        print(f"{linha[ind_nome]}: {total_orientandos_software}")
                        result = result + f"{linha[ind_nome]}: {total_orientandos_software}\n"

                        # Atualiza o total de orientandos no banco de dados
                        queryUpdate = "UPDATE orientador_estagio SET total_alunos_ativos = %s WHERE id = %s"
                        valores = (total_orientandos_software, linha[ind_id])
                        cursor.execute(queryUpdate, valores)
                        conn.commit()

                    porcentagem = round (total_alunos_comissao / total_ativos, 4) * 100
                    result = result + (
                        f"\nTotal de alunos com estágio ativo: {total_ativos}"
                        f"\nTotal de alunos sob orientação da comissão: {total_alunos_comissao} ({porcentagem}%)"
                        "\n\nOs dados no banco foram atualizados com sucesso."
                    )
                  

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
