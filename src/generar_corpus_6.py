import json

'''
Idem caso 5 considerando unicamente la caracteristica de variacion de consumo agregado.

Las características consideradas son:
 -- FRANJA

'''


def generar_corpus_6(path_corpus_5, escribir_archivo):

    file1 = open(path_corpus_5)
    dataset_json = file1.read()
    dataset_dic = json.loads(dataset_json)

    x_vector = dataset_dic["features"]
    y_vector = dataset_dic["activations"]

    reduced_vector = []
    for x in x_vector:
        reduced_vector.append([x[3]])

    if escribir_archivo:
        store = {
            "features": reduced_vector,
            "activations": y_vector
        }

        file = open("generar_corpus_6", "w+")
        file.write(json.dumps(store))
        file.close()

    return reduced_vector, y_vector


if __name__ == "__main__":

    _path_corpus_5 = ""
    _escribir_archivo = True

    generar_corpus_6(_path_corpus_5, _escribir_archivo)
