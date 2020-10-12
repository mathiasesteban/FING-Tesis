import numpy as np
import json
import tensorflow as tf

from tensorflow import keras
from metrics import *
from sklearn.utils import class_weight
from sklearn import preprocessing

def build_vectors_secuence(time_steps, data):
	# Elimino vectores hasta obtener un multiplo de "time_steps"
	es_multiplo = False
	while not es_multiplo:
		if len(data) % time_steps == 0:
			es_multiplo = True
		else:
			del data[0]
	
	secuence_vec = [] 
	for index, value in enumerate(data):
		aux = []
		if len(data) < time_steps + index:
			break
			
		for i in range(time_steps):
			aux.append(data[index + i])
		secuence_vec.append(aux)
	
	return np.array(secuence_vec)


def build_vectors_out_secuence(time_steps, data):
	if time_steps > 1:
		# Elimino vectores hasta obtener un multiplo de "time_steps"
		es_multiplo = False
		while not es_multiplo:
			if len(data) % time_steps == 0:
				es_multiplo = True
			else:
				del data[0]

		secuence_out_ag = data[time_steps - 1:]
		return np.array(secuence_out_ag)
	else:
		return np.array(data)


def build_vectors(train_json_path, test_json_path, time_steps):

	'''
	Esta funcion recibe el path al JSON con los datos del generador de corpus
	y agrupa los vectores en ventanas que seran pasadas a la red LSTM.
	La cantidad de vectores en una ventana esta indicada en >time_steps>
	'''

	file1 = open(train_json_path)
	dataset_json = file1.read()
	dataset_dic = json.loads(dataset_json)
	x_train = dataset_dic["features"]
	y_train = dataset_dic["activations"]

	file2 = open(test_json_path)
	dataset_json2 = file2.read()
	dataset_dic2 = json.loads(dataset_json2)
	x_test_data = dataset_dic2["features"]
	y_test_data = dataset_dic2["activations"]

	# Genero conjunto de validacion/testeo
	x_val = x_test_data[:len(x_test_data)//2]
	x_test = x_test_data[len(x_test_data)//2:]

	y_val = y_test_data[:len(x_test_data)//2]
	y_test = y_test_data[len(x_test_data)//2:]

	# Normalizacion de features

	# MinMaxSacler -> escala en el rango [0,1]
    # scaler = preprocessing.MinMaxScaler()

	# MaxAbsScaler -> escala en el rango [-1,1] y divide por el valor maximo de cada feature
	scaler = preprocessing.MaxAbsScaler()
	x_train_scaled = scaler.fit_transform(x_train)
	x_val_scaled = scaler.transform(x_val)
	x_test_scaled = scaler.transform(x_test)    
    	 
	# Formato que entiende como entrada la red
	x_train = build_vectors_secuence(time_steps, x_train_scaled.tolist())
	y_train = build_vectors_out_secuence(time_steps, y_train)	
	x_test = build_vectors_secuence(time_steps, x_test_scaled.tolist())
	y_test = build_vectors_out_secuence(time_steps, y_test)
	x_val = build_vectors_secuence(time_steps, x_val_scaled.tolist())
	y_val = build_vectors_out_secuence(time_steps, y_val)

	return x_train, y_train, x_val, y_val, x_test, y_test

if __name__ == '__main__':

	print("\n")
	print("*********************************************************************")
	print("LSTM BINARIO START")
	print("*********************************************************************\n")

	# SETEO DE PARAMETROS
	train_json_path = "datasets/ukdale/house_1/channel_12.dat_80_no_norm_generar_corpus_7"
	test_json_path = "datasets/ukdale/house_1/channel_12.dat_20_no_norm_generar_corpus_7"
	time_steps = 3
	epochs = 15
	optimizer = 'adam'
	loss = 'binary_crossentropy'
	metrics = ['accuracy']

	print("Train path: " + train_json_path)
	print("Test path: " + test_json_path)
	print("Timesteps: " + str(time_steps))
	print("Epochs: " + str(epochs))
	print("Optimizer: " + optimizer)
	print("Loss: " + loss)
	print("Metrics: " + str(metrics))

	# PREPARACION DE DATOS
	'''
	Una red LSTM en Keras espera como entrada un 3D array, con la siguiente shape: 
	
	[Samples, Timesteps, Features]
	
	Samples:Tamano de los datos, cantidad de ventanas a utilizar
	Timesteps:	Tamano de la ventana, esta asociado con la memoria de la red
	Features:	Cantidad de caracteristicas observadas en un timestep
	'''
	x_train, y_train, x_val, y_val, x_test, y_test = build_vectors(train_json_path, test_json_path, time_steps)

	print("Se entrena con un conjunto de datos de tamaño: " + str(len(x_train)))
	print("Se valida con un conjunto de datos de tamaño: " + str(len(x_val)))
    print("Se testea con un conjunto de datos de tamaño: " + str(len(x_test)))

	# ARQUITECTURA DE LA RED
	model = keras.Sequential()
	model.add(keras.layers.Bidirectional(keras.layers.CuDNNLSTM(128, input_shape=(time_steps, x_train.shape[2]), return_sequences=True)))
	model.add(keras.layers.Bidirectional(keras.layers.CuDNNLSTM(256, return_sequences=True)))
	model.add(keras.layers.CuDNNLSTM(128))
	model.add(keras.layers.Dense(1, activation=tf.nn.sigmoid))

	# COMPILACION DEL MODELO
	model.compile(optimizer=optimizer, loss=loss, metrics=metrics)

	# ENTRENAMIENTO
	class_weights = class_weight.compute_class_weight('balanced', np.unique(y_train), y_train)

	for idx, val in enumerate(class_weights):
		print("Peso clase " + str(idx) + ": " + str(val))
	print("\n")

	model.fit(x_train, y_train, epochs=epochs, validation_data=(x_val, y_val), class_weight=class_weights)

	# PREDICCIONES
	predictions = model.predict(x_test)
	y_pred = []
	for predict in predictions:
		if predict > 0.5:
			y_pred.append(1)
		else:
			y_pred.append(0)	

	imprimir_metricas(y_test, y_pred)
