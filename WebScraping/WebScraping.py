from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import smtplib
from openpyxl import Workbook
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
from fuzzywuzzy import fuzz


palavras_ignoradas = ['ar condicionado', 'refrigeração', 'refrigeracao', 'ar', 'ar-condicionado', 'oficina', 'mecanica', 'automotiva', 'automtoivo', 'ltda', 'me', 's/a', 'eireli', 'inc', 'corp', 'sa']


class WebScraping:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_experimental_option('prefs', {'intl.accept_languages': 'en_US'})
        options.add_argument('--disable-notifications')
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument('--disable-blink-features=FirstPaintMetrics')
        service = webdriver.ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(options=options, service=service)
        self.driver.get("https://www.google.com.br/maps")
        self.dados = {}

# inicia as classes 

    def iniciar_classes(self):
        self.coletar_email_usuario()
        self.navegar_maps()
        self.raspar_clientes()
        self.comparar_dados()
        self.criar_planilha(self.dados)
        self.enviar_email_usuario()

# coleta o e-mail do usuario, no qual será enviado a prospecção

    def coletar_email_usuario(self):
        self.nome_email =  input('Digite o e-mail que deseja receber a prospecção: ')
        self.nome_email = self.nome_email.lower()
        validar_email = re.search(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+\.[a-zA-Z\.]{2,6}$', self.nome_email)
        if validar_email:
            print('Email válido!')
        else:
            print('Digite um e-mail válido!\n')
            self.coletar_email_usuario()

# faz a navegação pelo maps buscando as informações necessárias para iniciar a raspagem

    def navegar_maps(self):
        self.pesquisar = input('Digite o que deseja pesquisar: ')
        try:
            campo_busca = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="searchboxinput"]')) #//*[@id="searchboxinput"] 
            )
            
            campo_busca.send_keys(self.pesquisar)
            campo_busca.send_keys(Keys.RETURN)
            time.sleep(10)
        
        except Exception as e:
            print(f"Não foi possível acessar o elemento da página {e}")
            self.driver.quit()

# busca cada elemento que corresponda ao nome da empresa e o telefone e me retorna em um dicionario padrozinado {nome: telefone}

    def raspar_clientes(self):
        action = ActionChains(self.driver)
        try:
            a = WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "hfpxzc"))
            )
        except Exception as e:
            print(f"Erro ao localizar elementos: {e}")
            self.driver.quit()
            return

        while True:  
            print(len(a))
            var = len(a)
            
            if a:
                scroll_origin = ScrollOrigin.from_element(a[len(a) - 1])
                action.scroll_from_origin(scroll_origin, 0, 1000).perform()
                time.sleep(2)

                try:
                    fim_lista = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Você chegou ao final da lista.')]")
                    if fim_lista:
                        print("Fim da lista encontrado. Parando a rolagem.")
                        break  
                except Exception as e:
                    print("Ainda não chegou ao fim da lista...")

                try:
                    a = WebDriverWait(self.driver, 30).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "hfpxzc"))
                    )
                except Exception as e:
                    print(f"Erro ao carregar mais elementos: {e}")
                    break

                if len(a) == var:
                    break
            else:
                print("Nenhum elemento encontrado!")
                break

        for i in range(len(a)):
            scroll_origin = ScrollOrigin.from_element(a[i])
            action.scroll_from_origin(scroll_origin, 0, 100).perform()
            action.move_to_element(a[i]).perform()

            try:
                self.driver.execute_script("arguments[0].click();", a[i])
            except Exception as e:
                print(f"Erro ao clicar no elemento: {e}")
                continue

            time.sleep(2)
            source = self.driver.page_source
            soup = BeautifulSoup(source, 'html.parser')
            try:
                Name_Html = soup.findAll('h1', {"class": "DUwDvf lfPIob"})
                name = Name_Html[0].text if Name_Html else 'Nome não encontrado'
                if name not in self.dados:
                    divs = soup.findAll('div', {"class": "Io6YTe fontBodyMedium"})
                    phones = []
                    for div in divs:
                        if re.match(r'\(\d{2}\) \d{4,5}-\d{4}', div.text):
                            phones.append(div.text)
                    phone = ', '.join(phones) if phones else 'Telefone não encontrado'
                    button = soup.find('button', {'aria-label': re.compile(r'Telefone:.*')})
                    if button and 'Telefone não encontrado' in phone:
                        phone = re.search(r'\(\d{2}\) \d{4,5}-\d{4}', button['aria-label']).group() if button else 'Telefone não encontrado'
                    
                    print([name, phone])
                    self.dados[name] = phone
            except Exception as e:
                print(f"Erro ao coletar dados do elemento: {e}")
                continue

# aqui ele faz o tratamento do nome da empresa retornado, removendo espaços, transformando em string e verficando se alguma dessas palavras estão na lista de palavras ignoradas 
    def limpar_nome(self, nome):
        nome_limpo = re.sub(r'[^\w\s]', '', nome.lower().strip())
        palavras = nome_limpo.split()
        palavras = [palavra for palavra in palavras if palavra not in palavras_ignoradas]
        return ' '.join(palavras)

# aqui ele compara os dados que não estão na lista de palavras ignoradas, assim verificando se o mesmo contém o nome ou numero da empresa no banco (planilha) e se caso n tenha, armazena no dicionario novamente
    def comparar_dados(self):
        telefones_existentes = pd.read_excel('C:/Users/SAMSUNG/Desktop/Ciencia de dados/Jumori/WebScraping/telefones.xlsx')

        telefones_existentes['TELEFONE1'] = telefones_existentes['TELEFONE1'].astype(str).apply(lambda x: re.sub(r'\D', '', x))
        telefones_existentes['RAZAOSOCIAL'] = telefones_existentes['RAZAOSOCIAL'].astype(str).str.lower().str.strip()  


        telefones_existentes_set = set(telefones_existentes['TELEFONE1'].tolist())
        nomes_existentes_set = set(telefones_existentes['RAZAOSOCIAL'].apply(lambda x: self.limpar_nome(x)).tolist())  

        deletar_titulos = []

        for titulo, tel in self.dados.items():
            titulo_str = self.limpar_nome(str(titulo))  
            tel_str = re.sub(r'\D', '', str(tel))  

            nome_existe = any(fuzz.ratio(titulo_str, nome) > 90 for nome in nomes_existentes_set)
            telefone_existe = tel_str in telefones_existentes_set 

            if nome_existe or telefone_existe:
                deletar_titulos.append(titulo)

        for titulo in deletar_titulos:
            del self.dados[titulo]
                
        print('-----------------------------------')
        print(f'Clientes removidos: {deletar_titulos}')

# aqui ele gera a planilha para mim, com os campos "nome" e "telefone", armazenando os dados em suas devidas colunas respectivamente

    def criar_planilha(self, dados):
        wb = Workbook()
        ws = wb.active
        ws.title = 'Prospecção'
        ws.append(['Nome', 'Telefone'])
        for nome, telefone in dados.items():
            ws.append([nome, telefone])
        self.arquivo_excel = 'Prospecção.xlsx'
        wb.save(self.arquivo_excel)
        print(f'Salvo como: {self.arquivo_excel}!')

# aqui ele envia o email que foi solicitado na função de coletar o email 

    def enviar_email_usuario(self):
        corpo_email = f"""
        <p>Segue em anexo a planilha de Prospecção de Clientes.<p>
        <br>
        """
        msg =  MIMEMultipart()
        msg['Subject'] = 'Lista de Clientes'
        msg['From'] = 'mailto:emailteste@gmail.com'
        msg['To'] = self.nome_email
        password = 'password'

        msg.attach(MIMEText(corpo_email, _subtype='html',))

        try:
            with open(self.arquivo_excel, 'rb') as f:
                corpo_email = MIMEApplication(f.read(), _subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                corpo_email.add_header('Content-Disposition', 'attachment', filename=self.arquivo_excel)
                msg.attach(corpo_email)
        
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(msg['From'], password)
            s.sendmail(msg['From'], [msg['To']], msg.as_string())
            s.quit()
            print('E-mail enviado com sucesso!')
        except Exception as e:
            print(f'Erro ao enviar o e-mail! {e}')
        
        self.driver.quit()

start = WebScraping()
start.iniciar_classes()
