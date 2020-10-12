import pandas as pd
import json

from datetime import datetime
from datetime import timedelta

'''

Es identico al caso 5 pero se vuelve al modelo BINARIO y en la variacion de consumo no se utiliza franja.
Variables sin NORMALIZADAR.

'''


def generar_corpus_9(path_data, path_aggregate, consumo_standby, interval_size, escribir_archivo):

    # Cargo los dataframes utilizando indices por defecto 0 .. CANTIDAD_ENTRADAS_ARCHIVO
    agg_file_panda = pd.read_csv(path_aggregate, sep=" ", header=None)
    agg_file_panda.columns = ["Timestamp", "Consumo"]

    app_file_panda = pd.read_csv(path_data, sep=" ", header=None)
    app_file_panda.columns = ["Timestamp", "Consumo"]

    # Vectores de entrenamiento
    vectores_entrada = []
    predicciones_entrada = []

    estado_ant = 0                  # Indica ON/OFF en intervalo anterior
    consumo_anterior = 0

    fin = False

    # Estas variables determinan los limites del intervalo de tiempo
    range_start = datetime.fromtimestamp(app_file_panda.iloc[0]['Timestamp'])
    range_end = range_start + timedelta(seconds=interval_size)

    # Limites de las ventanas de avance sobre los archivos
    first_index = app_file_panda.first_valid_index()
    last_index = app_file_panda.last_valid_index() + 1
    first_index_agg = agg_file_panda.first_valid_index()
    last_index_agg = agg_file_panda.last_valid_index() + 1

    avance = 0

    while not fin:

        avance += 1

        if avance % 500000 == 0:
            print("Avance: " + str(avance) + "/" + str(last_index))

        # Indices dentro del intervalo
        registros_aplicacion = []
        registros_agregados = []

        # ********************** SE BUSCAN LAS MEDIDAS DENTRO DEL INTERVALO **********************

        # Hallas las medidas de la aplicacion dentro del intervalo
        for i in range(first_index, last_index):

            actual_time = datetime.fromtimestamp(app_file_panda.iloc[i]['Timestamp'])

            if (actual_time >= range_start) and (actual_time < range_end):
                registros_aplicacion.append(i)

            # Si el tiempo actual supera el tope del intervalo se finaliza la iteracion
            if actual_time >= range_end:
                first_index = i
                break

            # Si se llego a la ultima medida del archivo se finaliza el while
            if i == last_index - 1:
                fin = True

        # Hallas las medidas de consumo agregado dentro del intervalo
        for i in range(first_index_agg, last_index_agg):
            actual_time = datetime.fromtimestamp(agg_file_panda.iloc[i]['Timestamp'])

            if (actual_time >= range_start) and (actual_time <= range_end):
                registros_agregados.append(i)

            if actual_time >= range_end:
                first_index_agg = i
                break

        # Se actualizan los limites del intervalo
        range_start = range_end
        range_end = range_start + timedelta(seconds=interval_size)

        # Si para la aplicacion o el agregado no se tienen medidas dentro del intervalo, este se descarta
        if (len(registros_aplicacion) == 0) or (len(registros_agregados) == 0):
            continue

        # ********************** FEATURE CONSUMO_AGREGADO **********************
        cont_enc = 0
        consumo_intervalo_app = 0

        # Se cuenta la cantidad de medidas que superan el stanby dentro del intervalo
        for j in registros_aplicacion:
            if app_file_panda.iloc[j]['Consumo'] > consumo_standby:
                cont_enc += 1
                consumo_intervalo_app += app_file_panda.iloc[j]['Consumo']

        # El aparato se considera encendido si la mitad de los valores superan el stanby
        if cont_enc >= len(registros_aplicacion) / 2:
            consumo_agregado_aux = 0

            for i in registros_agregados:
                consumo_agregado_aux += agg_file_panda.iloc[i]['Consumo']

            # Promedio de consumo agregado en el intervalo
            consumo_agregado = round(consumo_agregado_aux / len(registros_agregados))

            # Actualizacion del estado actual
            estado_act = 1

        else:
            # Si el aparato se considera apagado su consumo se resta al agregado
            consumo_agregado_aux = 0

            for i in registros_agregados:
                consumo_agregado_aux += agg_file_panda.iloc[i]['Consumo']

            # Promedio de consumo agregado en el intervalo
            consumo_agregado = round((consumo_agregado_aux - consumo_intervalo_app) / len(registros_agregados))

            # Se actualiza el encendido actual a OFF
            estado_act = 0

        # **********************  GENERACION VECTORES **********************
        vector_entrada = \
            [consumo_agregado - consumo_anterior]

        vectores_entrada.append(vector_entrada)

        # Genera el vector de salida
        predicciones_entrada.append(estado_act)

        # ********************** ACTUALIZACION DE VARIABLES **********************

        # El encendido anterior del proximo paso corresponde al encendido actual
        estado_ant = estado_act

        # Se actualiza el valor del consumo agregao anterior para el proximo paso
        consumo_anterior = consumo_agregado




        max_diferencia = 1

        # Hallo los maximos
    for i in vectores_entrada:
        if i[0] > max_diferencia:
            max_diferencia = i[0]
    print(max_diferencia)

    # ********************** ESCRIBIR **********************

    if escribir_archivo:
        store = {
            "features": vectores_entrada,
            "activations": predicciones_entrada
        }

        directories_file = path_data.split('/')
        file_name = directories_file[-1]

        file = open(file_name + "_generar_corpus_9", "w+")
        file.write(json.dumps(store))
        file.close()

    return vectores_entrada, predicciones_entrada


if __name__ == "__main__":
    _path_to_generate = "/home/ignacio/Escritorio/Respaldo/tesis/src/house_1/channel_12.dat_80"
    _path_aggregate = "/home/ignacio/Escritorio/Respaldo/tesis/src/house_1/channel_1.dat"
    _consumo_standby = 50
    _interval_size = 30
    _escribir_archivo = True

    generar_corpus_9(_path_to_generate, _path_aggregate, _consumo_standby, _interval_size, _escribir_archivo)

