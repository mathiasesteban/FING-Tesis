import pandas as pd
import json

from datetime import datetime
from datetime import timedelta


def calcular_cambios_estado(valores):
    cambios_estado = 0
    for i in range(1,len(valores)):
        if valores[i] == 0 and valores[i-1] != 0:
            cambios_estado += 1
        if valores[i] != 0 and valores[i-1] == 0:
            cambios_estado += 1
    return cambios_estado

def dividir_entrada_tiempo(path_data, interval_size, time):

    app_file_panda = pd.read_csv(path_data, sep=" ", header=None)
    app_file_panda.columns = ["Timestamp", "Consumo"]

    app_file_reduced = []
    aux_state_change = []
    output = []
    count_change_state = 0
    count_change_state_max = 0
    fin = False
    aux = []
    
 
    #Estas variables determinan los limites del intervalo semanal en este caso
    range_start_time = datetime.fromtimestamp(app_file_panda.iloc[0]['Timestamp'])
    range_end_time = range_start_time + timedelta(seconds=time)


    # Limites de las ventanas de avance sobre los archivos
    first_index = app_file_panda.first_valid_index()
    last_index = app_file_panda.last_valid_index() + 1
    while not fin:

         # Indices dentro del intervalo
        registros_aplicacion = []

        # ********************** SE BUSCAN LAS MEDIDAS DENTRO DEL INTERVALO **********************
        actual_time = datetime.fromtimestamp(app_file_panda.iloc[first_index]['Timestamp'])
        output_aux = []
        aux = []

            # Estas variables determinan los limites del intervalo de tiempo
        range_start = datetime.fromtimestamp(app_file_panda.iloc[first_index]['Timestamp'])
        range_end = range_start + timedelta(seconds=interval_size)

        while (actual_time + timedelta(seconds=interval_size) < range_end_time) and (not fin):
                
            # Hallas  las medidas de la aplicacion dentro del intervalo
            registros_aplicacion = []
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
            # Se actualizan los limites del intervalo
            range_start = range_end
            range_end = range_start + timedelta(seconds=interval_size)

            # Si para la aplicacion o el agregado no se tienen medidas dentro del intervalo, este se descarta
            if (len(registros_aplicacion) == 0):
                continue
                 # ********************** FEATURE CONSUMO_AGREGADO **********************
            cont_enc = 0

            # Se cuenta la cantidad de medidas que superan el stanby dentro del intervalo
            
            for j in registros_aplicacion:
                if app_file_panda.iloc[j]['Consumo'] > consumo_standby:
                    cont_enc += 1
            # El aparato se considera encendido si la mitad de los valores superan el stanby
            
            
            if cont_enc >= len(registros_aplicacion) / 2:
                # Actualizacion del estado actual
                estado_act = 1
                aux.append(estado_act)

            else:
                # Se actualiza el encendido actual a OFF
                estado_act = 0
                aux.append(estado_act)
            output_aux.append(registros_aplicacion)
            actual_time = datetime.fromtimestamp(app_file_panda.iloc[first_index]['Timestamp'])
        
        
        count_change_state = calcular_cambios_estado(aux)
        
        if count_change_state > count_change_state_max:
            output = output_aux
            count_change_state_max = count_change_state
        range_end_time += timedelta(seconds=time)

    print ("output: " + str(output))
    file_aux = open(path_data + "ejemplo_dividir_entrada_tiempo",'w')
    
    cont = 1
    for line in output:
        for i in line:
            file_aux.write(str(app_file_panda.iloc[i]['Timestamp']) + ' ' + str(app_file_panda.iloc[i]['Consumo']) + '\n')
    file_aux.close()

if __name__ == '__main__':

    path_data = "/home/ignacio/Escritorio/Respaldo/tesis/src/house_1/channel_12.dat"
    interval_size = 30
    time = 604800
    consumo_standby = 50

    dividir_entrada_tiempo(path_data, interval_size, time)
