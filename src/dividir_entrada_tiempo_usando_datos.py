import json

def calcular_cambios_estado(valores):
    cambios_estado = 0
    for i in range(1,len(valores)):
        if valores[i] == 0 and valores[i-1] != 0:
            cambios_estado += 1
        if valores[i] != 0 and valores[i-1] == 0:
            cambios_estado += 1
    return cambios_estado


def dividir_entrada_short(path_corpus_7, escribir_archivo, time):
    file1 = open(path_corpus_7)
    dataset_json = file1.read()
    dataset_dic = json.loads(dataset_json)
    x_vector = dataset_dic["features"]
    y_vector = dataset_dic["activations"]

    reduced_vector = []
    cant_vect = time / 5
    size_aux = cant_vect
    size_vector = len(x_vector)
    i = 0
    best_i = 0
    fin = False
    aux = []
    count_change_state = 0
    count_change_state_max = 0
    output = []

    while (i < size_vector) and (not fin):
        if (i + size_aux < size_vector):
            aux = x_vector[i:cant_vect - 1]

            reduced_vector = []
            for x in aux:
                reduced_vector.append(x[0])
            count_change_state = calcular_cambios_estado(reduced_vector)
            if count_change_state > count_change_state_max:
                output = aux
                count_change_state_max = count_change_state
                best_i = i

            i += size_aux
            cant_vect += size_aux
        else:
            fin = True
    print("best i:" + str(best_i))
    if escribir_archivo:
        store = {
            "features": output,
            "activations": y_vector[best_i:best_i + size_aux - 1]
        }

        directories_file = path_corpus_7.split('/')
        file_name = directories_file[-1]
        file = open(file_name + "_dividir_entrada_short_mes", "w+")
        file.write(json.dumps(store))
        file.close()

if __name__ == "__main__":
    _path_corpus_7 = "/home/ignacio/Descargas/channel_12.dat_80_generar_corpus_7.dat_80_generar_corpus_7_normalized"
    _escribir_archivo = True
    _time = 2592000

    dividir_entrada_short(_path_corpus_7, _escribir_archivo, _time)
