from sklearn.neighbors import KNeighborsClassifier
from metrics import *
import numpy as np
import json

# Se debe agregar el path al sistema para poder importar modulos de otros niveles
import sys
sys.path.append('../')

if __name__ == '__main__':

    # Parametros
    path_to_application_train = "datasets/ukdale/house_1/channel_12.dat_80_no_norm_generar_corpus_7"
    path_to_application_validation = "datasets/ukdale/house_1/channel_12.dat_20_no_norm_generar_corpus_7"
    n_neighbors = 5
    weights = 'uniform'

    print("Train path: " + path_to_application_train)
    print("Test path: " + path_to_application_validation)
    print("Neighbors: " + str(n_neighbors))
    print("Weights: " + weights)

    # Generacion de vectores de entrada
    file1 = open(path_to_application_train)
    dataset_json = file1.read()
    dataset_dic = json.loads(dataset_json)
    x_train = dataset_dic["features"]
    y_train = dataset_dic["activations"]

    file2 = open(path_to_application_validation)
    dataset_json2 = file2.read()
    dataset_dic2 = json.loads(dataset_json2)
    x_test_data = dataset_dic2["features"]
    y_test_data = dataset_dic2["activations"]

    # Genero conjunto de validacion/testeo
    x_validation = x_test_data[:len(x_test_data)//2]
    x_test = x_test_data[len(x_test_data)//2:]

    y_validation = y_test_data[:len(x_test_data)//2]
    y_test = y_test_data[len(x_test_data)//2:]

    print("Se entrena con un conjunto de datos de tamaño: " + str(len(x_train)))
    print("Se testea con un conjunto de datos de tamaño: " + str(len(x_test)))
    print("Se valida con un conjunto de datos de tamaño: " + str(len(x_validation)))

    # Inicializacion del clasificador
    neigh = KNeighborsClassifier(n_neighbors, weights)
    # Entrneamiento del calsificador  
    neigh.fit(np.array(x_train), np.array(y_train))

    y_pred_test = neigh.predict(np.array(x_test))
    # y_pred_validation = neigh.predict(np.array(x_validation))

    imprimir_metricas(y_test, y_pred_test)
    #imprimir_metricas(y_test, y_pred_validation)