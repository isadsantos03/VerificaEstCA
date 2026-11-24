import tkinter as tela
from tkinter import ttk  # Importa caixas de seleção
from math import isfinite

# Cria a janela principal
janela = tela.Tk()
janela.title("INTERFACE PARA CÁLCULO DE VIGAS")

# Lista de itens que o usuário deve preencher
campos = [
    "Largura da Seção - bw (cm):",
    "Altura da Seção - h (cm):",
    "Altura útil - d (cm):",
    "Distância da fibra comprimida ao CG - d' (cm):",
    "Cobrimento - c (cm):",
    "Resistência Característica do Concreto - fck (MPa):",
    "Momento de Cálculo - Mk (kN*cm):"]

# Lista de mensagens de erro para cada campo
erro = [
    "⚠️ Erro: Digite apenas números positivos!",                # bw
    "⚠️ Erro: Digite apenas números positivos!",                # h
    "⚠️ Erro: Digite apenas números positivos!",                # d
    "⚠️ Erro: Digite apenas números positivos!",                # d'
    "⚠️ Erro: Digite apenas números positivos!",                # c
    "⚠️ Erro: Digite um valor entre o intervalo de 20 e 90!",   # fck
    "⚠️ Erro: Digite um número e diferente de zero!",           # Mk
    "⚠️ Erro: É preciso selecionar uma opção!",                 # fyk
]

# Lista de constantes para o cálculo
constantes = [
    1.4,      #Yc
    1.15,     #Ys
    1.4,      #Yf 
    210000,   #Es
    0.15,     #Pmin,abs
    4,        #(As+A'smax)
]

# Listas que serão utilizadas no decorrer do código
entradas = []
viga = []
avisos = []

#EXECUÇÃO DO PROGRAMA

# Cria os textos e caixas vazias
for i, txt in enumerate(campos):
  tela.Label(janela, text=txt).pack()
  campo_digitação = tela.Entry(janela)
  campo_digitação.pack()
  entradas.append(campo_digitação)  # Guarda a caixinha na lista

  aviso = tela.Label(janela, text="", fg="red", font=("Arial", 8))
  aviso.pack()
  avisos.append(aviso) # Guarda o aviso na lista

# Opções classe do aço
tela.Label(janela, text="Resistência de Escoamento do Aço - fyk (MPa):").pack()
# Cria a caixa com opções
opcao_aco = ttk.Combobox(janela, values=["CA-50", "CA-60"], state="readonly")
opcao_aco.pack()
aviso_aco = tela.Label(janela, text="", fg="red", font=("Arial", 8))
aviso_aco.pack()

# Botão executado
def clicar():

  valores = []

  for i, campo in enumerate(entradas):
    try:
      valor = float(campo.get())
    except ValueError:
      avisos[i].config(text=erro[i])  # Mostra o erro correspondente
      continue

    if not isfinite(valor) or (i <= 4 and valor <=0) or (i == 5 and not 20<= valor <=90) or (i == 6 and valor == 0):
      avisos[i].config(text=erro[i])  # Mostra o erro correspondente
      continue

    avisos[i].config(text="")
    valores.append(valor)

  classe_aco = opcao_aco.get()
  if not classe_aco:
    aviso_aco.config(text=erro[7])
    return

  aviso_aco.config(text="")

  if len(valores) == len(entradas):
    valores.append(classe_aco)
    viga[:] = valores

# Cria o botão
tela.Button(
    janela, text="Ok", bg="green", fg="white", font=("Arial", 12, "bold"), command=clicar
).pack(pady=15)

janela.mainloop()