import numpy as np
from Estrategia import preprocessing, preprocessing_yf_


def SMA_strategy(input, mt5=False, yf=False):
    if mt5:
        df = preprocessing(input)

    if yf:
        df = preprocessing_yf_(input)

    # Creare resistencia Crear resistencia mediante un maximo rodante

    # Media Movil 30 dias
    df["SMA_Fast"] = df["close"].rolling(30).mean()

    # Media Movil 60 dias
    df["SMA_Slow"] = df["close"].rolling(80).mean()
    df["position"] = np.nan

    # Crear condiciones
    df.loc[(df["SMA_Fast"] > df["SMA_Slow"]), "position"] = 1
    df.loc[(df["SMA_Fast"] < df["SMA_Slow"]), "position"] = -1

    # Calcular las ganancias y perdidas
    #   Porcentaje de variacion
    df["pct"] = df["close"].pct_change(1)
    #   Calcular Rentabilidad (Retoro) de variacion del activo
    df["return"] = df["pct"] * df["position"].shift(1)

    return df["return"]


SMA_strategy("BTC-USD", yf=True).cumsum().plot(figsize=(15, 8))
