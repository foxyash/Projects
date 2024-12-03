from PySide6.QtWidgets import (QApplication, QPushButton, QWidget, 
                               QGridLayout, QMainWindow)
from PySide6.QtCore import Slot
import os
import csv
import sys

@Slot()
def exibirMundo(statusBar):
    statusBar.showMessage('Deu certo o teste')

@Slot()
def outro_slot(checked):
    print('está marcado?', checked)

@Slot()
def terceiro_slot(acao):
    def inner():
        outro_slot(acao.isChecked())
    return inner

app = QApplication(sys.argv)

class MyWindow(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.menu = self.menuBar()
        self.menuExtrato = self.menu.addMenu('Extrato da Conta')
        self.irParaExtrato = self.menuExtrato.addAction('Ver Extrato')
        self.irParaExtrato.triggered.connect(lambda: exibirMundo(self.statusBar))

        self.irParaExtrato2 = self.menuExtrato.addAction('Ver Extrato 2')
        self.irParaExtrato2.setCheckable(True)
        self.irParaExtrato2.hovered.connect(terceiro_slot(self.irParaExtrato2))

        self.statusBar = self.statusBar()
        self.statusBar.showMessage('Controle de Finanças')

        self.botao = QPushButton('sexo anal casual')
        self.botao.setStyleSheet('font-size: 80px; color: red;')
        self.botao.show()

        self.botao.clicked.connect(terceiro_slot(self.irParaExtrato2))

        self.botao2 = QPushButton('teste demais')
        self.botao2.show()

        self.botao3 = QPushButton('enviar')
        self.botao2.show()


        self.layout = QGridLayout()
        self.central_widget.setLayout(self.layout)
        self.layout.addWidget(self.botao, 1, 1, 1, 1)
        self.layout.addWidget(self.botao2, 1, 2, 1, 1)
        self.layout.addWidget(self.botao3, 3, 1, 1, 2)

        

self = MyWindow()

# caminho_inicial = "/Users/SAMSUNG/Desktop/Ciencia de dados/logica"
# os.chdir(caminho_inicial)

# registrosTransacao = {}
# registrosDeposito = {}

# extratoDespesas = ('extratoDespesas.csv')
# extratoReceitas = ('extratoReceitas.csv')

# def linhas():
#     return print('---------------')

# def salvarCSV(dados, nomeDoArquivo):
#     tituloColuna = {'Valor da Transação', 'Tipo da Transação'} 

#     with open(nomeDoArquivo, mode='a', newline='', encoding='UTF-8') as arquivo:

#         arquivoCSV = csv.DictWriter(arquivo, fieldnames=tituloColuna)
#         if arquivo.tell() == 0:
#             arquivoCSV.writeheader()

#         for tipo, valor in dados.items():    
#             arquivoCSV.writerow({'Tipo da Transação': tipo, 'Valor da Transação': valor})

# def lerCSV(bancoExtratos):
#     with open('extratoDespesas.csv', mode='r', encoding='UTF-8') as arquivo:
#         leitor = csv.DictReader(arquivo)
#         valores= []
    
#         for valor in leitor:
#             valor = float(valor['Valor da Transação'])  
#             valores.append(valor)
        
#     return valores

# def exibirValorNaConta():
#     extratoDespesa = lerCSV('extratoDespesas.csv')
#     extratoReceita = lerCSV('extratoReceitas.csv')
#     saldoAtual = sum(extratoReceita) + sum(extratoDespesa)
#     return print(f'Saldo Atual: R${saldoAtual:.2f}')

# def registrarEntradaDeDinheiro(tipo, deposito):
#     guardarDeposito = registrosDeposito[tipo] = deposito
#     return guardarDeposito

# def registrarGasto(tipo, gastos):
#     guardarTransacao = registrosTransacao[tipo] = -gastos
#     return guardarTransacao

# while True:
#     os.system('cls')
#     linhas()
#     print('\n- Auxiliar de Contas -')
#     print('\n----- Digite a opção que deseja efetuar -----')
#     print('\n1- Registrar Depositos - ')
#     print('\n2- Registrar Transações - ')
#     print('\n3- Ver Saldo -')
#     print('\n0 - Sair')
#     opcao = int(input('\nDigite a opção selecionada: '))
#     linhas()

#     if opcao == 0:
#         break

#     elif opcao == str:
#         print('Digite um dos valores números acima: {e}')

#     elif opcao == 3:
#         os.system('cls')
#         exibirValorNaConta()
#         voltar = str(input('\nDeseja voltar para o menu?: (s/n) '))
#         if voltar == 's' or voltar == 'S':
#             pass
#         else:
#             print('Bye, Bye...')
#             break

#     else:
#         tipo = str(input('Tipo do gasto: '))
#         valor = float(input('Valor do Gasto: '))
#         pass

#     match opcao:
#         case 1:
#             os.system('cls')
#             print('Depositos Registrado com Sucesso!\n')
#             registrarEntradaDeDinheiro(tipo, valor)
#             salvarCSV(registrosDeposito, extratoReceitas)

#             voltar = str(input('Deseja voltar para o menu?: (s/n) '))
#             if voltar == 's' or voltar == 'S':
#                 pass
#             else:
#                 print('Bye, Bye...')
#                 break

#         case 2:
#             os.system('cls')
#             print('Despesa Registrada com Sucesso!\n')
#             registrarGasto(tipo, valor)
#             salvarCSV(registrosTransacao, extratoDespesas)



#             voltar = str(input('Deseja voltar para o menu?: (s/n) '))
#             if voltar == 's' or voltar == 'S':
#                 pass
#             else:
#                 print('Bye, Bye...')
#                 break




window.show()
app.exec()