from selenium import webdriver
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
from time import sleep
from datetime import datetime



class ScrapingConcorrentes:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_experimental_option('prefs', {'intl.accept_languages': 'pt_BR'})
        options.add_argument('--disable-notifications')
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument('--disable-blink-features=FirstPaintMetrics')
        service = webdriver.ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(options=options, service=service)
        self.driver.get('https://www.acciolygm.com.br/loja/busca.php?loja=476243&palavra_busca=condensador&order=2&categoria=&pg=1')
        self.dict = {}

    def iniciar_classes(self):
        self.raspar_site()
        self.criar_planilha(self.dict)
        self.enviar_email()

    def raspar_site(self):
        i = 0
        while True:
            try:    
                produtos = WebDriverWait(self.driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, '//span[contains(text(), "Compressor ar condicionado") or contains(text(), "Condensador do ar condicionado") or contains(text(), "Condensador ar condicionado")]'))) 
                valores = WebDriverWait(self.driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@class="price-old pix-oriented"]')))
                valor_desconto =  WebDriverWait(self.driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, '//em[@class="value"]'))) 
                valor_a_vista =  WebDriverWait(self.driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="text-pix-payment"]'))) 

                for produto, valor, valordesconto, valorpix in zip(produtos, valores, valor_desconto, valor_a_vista):
                    valor_pix_tratado = valorpix.text.replace('à vista com desconto', '').strip()
                    self.dict[produto.text] = (valor.text, valordesconto.text, valor_pix_tratado)
                    print(f'{produto.text}: Valor sem desconto = {valor.text}, valor com desconto = {valordesconto.text}, valor à vista no pix =  {valor_pix_tratado}')

            except Exception as e:
                print(f'Não foi possivel localizar os elementos! {e}')
                break  
            try:
                botao_proximo = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//span[@class="pagination-next icon-arrow-simple"]/parent::a')))
                self.driver.execute_script("arguments[0].click();", botao_proximo)
                i += 1
                print(f'Clicado no botão próximo {i}')
                sleep(2)
            except Exception as e:
                print(f"Não foi possivel localizar o botão próximo! {e}")
                break

    def criar_planilha(self, dict):
        wb = Workbook()
        ws = wb.active
        ws.title = 'Valores Accioly'
        ws.append(['Produto', 'Valor sem Desconto', 'Valor com Desconto', 'Valor no PIX', 'Data/Hora'])

        data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for produto, ( valor, valordesconto, valorpix) in dict.items():
            ws.append([produto, valor, valordesconto, valorpix, data_hora_atual])
        self.nome_arquivo = 'ValoresAccioly.xlsx'
        wb.save(self.nome_arquivo)
        print(f"Salvo como: {self.nome_arquivo}")

    def enviar_email(self):
        corpo_email = f"""
        <p>Segue em anexo a planilha de Comparação de Valores da Accioly.<p>
        <br>
        """
        msg =  MIMEMultipart()
        msg['Subject'] = 'Valores Accioly'
        msg['From'] = 'mailto:email@email.com.br'
        msg['To'] = 'email@email.com'
        password = 'password'

        msg.attach(MIMEText(corpo_email, _subtype='html',))

        try:
            with open(self.nome_arquivo, 'rb') as f:
                corpo_email = MIMEApplication(f.read(), _subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                corpo_email.add_header('Content-Disposition', 'attachment', filename=self.nome_arquivo)
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

iniciar = ScrapingConcorrentes()
iniciar.iniciar_classes()