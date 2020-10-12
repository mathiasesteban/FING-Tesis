import numpy as np
import os
import json
import tensorflow as tf
import sys

from tensorflow import keras
from metrics import *
from data_representation import *
from plot import *
from numpy import newaxis

def build_vectors(train_json_path,test_json_path):
	file1 = open(train_json_path)
	dataset_json = file1.read()
	dataset_dic = json.loads(dataset_json)
	x_train = np.array(dataset_dic["features"])
	y_train = np.array(dataset_dic["activations"])

	file2 = open(test_json_path)
	dataset_json2 = file2.read()
	dataset_dic2 = json.loads(dataset_json2)
	x_test_data = dataset_dic2["features"]
	y_test_data = dataset_dic2["activations"]

	# Genero conjunto de validacion
	x_val  = x_test_data[:len(x_test_data)//2]
	x_test = x_test_data[len(x_test_data)//2:]
	y_val  = np.array(y_test_data[:len(x_test_data)//2])
	y_test = np.array(y_test_data[len(x_test_data)//2:])
	
	# Formato que entiende como entrada la red para poder testear
	x_val= np.array(x_val)
	x_test = np.array(x_test)

	# Calculo relacion entre encendidos y apagados en el conjunto de entrenamiento
	encendidos = 0
	apagados = 0
	for activation in y_train:
		if activation == 1:
			encendidos = encendidos + 1
		else:
			apagados = apagados + 1

	# Se calcula la relacion entre encendidos/apagados. Se asume por la realidad del problema que siempre existen mas instancias de apagado que de prendido
	relacion = 0
	if encendidos > 0  and apagados > 0:
		relacion = round(apagados/encendidos)

	return x_train,y_train,x_val,y_val,x_test,y_test,relacion


if __name__ == '__main__':

	print("MLP START")
	
	train_json_path = "datasets/ukdale/house_1/channel_12.dat_80_generar_corpus_3_normalized"
	test_json_path = "datasets/ukdale/house_1/channel_12.dat_20_generar_corpus_3_normalized"

	x_train, y_train, x_val, y_val, x_test, y_test, relacion_enc_apg = build_vectors(train_json_path, test_json_path)

	print("Generacion de vectores... OK")

	model = keras.Sequential()
	model.add(keras.layers.Dense(64, activation=tf.nn.relu))
	model.add(keras.layers.Dropout(0.3))
	model.add(keras.layers.Dense(64, activation=tf.nn.relu))
	model.add(keras.layers.Dropout(0.3))
	model.add(keras.layers.Dense(1, activation=tf.nn.sigmoid))

	model.compile(optimizer='adam', 
              loss='binary_crossentropy',
              metrics=['accuracy'])

	model.fit(x_train, y_train, epochs=5, validation_data=(x_val,y_val))

	predictions = model.predict(x_test)

	y_pred = []
	for predict in predictions:
		if predict > 0.5:
			y_pred.append(1)
		else:
			y_pred.append(0)	

	imprimir_metricas(y_test, y_pred)
	
	print("MLP END")

