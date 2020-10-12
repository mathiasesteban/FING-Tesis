def binary_to_onehot(binary_vector):

	''' Transformacion de representacion binaria a onehot '''

	onehot_vector = []

	for i in binary_vector:
		if i == 1:
			onehot_vector.append([1, 0])
		else:
			onehot_vector.append([0, 1])

	return onehot_vector


def onehot_to_binary(onehot_vector):

	''' Transformacion de representacion onehot a binaria '''

	binary_vector = []

	for p in onehot_vector:
		if p[0] > p[1]:
			binary_vector.append(1)
		else:
			binary_vector.append(0)

	return binary_vector
