# pip install -r requirements.txt

import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime

controle_livros_jumori = pd.read_excel('Z:/TI/WILLIAM/LIVROS.xlsm', sheet_name='CONSULTA', usecols=['COLABORADOR', 'DATA DEVOLUÇÃO', 'STATUS', 'LIVRO'])
controle_livros_jumori.columns = controle_livros_jumori.columns.str.strip().str.lower()
controle_livros_jumori['data devolução'] = pd.to_datetime(controle_livros_jumori['data devolução'], errors='coerce')
controle_livros_jumori.dropna(subset=['data devolução'], inplace=True)

controle_livros_jumori['status'] = controle_livros_jumori['status'].str.strip().str.lower()
data_hoje = pd.Timestamp(datetime.date.today())

devolucao_vencida_livros = controle_livros_jumori[
    (controle_livros_jumori['data devolução'] < data_hoje) & 
    (controle_livros_jumori['status'] != 'finalizado')
]

devolucao_datalimite_hoje = controle_livros_jumori[
    controle_livros_jumori['data devolução'] == data_hoje
][['colaborador', 'data devolução', 'livro']]


password = 'acdp enzz fkgh psgu'  
try:
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login('gabrielsandovaljumori@gmail.com', password)

    if not devolucao_vencida_livros.empty:
        devolucao_vencida_livros.columns = devolucao_vencida_livros.columns.str.upper()
        corpo_email_devolucao_vencido = f"""
        <p>Bom dia!</p>
        <p>Segue os serviços com o prazo de devolução vencidos até o dia de hoje ({data_hoje}):</p>
        <p>{devolucao_vencida_livros.to_html(index=False, justify='center', border=0)}</p>
        <p>Caso a devolução tenha sido efetuada e a planilha não tenha sido atualizada, favor desconsiderar essa mensagem e atualizar a planilha!</p>
        <br>
        """
        msg_vencidos = MIMEMultipart()
        msg_vencidos['Subject'] = 'Controle de livros da Jumori com devolução vencida.'
        msg_vencidos['From'] = 'gabrielsandovaljumori@gmail.com'
        msg_vencidos['To'] = 'gabriel.sandoval@jumori.com.br'
        msg_vencidos.attach(MIMEText(corpo_email_devolucao_vencido, _subtype='html'))
        s.sendmail(msg_vencidos['From'], [msg_vencidos['To']], msg_vencidos.as_string())
        print('E-mail de devoluções vencidas enviado com sucesso!')

    if not devolucao_datalimite_hoje.empty:
        devolucao_datalimite_hoje.columns = devolucao_datalimite_hoje.columns.str.upper()
        corpo_email_servico_hoje = f"""
        <p>Bom dia!</p>
        <p>Segue o aviso dos serviços com prazo de devolução para hoje ({data_hoje}):</p>
        <p>Detalhes:</p>
        <p>{devolucao_datalimite_hoje.to_html(index=False, justify='center', border=0)}</p>
        <br>
        """
        msg_hoje = MIMEMultipart()
        msg_hoje['Subject'] = 'Controle de livros da Jumori - Devoluções de Hoje.'
        msg_hoje['From'] = 'gabrielsandovaljumori@gmail.com'
        msg_hoje['To'] = 'gabriel.sandoval@jumori.com.br'
        msg_hoje.attach(MIMEText(corpo_email_servico_hoje, _subtype='html'))
        s.sendmail(msg_hoje['From'], [msg_hoje['To']], msg_hoje.as_string())
        print('E-mail de devoluções para hoje enviado com sucesso!')

    s.quit()
except Exception as e:
    print(f'Erro ao enviar os e-mails: {e}')
