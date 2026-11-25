import tkinter as tela
from tkinter import ttk  # Importa caixas de seleção
from math import isfinite, log, sqrt

# Cria a janela principal
janela = tela.Tk()
janela.title("INTERFACE PARA DIMENSIONAMENTO DAS ARMADURAS DE VIGAS DE CONCRETO ARMADO")

# Lista de itens que o usuário deve preencher
campos = [
    "Largura da Seção - bw (cm):",
    "Altura da Seção - h (cm):",
    "Altura útil - d (cm):",
    "Distância da fibra comprimida ao CG - d' (cm):",
    "Cobrimento - c (cm):",
    "Resistência Característica do Concreto - fck (MPa):",
    "Momento Característico - Mk (kN*m):"]

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

# Listas que serão utilizadas no decorrer do código
entradas = []
viga = []
avisos = []

# Dicionário para os parâmetros de cálculo
parametros_calculo = {}

#EXECUÇÃO DO PROGRAMA

# Função para limpar a tela
def limpar_tela():
    for componente in janela.winfo_children():
        componente.destroy()
   
# Função para tela inicial
def tela_inicial():
    global opcao_aco, aviso_aco, botao_avancar, mensagem_validacao

    limpar_tela()
    viga.clear()
    entradas.clear()
    avisos.clear()
    parametros_calculo.clear()

    # Cria os textos e caixas vazias
    for txt in campos:
        tela.Label(janela, text=txt).pack() 
        
        campo_digitação = tela.Entry(janela)
        campo_digitação.pack()
        entradas.append(campo_digitação)  # Guarda a caixinha na lista

        aviso = tela.Label(janela, text="", fg="red", font=("Arial", 8))
        aviso.pack()
        avisos.append(aviso) # Guarda o aviso na lista

    # Cria o texto e a caixa com opções
    tela.Label(janela, text="Resistência de Escoamento do Aço - fyk (MPa):").pack()
    opcao_aco = ttk.Combobox(
       janela, 
       values=["CA-50", "CA-60"], 
       state="readonly"
    )
    opcao_aco.pack()

    aviso_aco = tela.Label(
       janela, 
       text="", 
       fg="red", 
       font=("Arial", 8)
    )
    aviso_aco.pack()

    # Cria o botão de avanço
    botao_avancar = tela.Button(
        janela,
        text="Ok",
        bg="green",
        fg="white",
        font=("Arial", 12, "bold"),
        command=clicar,
    )
    botao_avancar.pack(pady=15)

    mensagem_validacao = tela.Label(
    janela, 
    text="", 
    fg="green"
    )
    mensagem_validacao.pack()

# Função para tela final
def tela_final():
    limpar_tela()

    bw, h, d, d_linha, c, fck, mk, aco = viga

    lambda_c = parametros_calculo["lambda_c"]
    epsilon_cu = parametros_calculo["epsilon_cu"]
    fyd = parametros_calculo["fyd"]
    sigma_cd = parametros_calculo["sigma_cd"]
    fctk_sup = parametros_calculo["fctk_sup"]
    es = 21000  # kN/cm²

    md = 1.4 * mk
    xlim = parametros_calculo["xi_lim"] * d
    ylim = xlim * lambda_c
    mdlim = sigma_cd * bw * ylim * (d - ylim / 2)

    # Função padrão pra exibição de texto dentro da tela final
    def exibir(texto, **opcoes):
        tela.Label(janela, text=texto, **opcoes).pack(anchor="w", padx=15)

    # Função para exibição do erro de dimensionamento
    def erro_dimensionamento():
        exibir(
            "Valores insuficientes para o dimensionamento. Aumente h ou bw.",
            fg="red",
        )
        janela.after(5000, tela_inicial)

    def calcular_armadura(momento):
        if momento <= mdlim:
            y = d - sqrt(d ** 2 - 2 * momento / (sigma_cd * bw))
            x = y / lambda_c
            as_tracao = sigma_cd * bw * (lambda_c * x) / fyd
            return as_tracao, 0.0, False

        as1 = sigma_cd * bw * ylim / fyd
        delta_md = momento - mdlim
        epsilon_s2 = epsilon_cu * (xlim - d_linha) / xlim

        if d_linha >= xlim or epsilon_s2 <= 0:
            return None

        sigma_s2 = min(es * epsilon_s2, fyd)
        braco = d - d_linha
        as_compressao = delta_md / (braco * sigma_s2)
        delta_as = delta_md / (braco * fyd)

        return as1 + delta_as, as_compressao, as_compressao > as1

    exibir("Momento de Cálculo e Momento-Limite:", font=("Arial", 12, "bold"))
    exibir(f"Md: {md / 100:.2f} kN·m")
    exibir(f"Mdlim: {mdlim / 100:.2f} kN·m")
    exibir("Caso de Armadura Simples" if md <= mdlim else "Caso de Armadura Dupla")
    
    exibir("Valores de Armadura:", font=("Arial", 12, "bold"))

    armadura = calcular_armadura(md)
    if armadura is None:
        erro_dimensionamento()
        return

    as_tracao, as_compressao, secao_subdimensionada = armadura
    exibir(f"As: {as_tracao:.2f} cm²")
    exibir(f"As′: {as_compressao:.2f} cm²")

    if secao_subdimensionada:
        exibir("A seção está subdimensionada", font=("Arial", 9))

    wo = bw * h ** 2 / 6
    mdmin = 0.8 * wo * fctk_sup

    armadura_minima = calcular_armadura(mdmin)
    if armadura_minima is None:
        erro_dimensionamento()
        return

    asmincalc, as_compressao_minima, minimo_subdimensionado = armadura_minima

    asmin = max(asmincalc, 0.0015 * bw * h)
    exibir(f"Asmin: {asmin:.2f} cm²")

    if md <= mdlim < mdmin:
        exibir("O momento mínimo exige armadura dupla.")

    if secao_subdimensionada or minimo_subdimensionado:
        exibir("A seção está subdimensionada", font=("Arial", 9))

    asfinal = max(as_tracao, asmin)
    as_compressao_final = max(as_compressao, as_compressao_minima)

    exibir(f"Armadura de compressão adotada (As′): {as_compressao_final:.2f} cm²")
    resultado = f"Valor de Armadura adotado: {asfinal:.2f} cm²"

    if asfinal + as_compressao > 0.04 * bw * h:
        resultado += " — taxa máxima excedida"
        exibir(resultado, fg="red")
    else:
        exibir(resultado)

    tela.Button(
        janela,
        text="Finalizar",
        command=tela_inicial,
    ).pack(pady=15)
        
# Função para troca de tela após inserção de dados
def tela_parametros():
    
    # Seção para o cálculo dos parâmetros do concreto
    fck = viga[5]
    ca = viga[7]

    if fck <= 40:
      eta_c = 1.0
    else:
      eta_c = round((40 / fck) ** (1 / 3), 3)

    if fck <= 50:
      alfa_c = 0.85
      lambda_c = 0.8
      epsilon_cu = 0.0035
      xi_lim = 0.45
      fct_m = round(0.03 * fck ** (2/3), 3)
    else:
      alfa_c = round(0.85 * (1 - (fck - 50) / 200), 3)
      lambda_c = round(0.8 - (fck - 50) / 400, 3)
      epsilon_cu = round(0.0026 + 0.035 * ((90 - fck) / 100) ** 4, 4)
      xi_lim = 0.35
      fct_m = round(0.212 * log(1 + 0.11 * fck), 3)

    fctk_sup = fct_m * 1.3
    fcd = fck / 14

    fyd_por_classe = {"CA-50": 43.48, "CA-60": 52.17}
    fyd = fyd_por_classe[ca]

    sigma_cd = alfa_c * eta_c * fcd
    epsilon_yd = fyd / 21000

    #
    parametros_calculo.update({
        "lambda_c": lambda_c,
        "epsilon_cu": epsilon_cu,
        "xi_lim": xi_lim,
        "fyd": fyd,
        "sigma_cd": sigma_cd,
        "fctk_sup": fctk_sup,
    })

    limpar_tela()

    #Cria os botões de navegação
    rodape = tela.Frame(janela)
    rodape.pack(side="bottom", fill="x", padx=15, pady=12)

    tela.Button(
        rodape, text="Voltar", command=tela_inicial
    ).pack(side="left")

    tela.Button(
        rodape, text="Próximo", command=tela_final
    ).pack(side="right")

    # Exibe os dados da viga
    rotulos = campos + ["Resistência de Escoamento do Aço - fyk (MPa):"]
    valores_resumo = viga.copy()
    valores_resumo[6] /= 100  # Converte o momento informado em kN*cm para kN*m

    for rotulo, valor in zip(rotulos, valores_resumo):
      tela.Label(janela, text=f"{rotulo} {valor}").pack(
        anchor = "w", padx = 15
      )

    # Exibe uma mensagem intermediária
    tela.Label(
      janela,
      text="A partir do fck informado, foram deteriminados os parâmetros do concreto:",
      justify="left",
      wraplength=440
    ).pack(anchor="w", padx=15, pady=(12,6))

    parametros_concreto = [
      f"ηc: {eta_c:.3f}",
      f"αc: {alfa_c:.3f}",
      f"λ: {lambda_c:.3f}",
      f"εcu: {epsilon_cu:.4f}",
      f"ξlim: {xi_lim:.2f}",
      f"fct,m: {fct_m:.3f} kN/cm²",
      f"fctk,sup: {fctk_sup:.5f} kN/cm²",
      f"fcd: {fcd:.4f} kN/cm²",
      f"fyd: {fyd:.2f} kN/cm²",
      f"σcd: {sigma_cd:.4f} kN/cm²",
      f"εyd: {epsilon_yd:.6f}"
    ]

    # Exibe os parâmetros do concreto
    for texto in parametros_concreto:
      tela.Label(janela, text=texto).pack(anchor="w", padx=15)
  
# Função para validar os dados inseridos pelo usuário
def clicar():

    valores = []

    for i, campo in enumerate(entradas): 
      try:
        valor = float(campo.get())
      except ValueError:
        avisos[i].config(text=erro[i])    # Mostra o erro correspondente
        continue

      if not isfinite(valor) or (i <= 4 and valor <=0) or (i == 5 and not 20<= valor <=90) or (i == 6 and valor == 0):  # Assegura o preenchimento correto dos parâmetros numéricos
        avisos[i].config(text=erro[i])    # Mostra o erro correspondente
        continue

      if i == 6:
         valor = abs(valor) * 100  # Converte o momento informado em kN*m para kN*cm

      avisos[i].config(text="")
      valores.append(valor)               # Coleta os valores informados em 1-7

    classe_aco = opcao_aco.get()
    if not classe_aco:
      aviso_aco.config(text=erro[7])      # Mostra o erro correspondente
      return

    aviso_aco.config(text="")

    if len(valores) == len(entradas):
      h = valores[1]
      d = valores[2]
      d_linha = valores[3]

      altura_util_invalida = d >= h
      distancia_comprimida_invalida = d_linha >= d

      if altura_util_invalida:
        avisos[2].config(
            text="⚠️ Erro: A altura útil d deve ser menor que h."
        )

      if distancia_comprimida_invalida:
        avisos[3].config(
            text="⚠️ Erro: A distância d′ deve ser menor que d."
        )

      valores.append(classe_aco)          # Coleta a classe informado em 8
      viga[:] = valores

      mensagem_validacao.config(text="Dados da viga validados")   # Mensagem exibida quando todos dados são válidos
      botao_avancar.config(state="disabled")                      # Desativa o botão para evitar um eventual segundo comando de troca de tela
      janela.after(3000, tela_parametros)                    

tela_inicial()
janela.mainloop()