#Passo1:Listar as abas disponíveis na planilha baixada
import pandas as pd

#Caminho referente à pasta onde se encontram armazenados os dados do Itaú Unibanco
excel_path = r"C:\Users\conta\itau_dfc_analysis\data\Kit do investidor 4T24\Kit do investidor 4T24\Planilha_Series_Historicas_BRGAAP_IFRS_4T24.xlsx"

# Criar um objeto ExcelFile para listar as abas
xls = pd.ExcelFile(excel_path)
print("Abas disponíveis na planilha:")
print(xls.sheet_names)

#Passo2: Com o nome da provável aba do DRE, vamos acessar seus valores e extrair Lucro Líquido de 2020 a 2024
import pandas as pd

# Definir caminho do arquivo e aba do Excel
excel_path = r"C:\Users\conta\itau_dfc_analysis\data\Kit do investidor 4T24\Kit do investidor 4T24\Planilha_Series_Historicas_BRGAAP_IFRS_4T24.xlsx"
sheet_name = "BRGAAP - DRE"

# Carregar os dados
df = pd.read_excel(excel_path, sheet_name=sheet_name)

# Exibir os nomes das colunas para depuração
print("Nomes das colunas no DataFrame:")
print(df.columns)

# Definir os anos corretamente (como inteiros)
anos = [2020, 2021, 2022, 2023, 2024]

# Localizar a linha do Lucro Líquido
linha_lucro = df[df.iloc[:, 0].astype(str).str.contains("LUCRO LÍQUIDO", na=False, case=False)]

if linha_lucro.empty:
    raise ValueError("Não foi possível encontrar a linha do Lucro Líquido.")

# Selecionar os dados do Lucro Líquido para os anos desejados
lucro_liquido = linha_lucro.iloc[:, [df.columns.get_loc(ano) for ano in anos]]

# Exibir os valores extraídos
print("Lucro Líquido por ano:")
print(lucro_liquido)

#Fizemos algo parecido para achar o Patrimônio Líquido (Dezembro de cada ano de 2020 a 2024 - Valor consolidado)
import pandas as pd
import datetime
import re

# Caminho do arquivo Excel
excel_path = r"C:\Users\conta\itau_dfc_analysis\data\Kit do investidor 4T24\Kit do investidor 4T24\Planilha_Series_Historicas_BRGAAP_IFRS_4T24.xlsx"

# Definir a aba que contém os dados do Balanço – Passivo e PL
sheet_name = "BRGAAP - Balanço - Passivo e PL"

# Carregar os dados da aba
df = pd.read_excel(excel_path, sheet_name=sheet_name)

# Exibir os nomes das colunas para verificação
print("Nomes das colunas no DataFrame:")
print(df.columns)

# Lista dos anos de interesse
anos = [2020, 2021, 2022, 2023, 2024]

# Encontrar a linha que contém "PATRIMÔNIO LÍQUIDO" na primeira coluna.
linha_pl = df[df.iloc[:, 0].astype(str).str.contains("PATRIMÔNIO LÍQUIDO", na=False, case=False)]
if linha_pl.empty:
    raise ValueError("Linha do Patrimônio Líquido não encontrada!")

# Construir um mapeamento para as colunas de fechamento de dezembro.
# A ideia é identificar, dentre as colunas, aquelas que possuem atributo "month" e são do mês 12.
dez_columns = {}
for col in df.columns:
    # Tentamos usar o atributo 'month': se o objeto tiver esse atributo e for dezembro, processamos.
    if hasattr(col, 'month'):
        try:
            if col.month == 12:
                # Formata a data para "dez-XX" (ex: 31/12/2020 -> "dez-20")
                key = col.strftime("dez-%y")
                dez_columns[key] = col
        except Exception as e:
            # Se ocorrer algum erro, apenas ignore essa coluna
            pass
    # Se a coluna já for string e estiver no padrão "dez-XX", também a incluímos.
    elif isinstance(col, str):
        match = re.match(r"dez-(\d{2})", col.lower())
        if match:
            key = col.lower()
            dez_columns[key] = col

print("Mapping de colunas de dezembro encontrado:")
print(dez_columns)

# Agora, para cada ano, procurar a coluna correspondente.
pl_por_ano = {}
for ano in anos:
    # Cria a chave: para 2020, será "dez-20"; para 2021, "dez-21", etc.
    ano_key = f"dez-{str(ano)[-2:]}"
    if ano_key in dez_columns:
        coluna = dez_columns[ano_key]
        valor_pl = linha_pl[coluna].values[0]
        pl_por_ano[ano] = valor_pl
    else:
        print(f"Coluna {ano_key} não encontrada para o ano {ano}.")

print("\nPatrimônio Líquido (PL) por ano:")
for ano, valor in pl_por_ano.items():
    print(f"{ano}: {valor}")

#Passo 4: Precisamos achar a taxa livre de risco (treasures americanos de 10 anos) e usamos a biblioteca do yahoo finance, o que dispensa webscrappling

import yfinance as yf

# Definir o ticker para o 10-year Treasury yield (proxy da taxa livre de risco)
ticker = yf.Ticker("^TNX")

# Obter os dados históricos, aqui pegamos o último dia disponível
data = ticker.history(period="1d")

# Extrair o valor de fechamento (Close)
# O valor retornado costuma estar em pontos percentuais, por exemplo: 2.5 equivale a 2,5%
risk_free_rate_percent = data["Close"].iloc[-1]
risk_free_rate = risk_free_rate_percent / 100  # Converter para decimal

print("Taxa livre de risco (10-year Treasury): {:.2%}".format(risk_free_rate))

#Passo 5: Calculamos o Rm (retorno esperado) e usamos os dados historicos do ibovespa via yahoo finance para calcular essa taxa

import yfinance as yf

# Baixar dados do IBOVESPA (código "^BVSP" no Yahoo Finance)
ibov = yf.download("^BVSP", start="2000-01-01", end="2024-01-01", interval="1mo")["Adj Close"]

# Mostrar as primeiras linhas
print(ibov.head())

import pandas as pd

# Converter para retornos anuais
ibov_annual = ibov.resample("Y").last()  # Pega o último valor do ano
returns = ibov_annual.pct_change().dropna()  # Calcula a variação percentual

# Média dos retornos
rm = returns.mean() * 100  # Convertendo para porcentagem
print(f"Retorno médio anual do Ibovespa: {rm:.2f}%")

#Passo 6: Calculamos o Prêmio de risco (Rm-Rf)

Rf = 4.54 / 100  # Taxa livre de risco (exemplo: 4.54%)
Rm = rm / 100  # Retorno médio do Ibovespa
premium = Rm - Rf

print(f"Prêmio de risco do mercado: {premium * 100:.2f}%")

#Passo 7: Calcular Beta do Itaú. Primeiro usarusando a biblioteca yfinance para pegar os preços ajustados do Itaú (código ITUB4.SA) e do Ibovespa (^BVSP).

import yfinance as yf

# Baixar dados históricos
itau = yf.download("ITUB4.SA", start="2010-01-01", end="2024-01-01", interval="1mo")["Adj Close"]
ibov = yf.download("^BVSP", start="2010-01-01", end="2024-01-01", interval="1mo")["Adj Close"]

#variação percentual dos preços para obter retornos mensais

import pandas as pd

# Calcular retornos logarítmicos mensais
ret_itau = itau.pct_change().dropna()
ret_ibov = ibov.pct_change().dropna()

# Unir os retornos em um dataframe
df = pd.DataFrame({"ITAU": ret_itau, "IBOV": ret_ibov}).dropna()
print(df.head())

#estimar o Beta via regressão linear
import numpy as np

# Calcular a covariância e variância
cov = np.cov(df["ITAU"], df["IBOV"])[0, 1]  # Covariância entre ITAU e IBOV
var_ibov = np.var(df["IBOV"])  # Variância do IBOV

# Calcular Beta
beta_itau = cov / var_ibov
print(f"Beta do Itaú: {beta_itau:.2f}")

#Passo 8: Calcular o valor da empresa fazendo calculo do ROE de cada periodo e do Excess returns usando também o patrimonio líquido e trazendo aos valores presentes
# Definir dados do Itaú (em milhões)
lucro_liquido = {2020: 18909.0, 2021: 24988.0, 2022: 29414.0, 2023: 33368.0, 2024: 40231.0}
patrimonio_liquido = {2020: 147706.0, 2021: 155576.0, 2022: 169735.0, 2023: 188935.0, 2024: 210457.0}

# Definir Ke (custo de capital)
Ke = 0.1521  # 15.21%

# Calcular o ROE para cada ano (Lucro Líquido / Patrimônio Líquido)
ROE = {ano: lucro_liquido[ano] / patrimonio_liquido[ano] for ano in lucro_liquido}

# Calcular o Excess Return para cada ano (ROE - Ke)
Excess_Return = {ano: ROE[ano] - Ke for ano in ROE}

# Calcular o valor presente do Excess Return para cada ano (descontado por Ke)
valor_excess_return = {ano: Excess_Return[ano] / (1 + Ke)**(2024 - ano) for ano in Excess_Return}

# Somar o valor presente dos Excess Returns e o Patrimônio Líquido de 2024
valor_empresa = patrimonio_liquido[2024] + sum(valor_excess_return.values())

# Exibir o resultado
print(f"Valor da empresa (valuation): R${valor_empresa:,.2f} milhões")

