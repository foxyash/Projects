# utilize pip install e o nome de cada lib abaixo para que o software funcione. ex: pip install smtplib
import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime

servicos_jumori = pd.read_excel('C:/Users/SAMSUNG/Desktop/Ciencia de dados/Jumori/RPA/ManutencaoPredio.xlsx') #caminho do arquivo
data_hoje = pd.Timestamp(datetime.date.today())

for index, linha in servicos_jumori.iterrows():
    nome_servico = linha['Serviço']
    prox_visita = linha['Proxima Visita']

    if pd.isna(prox_visita):
        print(f'Nenhuma visita agendada')
    elif prox_visita == data_hoje:
        corpo_email = f"""
        <p>Bom dia, Leonardo.<p>
        <p>Segue o aviso que o serviço {nome_servico} está com o prazo de visita para hoje! {prox_visita}.<p>
        <br>
        """
        msg =  MIMEMultipart()
        msg['Subject'] = 'Serviços Jumori no PRAZO de 1 ano.'
        msg['From'] = 'mailto:gabrielsandovaljumori@gmail.com'
        msg['To'] =  'gabriel.sandoval@jumori.com.br' #'leonardo.reis@jumori.com.br' #
        password = 'acdp enzz fkgh psgu'

        msg.attach(MIMEText(corpo_email, _subtype='html',))

        try:        
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(msg['From'], password)
            s.sendmail(msg['From'], [msg['To']], msg.as_string())
            s.quit()
            print('E-mail enviado com sucesso!')
        except Exception as e:
            print(f'Erro ao enviar o e-mail! {e}')
    else:
        pass