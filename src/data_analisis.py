import operator

def generador_estados(path, interval_size):

    file = open(path)
    content = file.readlines()

    dic_valores = {}
    max_power = 0

    for line in content:

        # Obtengo el valor de consumo
        consumo = int(line.split()[1])

        # Lo agrego al diccionario o sumo sus repeticiones
        if dic_valores.get(consumo) is None:
            dic_valores[consumo] = 1
        else:
            dic_valores[consumo] += 1

        # Busco el maximo consumo
        if consumo > max_power:
            max_power = consumo

    # Elimino aquellos consumos registrados pocas veces
    dic_copy = dic_valores.copy()

    for key in dic_copy.keys() :
        if dic_valores[key] <= 500:
            del dic_valores[key]

    # Ordeno los valores por orden de repeticiones
    sorted_dic = sorted(dic_valores.items(), key=operator.itemgetter(1), reverse=True)

    # Lista de estados
    states = []
    # Identificador de estados
    state_id = 0
    # Agrego el estado OFF
    states.append([0,interval_size,state_id])
    state_id += 1
    # Agrego el estado MAX
    states.append([max_power - interval_size, max_power,state_id])

    consumo_procesado = False
    hubo_intercepcion = False

    # Definicion de estados
    for power in sorted_dic:

        # Verifico si el consumo ya se encuentra en algun estado
        for state in states:

            # Si el consumo se encuentra en un estado lo salteo
            if state[0] <= power[0] <= state[1]:
                consumo_procesado = True
                break

        if not consumo_procesado:

            # Defino los rangos del estado generado por el consumo actual
            min_power = int(power[0] - interval_size / 2)
            max_power = int(power[0] + interval_size / 2)

            # Busco intercepciones con otros estados

            for state in states:
                if state[0] <= min_power <= state[1]:
                    # Expando el fin del estado interceptado hasta el consumo actual
                    state[1] = power[0]
                    hubo_intercepcion = True

            if not hubo_intercepcion:
                for state in states:
                    if state[0] <= max_power <= state[1]:
                        # Expando el inicio del estado interceptado con el consumo actual
                        state[0] = power[0]
                        hubo_intercepcion = True

            if not hubo_intercepcion:
                state_id += 1
                states.append([min_power, max_power, state_id])

        consumo_procesado = False
        hubo_intercepcion= False
           
    # Ordeno los estados
    final_states = sorted(states, key=lambda x: x[1])

    # Recorro los estados buscando huecos vacios
    for i in range(0,len(final_states) - 1):

        # Si la diferencia entre el fin del estado actual con el inicio del proximo es mayor a 1 debo ajustar
        if final_states[i + 1][0] - final_states[i][1] > 1:
            final_states[i][1] = final_states[i + 1][0] - 1

    # Ordenamiento final
    final_states = sorted(final_states, key=lambda x: x[1])

    print("********* Estados definidos *********")
    for e in final_states:
        print(e)
    print("*************************************")

    return final_states

if __name__ == '__main__':
    pass
    # path = ""
    # interval_size = 30
    # generador_estados(path, interval_size)