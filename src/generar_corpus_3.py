import pandas as pd
import json

from datetime import datetime
from datetime import timedelta

'''

Para evitar descartar datos, se discretiza el tiempo tomando intervalos de 30 segundos.
MODELO BINARIO donde se considera encendido el aparato si mas de la mitad de los consumos 
supera cierto valor de standby.

Si la aplicacion se considera apagada se restan del consumo agregado aquellas mediciones que superan
el valor de standby.

Las características consideradas son:
 -- ENCENDIDO_ANT
 -- SECONDS_PAST
 -- CONSUMO_AGREGADO
 -- DIA_MEDICION
 -- HORA_DIA

'''

def generar_corpus_3(path_data, path_aggregate, consumo_standby, interval_size, escribir_archivo):

    # Cargo los dataframes utilizando indices por defecto 0 .. CANTIDAD_ENTRADAS_ARCHIVO
    agg_file_panda = pd.read_csv(path_aggregate, sep=" ", header=None)
    agg_file_panda.columns = ["Timestamp", "Consumo"]

    app_file_panda = pd.read_csv(path_data, sep=" ", header=None)
    app_file_panda.columns = ["Timestamp", "Consumo"]

    # Vectores de entrenamiento
    vectores_entrada = []
    predicciones_entrada = []

    encendido_ant = 0              # Indica ON/OFF en intervalo anterior
    seconds_past = 0               # Cantidad de segundos que lleva apagada
    registro_horario_ant = 0       # Timestamp del ultimo instante de tiempo donde estuvo apagada
    max_time_off = 0               # Tiempo maximo que la aplicacion se encontro apagada

    fin = False

    # Estas variables determinan los limites del intervalo de tiempo
    range_start = datetime.fromtimestamp(app_file_panda.iloc[0]['Timestamp'])
    range_end = range_start + timedelta(seconds=interval_size)

    # Son el primer y ultimo timestamp de los intervalos a considerar del aparato y el consumo total de la casa
    # Inicialmente como no se conocen los limites del intervalo se inicializan con el primer y ultimo timestamp
    # del archivo. A los last_index se le suma uno para incluir la ultima medidad del archivo
    first_index = app_file_panda.first_valid_index()
    last_index = app_file_panda.last_valid_index() + 1
    first_index_agg = agg_file_panda.first_valid_index()
    last_index_agg = agg_file_panda.last_valid_index() + 1

    count_intervalos = 0

    while not fin:

        count_intervalos += 1

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
        range_end = range_start + timedelta(seconds=30)

        # Si para la aplicacion o el agregado no se tienen medidas dentro del intervalo, entonces se descartan
        if (len(registros_aplicacion) == 0) or (len(registros_agregados) == 0):
            continue

        # ********************** FEATURE HORAS_APAGADO **********************
        if registro_horario_ant > 0:
            # Segundos desde la medicion anterior
            datetime1 = datetime.fromtimestamp(app_file_panda.iloc[registros_aplicacion[0]]['Timestamp'])
            datetime2 = datetime.fromtimestamp(registro_horario_ant)
            datetime_aux = datetime1 - datetime2

            seconds_past += datetime_aux.total_seconds()

            if seconds_past > max_time_off:
                max_time_off = seconds_past

        #  **********************  FEATURE FIN_DE_SEMANA **********************
        dia_medicion = datetime.fromtimestamp(app_file_panda.iloc[registros_aplicacion[0]]['Timestamp']).strftime("%A")

        if dia_medicion == 'Saturday' or dia_medicion == 'Sunday':
            dia_medicion = 1
        else:
            dia_medicion = 0

        # **********************  FEATURE HORA_DEL_DIA **********************
        # Se utiliza el primer timestamp comprendido dentro del intervalo
        hora_dia = datetime.fromtimestamp(app_file_panda.iloc[registros_aplicacion[0]]['Timestamp']).hour

        # Cuento la cantidad de encendidos en el intervalo y guardo en consumo_intervalo el consumo total del
        # intervalo del aparato
        cont_enc = 0
        consumo_intervalo_app = 0
        for j in registros_aplicacion:
            if app_file_panda.iloc[j]['Consumo'] > consumo_standby:
                cont_enc += 1
                consumo_intervalo_app += app_file_panda.iloc[j]['Consumo']

        # ********************** FEATURE CONSUMO_AGREGADO **********************
        # Si la cantidad de encendidos es mayor o igual que la mitad del intervalo se considera al
        # aparato encendido en ese intervalo
        if cont_enc >= len(registros_aplicacion) / 2:
            consumo_agregado_aux = 0

            for i in registros_agregados:
                consumo_agregado_aux += agg_file_panda.iloc[i]['Consumo']

            # Promedio de consumo agregado en el intervalo
            consumo_agregado = round(consumo_agregado_aux / len(registros_agregados))

            # Se actualiza el encendido actual
            encendido_act = 1
        else:
            # Si se considera el aparato apagado, se le resta al numerador del promedio de valores
            # agregados el consumo del aparato en el intervalo
            consumo_agregado_aux = 0

            for i in registros_agregados:
                consumo_agregado_aux += agg_file_panda.iloc[i]['Consumo']

            # Promedio de consumo agregado en el intervalo
            consumo_agregado = round((consumo_agregado_aux - consumo_intervalo_app) / len(registros_agregados))

            # Se actualiza el encendido actual
            encendido_act = 0

        # **********************  GENERACION VECTORES **********************
        vector_entrada = [encendido_ant, seconds_past, consumo_agregado, dia_medicion, hora_dia]
        vectores_entrada.append(vector_entrada)

        # El encendido anterior del proximo paso corresponde al encendido actual
        encendido_ant = encendido_act

        # Actualiza contadores de segundos
        if encendido_act == 0:
            registro_horario_ant = app_file_panda.iloc[registros_aplicacion[0]]['Timestamp']
        else:
            seconds_past = 0
            registro_horario_ant = 0

        # Genera el vector de salida
        predicciones_entrada.append(encendido_act)

    if escribir_archivo:

        store = {
            "features": vectores_entrada,
            "activations": predicciones_entrada
        }

        directories_file = path_data.split('/')
        file_name = directories_file[-1]

        file = open(file_name + "_generar_corpus_3", "w+")
        file.write(json.dumps(store))
        file.close()

    return vectores_entrada, predicciones_entrada


if __name__ == "__main__":
    _path_data = 'datasets/ukdale/house_2/channel_14.dat_80'
    _path_aggregate = 'datasets/ukdale/house_2/channel_1.dat'
    _consumo_standby = 50
    _interval_size = 30
    _escribir_archivo = True

    generar_corpus_3(_path_data, _path_aggregate, _consumo_standby, _interval_size, _escribir_archivo)