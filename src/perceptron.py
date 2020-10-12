import numpy as np
import os
import json
import tensorflow as tf

# Remover mensajes log de tensorflow:
# https://stackoverflow.com/questions/35911252/disable-tensorflow-debugging-information
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from sklearn import preprocessing
from metrics import *
from data_representation import *
from plot import *

def perceptron_train(x_train, y_train_onehot, hidden_neurons, num_iters, gradient_step, weigths1, weigths2):
	# Reset the graph
	tf.reset_default_graph()

	# Placeholders for input and ouput data
	X = tf.placeholder(shape=(len(x_train), len(x_train[0])), dtype=tf.float64, name='X')
	Y = tf.placeholder(shape=(len(y_train_onehot), len(y_train_onehot[0])), dtype=tf.float64, name='Y')

	# Los pesos pueden ser randomicos o pasarse como parametros
	if weigths1 is None or weigths2 is None:
		# Variables for the two group of weigths between the three layers of the network
		W1 = tf.Variable(np.random.rand(len(x_train[0]), hidden_neurons), dtype=tf.float64)
		W2 = tf.Variable(np.random.rand(hidden_neurons, len(y_train_onehot[0])), dtype=tf.float64)
	else:
		W1 = tf.Variable(weigths1)
		W2 = tf.Variable(weigths2)

	# Create the neural net graph
	A1 = tf.sigmoid(tf.matmul(X, W1))
	y_predictions = tf.sigmoid(tf.matmul(A1, W2))

	# Funcion de costo
	deltas = tf.square(y_predictions - Y)
	loss = tf.reduce_sum(deltas)

	# Define a train operation to minimize the loss
	optimizer = tf.train.GradientDescentOptimizer(gradient_step)
	train = optimizer.minimize(loss)

	# Initialize variables and run session
	init = tf.global_variables_initializer()
	sess = tf.Session()
	sess.run(init)

	# Dataset
	data_feed = {X: x_train, Y: y_train_onehot}

	# Costo over time
	loss_values = []

	# Go through num_iters iterations: ENTRENANDO LA RED

	for i in range(num_iters):
		# Train
		sess.run(train, feed_dict=data_feed)

		# Save loss value
		loss_values.append(sess.run(loss, feed_dict=data_feed))

	weights1 = sess.run(W1)
	weights2 = sess.run(W2)

	sess.close()

	res = {
		"weights1": weights1,
		"weights2": weights2,
		"loss_values": loss_values
	}

	return res


def perceptron_test(x_test, weigths1, weigths2):

	# Reset the graph
	tf.reset_default_graph()

	# Se definen los placeholder para los datos del testeo
	X = tf.placeholder(shape=(len(x_test), len(x_test[0])), dtype=tf.float64, name='X')

	# Se definen las variables para los pesos ingresados como parametros
	W1 = tf.Variable(weigths1)
	W2 = tf.Variable(weigths2)

	# Create the neural net graph
	A1 = tf.sigmoid(tf.matmul(X, W1))
	y_predictions = tf.sigmoid(tf.matmul(A1, W2))

	init = tf.global_variables_initializer()
	sess = tf.Session()
	sess.run(init)

	data_feed_test = {X: x_test}
	last_prediction_onehot = sess.run(y_predictions, feed_dict=data_feed_test)
	last_prediction = onehot_to_binary(last_prediction_onehot)

	return last_prediction


def perceptron_run(train_json_path, test_json_path, cant_neuronas, cant_iteraciones, learning_rate, lote_entrenamiento):

	print("\n FEED FORWARD NEURAL NETWORK\n")

	# Este codigo carga los vectores de caracteristicas y salidas desde el JSON obtenido por el generar corpus

	# Datos de entrenamiento
	file1 = open(train_json_path)
	dataset_json = file1.read()
	dataset_dic = json.loads(dataset_json)
	x_train = dataset_dic["features"]
	y_train = dataset_dic["activations"]
	y_train_onehot = binary_to_onehot(y_train)

	# Datos de testeo/validacion
	file2 = open(test_json_path)
	dataset_json2 = file2.read()
	dataset_dic2 = json.loads(dataset_json2)
	x_test_data = dataset_dic2["features"]
	y_test_data = dataset_dic2["activations"]

	x_val = x_test_data[:len(x_test_data)//2]
	x_test = x_test_data[len(x_test_data)//2:]

	y_val = y_test_data[:len(x_test_data)//2]
	y_test = y_test_data[len(x_test_data)//2:]

	# Normalizacion de features   
	# MaxAbsScaler -> escala en el rango [-1,1] y divide por el valor maximo de cada feature
	scaler = preprocessing.MaxAbsScaler()
	x_train = (scaler.fit_transform(x_train)).tolist()
	x_val = (scaler.transform(x_val)).tolist()
	x_test = (scaler.transform(x_test)).tolist()

	print("Carga datos ... OK")

	# El conjunto de entrenamiento es procesado en lotes
	counter = 0		# Variable de iteracion
	lote_x = []		# Lote con entradas
	lote_y = []		# Lote con salidas
	w1 = None		# Matriz de pesos uno
	w2 = None		# Matriz de pesos dos

	# Resultados del entrenamiento
	train_results = {
		"weights1": None,
		"weights2": None,
		"loss_values": []
	}

	print("Comenzando entrenamiento ... OK")

	tamano_entenamiento = len(x_train)

	# Se recorre el conjunto de entrenamiento
	while counter <= tamano_entenamiento - 1:

		# Se agregan los datos al lote
		lote_x.append(x_train[counter])
		lote_y.append(y_train_onehot[counter])

		# Nuevo lote
		if counter % lote_entrenamiento == 0:

			print("Entrenando nuevo lote ... " + str(counter) + "/" + str(tamano_entenamiento))

			# Se entrena el lote
			resultado_lote = perceptron_train(lote_x,
											  lote_y,
											  cant_neuronas,
											  cant_iteraciones,
											  learning_rate,
											  w1,
											  w2)

			# Se actualizan w1 y w2
			w1 = resultado_lote["weights1"]
			w2 = resultado_lote["weights2"]

			# Se guardan los valores de costo
			train_results["loss_values"].extend(resultado_lote["loss_values"])

			# Se reinicia el lote
			lote_x = []
			lote_y = []

		# Se avanza al siguiente vector de entrada
		counter += 1

	print ("Entrenamiento ... OK")

	# Testeo

	print("Comenzando testeo ... " + str(len(x_test)) + " entradas")

	test_predictions = perceptron_test(x_test, w1, w2)

	print ("Testeo ... OK\n")

	# Resultados
	imprimir_metricas(y_test, test_predictions)

	# Se escribe en un archivo un JSON con los resultados
	resultados_dic = {"activaciones_reales": y_test, "activaciones_predichas": test_predictions}
	file = open("resultado_perceptron", "w+")
	file.write(json.dumps(resultados_dic))
	file.close()

	# Graficas
	plot_vectors([["Costo", train_results["loss_values"], 'b-']], "Iteraciones", "Costo")
	plot_vectors([["Activaciones predichas", test_predictions, 'bo']],"Tiempo", "Activaciones")

	print("\nFin... OK\n")

if __name__ == '__main__':

	# Parametros
	train_json_path = "datasets/ukdale/house_1/channel_12_80_generar_corpus_3"	# Archivo entrenamiento
	test_json_path = "datasets/ukdale/house_1/channel_12_20_generar_corpus_3"	# Archivo testeo
	lote_entrenamiento = 2000													# Tamaño lote
	cant_neuronas = 5															# Cantidad de neuronas
	cant_iteraciones = 10														# Iteraciones entrenamiento
	learning_rate = 0.005														# Rate aprendizaje

	perceptron_run(train_json_path, test_json_path, cant_neuronas, cant_iteraciones, learning_rate, lote_entrenamiento)
