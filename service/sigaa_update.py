import os
import re
import time

import mysql.connector
from mysql.connector import Error

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

from service import CredentialManager

class SIGAAUpdate:
    def __init__(self, orientador_estagio_dao):
        self.orientador_estagio_dao = orientador_estagio_dao

    def update(self, driver, wait, orientadores, url, curso):
        # Acessa o vinculo de Coordenador de Estagio
        print(f"Acessando perfil de Coordenador de Estagio de {curso.capitalize()}")
        driver.get (url)

        # Clica em "Gerenciar Estagios"
        print("   Clicando em Gerenciar Estagios")
        xpath = '//*[@id="geral"]/ul/li[3]/ul/li[1]/a'
        wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        driver.find_element (By.XPATH, xpath).click()

        # Filtra por ATIVOS
        print("   Selecionando apenas filtro de Estagios Ativos")
        xpath = '//*[@id="form:checkStatus"]'
        wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        driver.find_element (By.XPATH, xpath).click()
        Select(driver.find_element (By.XPATH, '//*[@id="form:statusStagio"]')).select_by_value("7")

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

        total_comissao = 0
        # Busca o total de alunos ativos por orientador
        for orientador, alunos in orientadores.items():
            driver.get (driver.current_url)

            print (f"   Alunos de {orientador}")

            # Filtra por ATIVOS
            xpath = '//*[@id="form:checkStatus"]'
            wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            driver.find_element (By.XPATH, xpath).click()
            Select(driver.find_element (By.XPATH, '//*[@id="form:statusStagio"]')).select_by_value("7")

            # Preenche o nome do orientador
            driver.find_element (By.XPATH, '//*[@id="form:orientador"]').clear()
            driver.find_element (By.XPATH, '//*[@id="form:orientador"]').send_keys(orientador)

            # Clica em Buscar
            driver.find_element (By.XPATH, '//*[@id="form:btBuscar"]').click()

            # Recupera o total de Estagios Encontrados para ESW
            try:
                xpath_sucesso = '//*[@id="form"]/table[2]/caption'
                xpath_falha = '//*[@id="painel-erros"]/ul'
               
                elemento = wait.until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, xpath_sucesso)),
                        EC.presence_of_element_located((By.XPATH, xpath_falha))
                    )
                )

                if elemento.get_attribute("class") == "erros":
                    total_alunos = 0
                else:
                    caption = elemento.text
                    total_alunos = int(re.search(r"\((\d+)\)", caption).group(1))

            except NoSuchElementException:
                total_alunos = 0

            orientadores[orientador][curso] = total_alunos
            total_comissao = total_comissao + total_alunos

        return total_ativos, total_comissao

    async def run_update(self):
        print("Comecando a rotina de atualizacao")
        result = ""
        result_soft = ""
        result_abi = ""
        try:
            options = Options()
            options.add_argument("--headless")    # Adiciona o argumento para headless
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
                driver.find_element (By.XPATH, '//*[@id="username"]').send_keys (CredentialManager.read_credential("sigaa_user"))
                driver.find_element (By.XPATH, '//*[@id="password"]').clear()
                driver.find_element (By.XPATH, '//*[@id="password"]').send_keys (CredentialManager.read_credential("sigaa_password"))
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

            # Constroi lista de orientadores
            orientadores = self.orientador_estagio_dao.lista_orientadores_ativos()

            # Atualiza alunos de Software
            link = 'https://sigaa.unb.br/sigaa/escolhaVinculo.do?dispatch=escolher&vinculo=3'
            total_ativos_software, total_comissao_software = self.update (driver, wait, orientadores, link, 'software')

            # Atualiza alunos das Engenharias
            link = 'https://sigaa.unb.br/sigaa/escolhaVinculo.do?dispatch=escolher&vinculo=4'
            total_ativos_engenharias, total_comissao_engenharias = self.update (driver, wait, orientadores, link, 'engenharias')

            for nome, info in orientadores.items():
                if info["engenharias"] > 0:
                    result = result + f'{nome}: {info["software"]} + {info["engenharias"]} = {info["software"] + info["engenharias"]}\n'
                else:
                    result = result + f'{nome}: {info["software"]}\n'

                # Atualiza o total de orientandos no banco de dados
                self.orientador_estagio_dao.atualiza_alunos_orientador(info["id"], info["software"] + info["engenharias"])

            result_soft = "\nENGENHARIA DE SOFTWARE\n"
            porcentagem = round (total_comissao_software / total_ativos_software, 4) * 100
            result_soft = result_soft + f"- Total de alunos com estágio ativo: {total_ativos_software}\n"
            result_soft = result_soft + f"- Total de alunos sob orientação da comissão: {total_comissao_software} ({porcentagem:.2f}%)\n"

            result_abi = "\nENGENHARIAS (ABI)\n"
            porcentagem = round (total_comissao_engenharias / total_ativos_engenharias, 4) * 100
            result_abi = result_abi + f"- Total de alunos com estágio ativo: {total_ativos_engenharias}\n"
            result_abi = result_abi + f"- Total de alunos sob orientação da comissão: {total_comissao_engenharias} ({porcentagem:.2f}%)\n"

            driver.quit()

        except Exception as e:
            result = f"Houve um erro na atualização do SIGAA: {e}"
            print(result)


        finally:
            if result_soft != "":
                result = result + result_abi + result_soft

            return [result]
