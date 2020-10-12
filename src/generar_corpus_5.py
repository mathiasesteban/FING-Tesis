import pandas as pd
import json

from datetime import datetime
from datetime import timedelta
from data_analisis import generador_estados

'''

Para evitar descartar datos, se discretiza el tiempo tomando intervalos de 30 segundos.

MODELO DE  ESTADOS, se agregan las caracteristicas de variacion de consumo (con franja) y 
cantidad de segundos encendido.

Las características consideradas son:
 -- ESTADO_ANTERIOR
 -- SECONDS_PAST
 -- SECONDS_PAST_ON
 -- FRANJA
 -- FIN_SEMANA
 -- HORA_DIA


'''

def generar_corpus_5(path_data, path_aggregate, consumo_standby, interval_size, states, escribir_archivo, normalizar):

    # Cargo los dataframes utilizando indices por defecto 0 .. CANTIDAD_ENTRADAS_ARCHIVO
    agg_file_panda = pd.read_csv(path_aggregate, sep=" ", header=None)
    agg_file_panda.columns = ["Timestamp", "Consumo"]

    app_file_panda = pd.read_csv(path_data, sep=" ", header=None)
    app_file_panda.columns = ["Timestamp", "Consumo"]

    # Vectores de entrenamiento
    vectores_entrada = []
    predicciones_entrada = []

    estado_ant = 0              # Indica ON/OFF en intervalo anterior
    seconds_past = 0               # Cantidad de segundos que lleva apagada
    seconds_past_on = 0
    registro_horario_ant = 0       # Timestamp del ultimo instante de tiempo donde estuvo apagada
    registro_horario_ant_on = 0
    max_time_off = 0               # Tiempo maximo que la aplicacion se encontro apagada
    max_time_on = 0
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

        # ********************** FEATURE HORAS_APAGADO **********************
        if registro_horario_ant > 0:
            datetime1 = datetime.fromtimestamp(app_file_panda.iloc[registros_aplicacion[0]]['Timestamp'])
            datetime2 = datetime.fromtimestamp(registro_horario_ant)
            datetime_aux = datetime1 - datetime2
            seconds_past += datetime_aux.total_seconds()

            if seconds_past > max_time_off:
                max_time_off = seconds_past

        # ********************** FEATURE HORAS_ENCEDIDO **********************
        if registro_horario_ant_on > 0:
            datetime1 = datetime.fromtimestamp(app_file_panda.iloc[registros_aplicacion[0]]['Timestamp'])
            datetime2 = datetime.fromtimestamp(registro_horario_ant_on)
            datetime_aux = datetime1 - datetime2
            seconds_past_on += datetime_aux.total_seconds()

            if seconds_past_on > max_time_on:
                max_time_on = seconds_past_on

        #  **********************  FEATURE FIN_DE_SEMANA **********************
        dia_medicion = datetime.fromtimestamp(app_file_panda.iloc[registros_aplicacion[0]]['Timestamp']).strftime("%A")

        if dia_medicion == 'Saturday' or dia_medicion == 'Sunday':
            dia_medicion = 1
        else:
            dia_medicion = 0

        # **********************  FEATURE HORA_DEL_DIA **********************
        hora_dia = datetime.fromtimestamp(app_file_panda.iloc[registros_aplicacion[0]]['Timestamp']).hour

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
            encontre = False
            for state in states:
                consumo_promedio_app = round(consumo_intervalo_app / len(registros_aplicacion))
                if state[0] <= consumo_promedio_app <= state[1]:
                    estado_act = state[2]
                    encontre = True
            if not encontre:
                raise Exception('Value out of range: ' + str(consumo_promedio_app))

        else:
            # Si el aparato se considera apagado su consumo se resta al agregado
            consumo_agregado_aux = 0

            for i in registros_agregados:
                consumo_agregado_aux += agg_file_panda.iloc[i]['Consumo']

            # Promedio de consumo agregado en el intervalo
            consumo_agregado = round((consumo_agregado_aux - consumo_intervalo_app) / len(registros_agregados))

            # Se actualiza el encendido actual (OFF)
            estado_act = states[0][2]

        # **********************  GENERACION VECTORES **********************
        franja = round((abs(consumo_agregado - consumo_anterior)) / consumo_standby)

        vector_entrada = [estado_ant, seconds_past, seconds_past_on, franja, dia_medicion, hora_dia]
        vectores_entrada.append(vector_entrada)

        # Genera el vector de salida
        predicciones_entrada.append(estado_act)

        # ********************** ACTUALIZACION DE VARIABLES **********************

        # El encendido anterior del proximo paso corresponde al encendido actual
        estado_ant = estado_act

        # Se actualiza el valor del consumo agregao anterior para el proximo paso
        consumo_anterior = consumo_agregado

        # Actualiza caracteristica de encendido y features restantes
        if estado_act == 0:
            seconds_past_on = 0
            registro_horario_ant = app_file_panda.iloc[registros_aplicacion[0]]['Timestamp']
            registro_horario_ant_on = 0
        else:
            seconds_past = 0
            registro_horario_ant = 0
            registro_horario_ant_on = app_file_panda.iloc[registros_aplicacion[0]]['Timestamp']

    # ********************** NORMALIZAR **********************
    if normalizar:
        max_estado = 1
        max_seconds = 1
        max_seconds_on = 1
        max_franja = 1
        max_finsemana = 1
        max_horas = 23

        # Hallo los maximos
        for i in vectores_entrada:
            if i[0] > max_estado:
                max_estado = i[0]

            if i[1] > max_seconds:
                max_seconds = i[1]

            if i[2] > max_seconds_on:
                max_seconds_on = i[2]

            if i[3] > max_franja:
                max_franja = i[3]

            if i[4] > max_finsemana:
                max_finsemana = i[4]

            if i[5] > max_horas:
                max_horas = i[5]

        # Normalizo
        for i in vectores_entrada:
            i[0] = i[0] / max_estado
            i[1] = i[1] / max_seconds
            i[2] = i[2] / max_seconds_on
            i[3] = i[3] / max_franja
            i[4] = i[4] / max_finsemana
            i[5] = i[5] / max_horas

    # ********************** ESCRIBIR **********************
    if escribir_archivo:
        store = {
            "features": vectores_entrada,
            "activations": predicciones_entrada
        }

        directories_file = path_data.split('/')
        file_name = directories_file[-1]

        file = open(file_name + "_no_norm_generar_corpus_5", "w+")
        file.write(json.dumps(store))
        file.close()

    return vectores_entrada, predicciones_entrada


if __name__ == "__main__":
    _path_to_generate = "datasets/ukdale/house_1/channel_12.dat_80"
    _path_aggregate = "datasets/ukdale/house_1/channel_1.dat"
    _path_to_application = "datasets/ukdale/house_1/channel_12.dat"
    _consumo_standby = 50
    _interval_size = 30
    _states = generador_estados(_path_to_application, _consumo_standby)
    _escribir_archivo = True
    _normalizar = False

    generar_corpus_5(_path_to_generate, _path_aggregate, _consumo_standby, _interval_size, _states, _escribir_archivo, _normalizar)
