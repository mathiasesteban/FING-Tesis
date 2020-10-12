import matplotlib.pyplot as plt

def plot_vectors(vectors, Xlabel, Ylabel):

    plt.figure(figsize=(12, 8))

    for vector in vectors:
        label = vector[0]
        data = vector[1]
        color = vector[2]

        plt.plot(range(len(data)), data, color, label=label)

    plt.xlabel(Xlabel, fontsize=12)
    plt.ylabel(Ylabel, fontsize=12)
    plt.legend(fontsize=12)
    plt.show()