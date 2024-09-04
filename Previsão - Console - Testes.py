import requests
import time
from colorama import Fore, Style

# Sequência específica de números ordenados
numeros_ordenados = [0, 26, 3, 35, 12, 28, 7, 29, 18, 22, 9, 31, 14, 20, 1, 33, 16, 24, 5, 10, 23, 8, 30, 11, 36, 13, 27, 6, 34, 17, 25, 2, 21, 4, 19, 15, 32]

def calcular_custo_fichas(numeros_previstos, valor_ficha=5):
    # Calcula o custo total das fichas considerando os números previstos e seus vizinhos
    quantidade_numeros_previstos = len(numeros_previstos)
    quantidade_vizinhos = quantidade_numeros_previstos * 6  # Cada número previsto tem 6 vizinhos
    custo_total = (quantidade_numeros_previstos + quantidade_vizinhos) * valor_ficha
    return custo_total

# Função para fazer a requisição à API e armazenar os resultados
def buscar_resultado():
    url = 'https://api.casinoscores.com/svc-evolution-game-events/api/immersiveroulette/latest'
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
def prever_proximo_numero(numero_atual, padrao_encontrado):
    if padrao_encontrado:
        # Prever os números 1, 5, 8, 6, 2, 3 com 1 vizinho para cada lado
        proximos = [1, 5, 8, 6, 2, 3, 0, 36]
    else:
        # Prever apenas os números 0 e 36 sem escolher os vizinhos
        proximos = [0, 36]
    return proximos

# Função para analisar se o número está entre os previstos ou entre os vizinhos
def analisar_vizinhos(numero_atual, numeros_previstos, saldo, valor_ficha=5):
    if numeros_previstos:
        # Ordena os números previstos de acordo com a lista numeros_ordenados
        numeros_previstos.sort(key=lambda x: numeros_ordenados.index(x))        
        if numero_atual in numeros_previstos:          

            ganho = 36 * valor_ficha # Ganho é multiplicado pelo valor da ficha
            if len(numeros_previstos) == 3:
                ganho_real = ganho - 100
            elif len(numeros_previstos) == 4:
                ganho_real = ganho - 135
            saldo += ganho_real
            print(Fore.GREEN + f"Ganho: + R$ {ganho}" + Style.RESET_ALL)                        
            print(Fore.GREEN + f"Lucro Real: + R$ {ganho_real}" + Style.RESET_ALL)                        
            print("Saldo atual: R$", saldo)
            return Fore.GREEN + f"GANHO PREVISTO $ - (Número: {numero_atual})" + Style.RESET_ALL, saldo        
        else:
            # Encontra os vizinhos de cada número previsto, respeitando o ordenamento definido da roleta
            vizinhos_previstos = []
            
            for num_previsto in numeros_previstos:
                indice_num_previsto = numeros_ordenados.index(num_previsto)
                vizinhos_indices = [(indice_num_previsto + i) % len(numeros_ordenados) for i in range(-3, 4)]
                vizinhos_previstos.extend([numeros_ordenados[i] for i in vizinhos_indices])
                
            # Verifica se o número atual está entre os vizinhos dos números previstos
            if numero_atual in vizinhos_previstos: 

                ganho = 36 * valor_ficha  # Ganho é multiplicado pelo valor da ficha
                if len(numeros_previstos) == 3:
                    ganho_real = ganho - 100                
                elif len(numeros_previstos) == 4:
                    ganho_real = ganho - 135
                saldo += ganho_real
                print(Fore.GREEN + f"Ganho: + R$ {ganho}" + Style.RESET_ALL)                        
                print(Fore.GREEN + f"Lucro Real: + R$ {ganho_real}" + Style.RESET_ALL)                        
                print("Saldo atual: R$", saldo)
                return Fore.GREEN + f"GANHO $ - Acerto de Vizinho (Número: {numero_atual})" + Style.RESET_ALL, saldo
            else:
                custo_fichas = calcular_custo_fichas(numeros_previstos, valor_ficha)
                saldo -= custo_fichas
                print(Fore.RED + f"Perda: - R$ {custo_fichas}" + Style.RESET_ALL)
                print("Saldo atual: R$", saldo)
                return Fore.RED + f"PERDA $ - Número não previsto (Número: {numero_atual})" + Style.RESET_ALL, saldo
    else:
        return Fore.YELLOW + "Primeira rodada, aguardando previsões...\n" + Style.RESET_ALL, saldo

def escutar_api(saldo_inicial=500, valor_ficha=5):
    saldo = saldo_inicial
    numeros_previstos = []
    rodadas_esperadas = 3
    rodadas_contadas = 0
    padrao_encontrado = False
    ultimo_numero = None
    
    while True:
        resultado = buscar_resultado()
        if resultado:
            novo_numero = resultado['numero']
            
            if novo_numero < 10:
                rodadas_contadas += 1
                
                if rodadas_contadas == rodadas_esperadas:
                    padrao_encontrado = True
                    
            else:
                rodadas_contadas = 0
                
            if novo_numero != ultimo_numero:  # Verifica se é um novo número
                novos_numeros_previstos = prever_proximo_numero(novo_numero, padrao_encontrado)
                print("Número atual:", Fore.YELLOW + str(novo_numero) + Style.RESET_ALL)
                print("Próximos números previstos:", end=" ")
                for num in novos_numeros_previstos:
                    print(Fore.BLUE + str(num) + Style.RESET_ALL, end=" ")
                print()
                analise, saldo = analisar_vizinhos(novo_numero, numeros_previstos, saldo, valor_ficha)
                if analise:
                    print("Análise:", analise, "\n")
                numeros_previstos = novos_numeros_previstos
                ultimo_numero = novo_numero
            else:
                print("Número repetido. Aguardando novo número...\n")
            time.sleep(1)


# Chamada da função para começar a escutar a API
escutar_api()
