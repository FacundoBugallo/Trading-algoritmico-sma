from matplotlib import cycler
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
import warnings
warnings.filterwarnings("ignore")

# SetUp

colors = cycler('color', ['#669FEE', '#66EE91',
                          '#9988DD', '#EECC55', '#88BB44', '#FFBBBB'])
plt.rc('figure', facecolor='#313233')
plt.rc('axes', facecolor='#313233', edgecolor='none', axisbelow=True,
       grid=True, prop_cycle=colors, labelcolor='gray')
plt.rc('grid', color='474A4A', linestyle='solid')
plt.rc('xtick', color='gray')
plt.rc('ytick', direction='out', color='gray')
plt.rc('legend', facecolor='#313233', edgecolor='#313233')
plt.rc('text', color='#C9C9C9')

# Funcion de preprocesado

# ------------------PRCESAMOS LOS DATOS----------------------


def preprocessing(name):

    # importar datos
    df = pd.read_csv(name, delimitar="\t", index_col="<DATE>",
                     parse_dates=True).dropna()

    # Eliminar las ultimas dos col
    df = df.iloc[:, :-2]

    # Renombrar
    df.columna = ["open", "higt", "low", "close", "volumen"]
    df.index.name = "time"

    return df


def preprocessing_yf_(symbol):

    # Importar los datos
    df = yf.download(symbol).dropna()

    # renombrar
    df.columns = ["open", "higt", "low", "close", "adjclose", "volumen"]
    df.index.name = "time"

    # eliminar la columna  adjclose
    del df["adjclose"]

    return df


df = preprocessing_yf_("BTC-USD")

# ------------------------------------------------------


# --------------------CREAMOS LA MEDIA-----------------

# Media Movil 30 dias
# Junta 30 vultimos valores y sacamos la media
df["SMA_Fast"] = df["close"].rolling(30).mean()

# Media Movil 60 dias
df["SMA_Slow"] = df["close"].rolling(80).mean()

# Plot resultado
df[["close", "SMA_Fast", "SMA_Slow"]].plot(figsize=(15, 8))
df[["close", "SMA_Fast", "SMA_Slow"]].loc["2018"].plot(figsize=(15, 8))

# -----------------------------------------------------

# --------------------CREAMOS LA ESTRATEGIA-------------

# Estrategia
df["position"] = np.nan  # ---> GUARDAREMOS LA OPERACOION

# Crear la condiciones
df.loc[(df["SMA_Fast"] > df["SMA_Slow"]), "position"] = 1
df.loc[(df["SMA_Fast"] < df["SMA_Slow"]), "position"] = -1

# --------------------GRAFICAMOS LA ESTRATEGIA-----------
# Representamos en una grafica las señales de la estrategia

year = "2020"

#   seleccionamos tolas las señaes en una lista de indices
#    para representar solo estos puntos

idx_open = df.loc[df["position"] == 1].loc[year].index
idx_close = df.loc[df["position"] == -1].loc[year].index


# Grafico
plt.figure(figsize=(15, 6))
plt.scatter(idx_open, df.loc[idx_open]
            ["close"].loc[year], color="#57CE95", marker="^")
plt.scatter(idx_close, df.loc[idx_close]
            ["close"].loc[year], color="red", marker="v")


plt.plot(df["close"].loc[year].index, df["close"].loc[year], alpha=0.35)

plt.plot(df["close"].loc[year].index, df["SMA_Fast"].loc[year], alpha=0.35)

plt.plot(df["close"].loc[year].index, df["SMA_Slow"].loc[year], alpha=0.35)

plt.show()

# -----------------------------------------------------------

# -----------------CALCULAR LAS GANACIAS---------------------

#   Porcentaje de variacion del activo
df["pct"] = df["close"].pct_change(1)

#   Calcular Rentabilidad(Retorno) de la estrategia
df["return"] = df["pct"] * df["position"].shift(1)
df["return"].plot(figsize=(15, 8))

# balanze diario (1%, 3%, -1%) --> balanze acumulado (1%, 4%, -1%)
df["return"].cumsum().plot(figsize=(15, 8))

# ------------------------------------------------------------

# ----------------Calcular metricas----------------------------

# Preparar datos
btc = yf.download("BTC-USD", end="2024-04-04")
return_serie = btc["Adj Close"].pct_change(1).dropna()
return_serie.name = "return"


# Sortino


# En el indice de sortino se tiene en cuenta la volatiidad negativa
# Calcular el indice de sortino
mean = np.mean(return_serie)
vol = np.std(return_serie[return_serie < 0])
sortino = np.sqrt(365) * mean/vol

print(f"Sortino: {'%.3f' % sortino}")
# funcionan las 24 horas del día, los 365 días del año
# por eso multimplicamos la media por 365 dia para anualizarlo


# Beta
# Necesitamos calcular la covatianza entre el mercado y la cartera
# pct_change --> porcentaje de cambio dirario
eth = yf.download("ETH-USD")["Adj Close"].pct_change(1)
eth.name = "ETH-USD"

# Los concatenamos para hacer la covarianza
val = pd.concat((return_serie, eth), axis=1).dropna()
val

# Calculamos la matriz de covarianzas
cov_var_mat = np.cov(val.values, rowvar=False)
cov_var_mat

# Cauclulamos beta
cov = cov_var_mat[0][1]
var = cov_var_mat[1][1]

beta = cov/var
# Drawdown
print(f"Beta: {'%.3f' % beta}")


def drawndown_function(serie):
    # Calcula la suma de los rendimientos
    cum = serie.dropna().cumsum() + 1
    # Calculamos el maximo  de la suma en el periodo (MaximoAcumulado)
    running_max = np.maximum.accumulate(cum)
    # Calculamos la metrica Drawdown
    drawndown = cum/running_max - 1
    return drawndown


drawndown = drawndown_function(return_serie)

plt.fill_between(drawndown.index, drawndown*100, 0,
                 drawndown, color="#CE5757", alpha=0.65)
plt.title("DrawnDown")
plt.ylabel("DrawnDown en %")
plt.show()
