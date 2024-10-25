import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import os

controle_livros_jumori = pd.read_excel('c:/Users/SAMSUNG/Desktop/Ciencia de dados/LIVROS.xlsm', sheet_name='CONSULTA') 
controle_livros_jumori.columns = controle_livros_jumori.columns.str.strip().str.lower()
controle_livros_jumori['data devolução'] = pd.to_datetime(controle_livros_jumori['data devolução'], errors='coerce')
data_hoje = pd.Timestamp(datetime.date.today())
dt_livros_jumori = controle_livros_jumori[['colaborador', 'data devolução', 'status', 'livro']].sort_values(by='data devolução', ascending=False)
dt_livros_jumori = dt_livros_jumori.dropna()

devolucao_vencida_livros = []
devolucao_datalimite_hoje = []

for index, linha in dt_livros_jumori.iterrows():
    nome_colaborador = linha['colaborador']
    data_devolucao = linha['data devolução']
    livro = linha['livro']
    finalizado = linha['status']

    if pd.isna(data_devolucao):
        print(f'Nenhuma devolução agendada para {nome_colaborador}')
        continue

    if data_devolucao < data_hoje and str(finalizado).strip().lower() not in ["finalizado"]:
        devolucao_vencida_livros.append(linha)

    elif data_devolucao == data_hoje:
        devolucao_datalimite_hoje.append(linha[['colaborador', 'data devolução', 'livro']])

devolucao_vencida_livros = pd.DataFrame(devolucao_vencida_livros)
devolucao_datalimite_hoje = pd.DataFrame(devolucao_datalimite_hoje)

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
    password = 'acdp enzz fkgh psgu'  
    msg_vencidos.attach(MIMEText(corpo_email_devolucao_vencido, _subtype='html'))

    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(msg_vencidos['From'], password)
        s.sendmail(msg_vencidos['From'], [msg_vencidos['To']], msg_vencidos.as_string())
        s.quit()
        print('E-mail de devoluções vencidas enviado com sucesso!')
    except Exception as e:
        print(f'Erro ao enviar o e-mail de devoluções vencidas: {e}')

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

    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(msg_hoje['From'], password)
        s.sendmail(msg_hoje['From'], [msg_hoje['To']], msg_hoje.as_string())
        s.quit()
        print('E-mail de devoluções para hoje enviado com sucesso!')
    except Exception as e:
        print(f'Erro ao enviar o e-mail de devoluções de hoje: {e}')
else:
    print('Nenhum serviço para o dia de hoje!')

print("Controle dos Livros Jumori:")
print(controle_livros_jumori)
print("---------------------")
print("Devoluções Vencidas:")
print(devolucao_vencida_livros)
print("---------------------")
print("Devoluções de Hoje:")
print(devolucao_datalimite_hoje)