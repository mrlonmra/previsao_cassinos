import requests
import time
import tkinter as tk
from tkinter import ttk
from colorama import Fore, Style
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Variáveis para armazenar o número de ganhos e perdas
num_ganhos = 0
num_perdas = 0

# Listas para armazenar os dados do gráfico
eixo_x = []
eixo_y = []

# Variável para controlar a primeira análise
primeira_analise = True

# Função para fazer a requisição à API e armazenar os resultados
def buscar_resultado():
    url = 'https://api.casinoscores.com/svc-evolution-game-events/api/xxxtremelightningroulette/latest'
    response = requests.get(url)
    if response.status_code == 200:
        resultado = response.json()['data']['result']
        numero = resultado['outcome']['number']
        tipo = resultado['outcome']['type']
        cor = resultado['outcome']['color']
        return {'numero': numero, 'tipo': tipo, 'cor': cor}
    else:
        print("Falha ao buscar o resultado da API")
        return None

# Função para prever o próximo número com base no número atual
def prever_proximo_numero(numero_atual):
    ultimo_digito = numero_atual % 10
    proximos = []
    for i in range(0, 37):
        if i % 10 == ultimo_digito:
            proximos.append(i)
    return proximos

# Função para calcular os números vizinhos abaixo dos próximos números previstos
def calcular_vizinhos(numeros_previstos):
    vizinhos = []
    for numero in numeros_previstos:
        for i in range(numero - 3, numero):
            if i >= 0:
                vizinhos.append(i)
    return vizinhos

# Função para analisar se o número está entre os previstos ou entre os vizinhos
def analisar_vizinhos(numero_atual, numeros_previstos):
    global num_ganhos, num_perdas, primeira_analise
    if primeira_analise:
        primeira_analise = False
        return "Primeira análise"
    
    if numeros_previstos:
        if numero_atual in numeros_previstos:
            num_ganhos += 1
            return Fore.GREEN + "GANHO $ - Na cabeça" + Style.RESET_ALL
        elif any(abs(numero_atual - numero) <= 3 for numero in numeros_previstos):
            num_ganhos += 1
            return Fore.GREEN + "GANHO $ - Vizinhos" + Style.RESET_ALL
    num_perdas += 1
    return Fore.RED + "LOSS $" + Style.RESET_ALL

# Função para escutar a API e armazenar os resultados
def escutar_api():
    numeros_previstos = []
    ultimo_numero = None
    
    # Função para atualizar a interface gráfica com os resultados
    def atualizar_interface(ultimo_numero):
        global num_ganhos, num_perdas, eixo_x, eixo_y
        resultado = buscar_resultado()
        if resultado:
            novo_numero = resultado['numero']
            if novo_numero != ultimo_numero:
                novos_numeros_previstos = prever_proximo_numero(novo_numero)
                numero_atual_label.config(text=f"Número atual: {novo_numero}", foreground='black')
                numeros_previstos_label.config(text="Próximos números previstos: " + " ".join(map(str, novos_numeros_previstos)), foreground='blue')
                
                # Calcula e exibe os números vizinhos abaixo dos próximos números previstos
                vizinhos = calcular_vizinhos(novos_numeros_previstos)
                vizinhos_label.config(text="Números vizinhos Previstos: " + " - ".join(map(str, vizinhos)), foreground='orange')
                
                analise = analisar_vizinhos(novo_numero, numeros_previstos)
                analise_label.config(text="Análise: " + analise, foreground='green' if 'GANHO' in analise else 'red')
                numeros_previstos[:] = novos_numeros_previstos
                ultimo_numero = novo_numero
                
                # Atualiza o gráfico
                eixo_x.append(len(eixo_x) + 1)
                eixo_y.append(num_ganhos - num_perdas)
                ax.clear()
                ax.plot(eixo_x, eixo_y, marker='o', linestyle='-')
                ax.set_title('Ganhos e Perdas ao longo do tempo')
                ax.set_xlabel('Rodadas')
                ax.set_ylabel('Acertos')
                canvas.draw()
                
                # Atualiza a área de texto
                texto_area.delete('1.0', tk.END)
                total_jogadas = num_ganhos + num_perdas
                if total_jogadas > 0:
                    porcentagem_ganhos = (num_ganhos / total_jogadas) * 100
                    porcentagem_perdas = (num_perdas / total_jogadas) * 100
                else:
                    porcentagem_ganhos = 0.0
                    porcentagem_perdas = 0.0

                texto_area.insert(
                    tk.END, f"Ganhos: {num_ganhos}\nPerdas: {num_perdas}\nPorcentagem de Ganhos: {porcentagem_ganhos:.2f}%\nPorcentagem de Perdas: {porcentagem_perdas:.2f}%")

        # Utiliza lambda para passar o valor de ultimo_numero
        root.after(1000, lambda: atualizar_interface(ultimo_numero))

    # Configuração da interface gráfica
    root = tk.Tk()
    root.title("Análise de resultados de roleta")

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0)

    numero_atual_label = ttk.Label(
        frame, text="Número atual: ", font=('Helvetica', 12))
    numero_atual_label.grid(row=0, column=0, sticky="w")

    numeros_previstos_label = ttk.Label(
        frame, text="Próximos números previstos: ", font=('Helvetica', 12))
    numeros_previstos_label.grid(row=1, column=0, sticky="w")
    
    vizinhos_label = ttk.Label(
        frame, text="Números vizinhos abaixo: ", font=('Helvetica', 12))
    vizinhos_label.grid(row=2, column=0, sticky="w")

    analise_label = ttk.Label(frame, text="Análise: ", font=('Helvetica', 12))
    analise_label.grid(row=3, column=0, sticky="w")

    # Configuração do gráfico
    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().grid(row=4, column=0)

    # Configuração da área de texto
    texto_area = tk.Text(frame, height=4, width=40, font=('Helvetica', 12))
    texto_area.grid(row=5, column=0, pady=10)

    # Inicia a atualização da interface com o valor inicial de ultimo_numero
    atualizar_interface(ultimo_numero)

    root.mainloop()


# Chamada da função para começar a escutar a API
escutar_api()
