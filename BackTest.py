import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from Estrategia import drawndown_function, return_serie


def BackTest(serie, annualiazed_scalar=364):

    # Importar el benchmark
    btc = yf.download("BTC-USD")["Adj Close"].pct_change(1)
    btc.name = "BTC-USD"

    # Concatenar los retornos y el sp500
    val = pd.concat((serie, btc), axis=1).dropna()

    # Calcular el drawdown
    drawdown = drawndown_function(serie)*100

    # Calcular el maxdrawdown
    max_drawdown = -np.min(drawdown)

    # put a subplots
    fig, (cum, dra) = plt.subplots(1, 2, figsize=(20, 6))

    # put a suptitle
    fig.suptitle("BackTesting", size=20)

    # Returns cumsum chart
    cum.plot(serie.cumsum()*100, color="#39B3C7")

    # BTC cumsum chart
    cum.plot(val["BTC-USD"].cumsum()*100, color="#B85A0F")

    # put a legend
    cum.legend(["PortFolio", "BTC-USD"])

    # set individual title
    cum.set_title("Cumulative Return", size=13)
    cum.set_ylabel("cumutative Return %", size=11)

    plt.show()

    # cauclular el indice sortino
    sortino = np.sqrt(annualiazed_scalar) * serie.mean() / \
        serie.loc[serie < 0].std()

    # calcular el indice beta
    beta = np.cov(val[["return", "BTC-USD"]].values,
                  rowvar=False)[0][1]/np.var(val["BTC-USD"].values)

    # Calcular indice alpha
    alpha = annualiazed_scalar * (serie.mean() - beta*serie.mean())

    # imprimir estadisticos
    print(f"Sortino: {np.round(sortino,3)}")
    print(f"Beat: {np.round(beta, 3)}")
    print(f"alpha: {np.round(alpha*100, 3)} %")
    print(f"MaxDrawndown:{np.round(max_drawdown, 3)} %")


BackTest(return_serie, annualiazed_scalar=364)
