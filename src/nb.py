from sklearn.naive_bayes import GaussianNB
from metrics import *
import numpy as np
import json

# Se debe agregar el path al sistema para poder importar modulos de otros niveles
import sys
sys.path.append('../')


if __name__ == '__main__':

    path_to_application_train = "datasets/ukdale/house_1/channel_12.dat_80_no_norm_generar_corpus_7"
    path_to_application_test = "datasets/ukdale/house_1/channel_12.dat_20_no_norm_generar_corpus_7"
    print("Train path: " + path_to_application_train)
    print("Test path: " + path_to_application_test)

    # Generacion de vectores de entrada
    
    file1 = open(path_to_application_train)
    dataset_json = file1.read()
    dataset_dic = json.loads(dataset_json)
    x_train = dataset_dic["features"]
    y_train = dataset_dic["activations"]

    file2 = open(path_to_application_test)
    dataset_json2 = file2.read()
    dataset_dic2 = json.loads(dataset_json2)
    x_test = dataset_dic2["features"]
    y_test = dataset_dic2["activations"]

    print("Se entrena con un conjunto de datos de tamano: " + str(len(x_train)))
    print("Se valida con un conjunto de datos de tamano: " + str(len(x_test)))

    # Inicializacion del clasificador
    gnb = GaussianNB()

    # Entrenamiento del clasificador
    gnb.fit(np.array(x_train), np.array(y_train))

    y_pred = gnb.predict(np.array(x_test))

    imprimir_metricas(y_test, y_pred)

    