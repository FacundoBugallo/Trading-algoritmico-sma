import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from Estrategia import drawndown_function, return_serie

serie = return_serie


def BackTest(serie, annualiazed_scalar=364):
    # Importar los datos de Ethereum
    eth = yf.download("ETH-USD")["Adj Close"].pct_change(1)
    eth.name = "ETH-USD"

    # Concatenar los retornos de la serie y Ethereum
    val = pd.concat((serie, eth), axis=1).dropna()

    # Calcular el drawdown
    drawdown = drawndown_function(serie) * 100

    # Calcular el maxdrawdown
    max_drawdown = -np.min(drawdown)

    # Crear subplots
    fig, (cum, dra) = plt.subplots(1, 2, figsize=(15, 6))

    # Título principal
    fig.suptitle("BackTesting", size=20)

    # Gráfico de rendimientos acumulados
    cum.plot(serie.cumsum() * 100, color="#39B3C7")
    cum.plot(val["ETH-USD"].cumsum() * 100, color="#B85A0F")

    # Leyenda
    cum.legend(["PortFolio", "ETH-USD"])

    # Títulos
    cum.set_title("Cumulative Return", size=13)
    cum.set_ylabel("Cumulative Return %", size=11)

    # put the drawdown
    dra.fill_between(drawdown.index, 0, drawdown, color="#C73954")

    # titulos
    dra.set_title("Drawdown", size=13)
    dra.set_ylabel("Drawdown in %", size=11)

    plt.show()

    # Calcular el índice Sortino
    sortino = np.sqrt(annualiazed_scalar) * serie.mean() / \
        serie.loc[serie < 0].std()

    # Calcular el índice beta
    beta = np.cov(val[["return", "ETH-USD"]].values,
                  rowvar=False)[0][1] / np.var(val["ETH-USD"].values)

    # Calcular el índice alpha
    alpha = annualiazed_scalar * (serie.mean() - beta * serie.mean())

    # Imprimir estadísticas
    print(f"Sortino: {np.round(sortino,3)}")
    print(f"Beta: {np.round(beta, 3)}")
    print(f"Alpha: {np.round(alpha * 100, 3)} %")
    print(f"MaxDrawdown: {np.round(max_drawdown, 3)} %")


BackTest(serie, annualiazed_scalar=364)
