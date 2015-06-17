import matplotlib.pyplot as plt
import numpy as np
import random
import sys
sys.path.append("..")
from convnet import ConvolutionalNeuralNetwork


def separate_class_from_dataset(separate_class, data_set, data_labels):
	matching_indices = []
	nonmatching_indices = []
	for i in range(len(data_set)):
		if np.argmax(data_labels[i]) == separate_class:
			matching_indices.append(i)
		else:
			nonmatching_indices.append(i)
	return data_set[nonmatching_indices], data_labels[nonmatching_indices], data_set[matching_indices], data_labels[matching_indices]


def get_task_accuracy(cnn, X, Y, task = None):
	if not task:
		return np.mean(cnn.predict(X) == np.argmax(Y, axis = 1))
	else:
		classes = np.argmax(Y, axis = 1)
		task_data = []
		task_labels = []
		for i in range(len(X)):
			if classes[i] == task:
				task_data.append(X[i])
				task_labels.append(task)
		task_data = np.asarray(task_data)
		task_labels = np.asarray(task_labels)
		if task_data.any() and task_labels.any():
			return np.mean(cnn.predict(np.asarray(task_data)) == np.asarray(task_labels))
		else:
			return 0.0


def train_per_task(cnn, num_tasks, verbose, epochs, batch_size):
	accuracies = {}
	accuracies["total"] = []
	for t in range(num_tasks):
		accuracies[t] = []

	for e in range(epochs):
		for start, end in zip(range(0, len(cnn.trX), batch_size), range(batch_size, len(cnn.trX), batch_size)):
			cnn.cost = cnn.train(cnn.trX[start:end], cnn.trY[start:end])
		accuracy = get_task_accuracy(cnn, cnn.teX, cnn.teY)
		accuracies["total"].append(accuracy)
		if verbose:
			print("Accuracy at epoch {0:02d}: {1:0.04f}".format(e, accuracy))
		for t in range(num_tasks):
			accuracies[t].append(get_task_accuracy(cnn, cnn.teX, cnn.teY, t))

	accuracies["total"] = np.asarray(accuracies["total"])
	for t in range(num_tasks):
		accuracies[t] = np.asarray(accuracies[t])
	return accuracies


def train_new_task(cnn, trXT, trYT, teXT, teYT, num_tasks, verbose, epochs, batch_size):
	accuracies = {}
	accuracies["total"] = []
	for t in range(num_tasks):
		accuracies[t] = []

	for e in range(epochs):
		for start, end in zip(range(0, len(trXT), batch_size), range(batch_size, len(trXT), batch_size)):
			cnn.cost = cnn.train(trXT[start:end], trYT[start:end])
		accuracy = get_task_accuracy(cnn, teXT, teYT)
		accuracies["total"].append(accuracy)
		if verbose:
			print("Accuracy at epoch {0:02d}: {1:0.04f}".format(e, accuracy))
		for t in range(num_tasks):
			accuracies[t].append(get_task_accuracy(cnn, teXT, teYT, t))

	accuracies["total"] = np.asarray(accuracies["total"])
	for t in range(num_tasks):
		accuracies[t] = np.asarray(accuracies[t])
	return accuracies


def main(argv):
	cnn = ConvolutionalNeuralNetwork()
	cnn.initialize_mnist()

	cnn.trX = cnn.trX[:len(cnn.trX)*.1]
	cnn.trY = cnn.trY[:len(cnn.trY)*.1]
	cnn.teX = cnn.teX[:len(cnn.teX)*.1]
	cnn.teY = cnn.teY[:len(cnn.teY)*.1]

	cnn.trX, cnn.trY, trX9, trY9 = separate_class_from_dataset(9, cnn.trX, cnn.trY)
	cnn.teX, cnn.teY, teX9, teY9 = separate_class_from_dataset(9, cnn.teX, cnn.teY)

	cnn.create_model_functions()

	n_t = 9
	v = True
	e = 20
	b = 100
	colors = ["#00FF00", "#0000FF", "#00FFFF", "#FFFF00", "#FF00FF", "#000000", "#888888", "#0088FF", "#88FF00"]

	print("Training on tasks 0-8")
	accuracies = train_per_task(cnn, n_t, v, e, b)
	for t in range(n_t):
		plt.plot(np.arange(0, e), accuracies[t], color = colors[t])
	plt.plot(np.arange(0, e), accuracies["total"], color = "#FF0000", marker = "o")
	plt.axis([0, e-1, 0, 1])
	plt.xlabel("Epoch")
	plt.ylabel("Accuracy")
	plt.title("Model Accuracy (Tasks 0-8)")
	plt.legend(["Task {0}".format(t) for t in range(n_t)]+["Total"], loc = "lower right")
	plt.show()


	n_t += 1
	colors.append("#FF0088")
	total_trX = np.concatenate((cnn.trX, trX9), axis = 0)
	total_trY = np.concatenate((cnn.trY, trY9), axis = 0)
	total_teX = np.concatenate((cnn.teX, teX9), axis = 0)
	total_teY = np.concatenate((cnn.teY, teY9), axis = 0)

	print("Retraining on tasks 0-9") # try training with just new task?
	accuracies = train_new_task(cnn, total_trX, total_trY, total_teX, total_teY, n_t, v, e, b)
	for t in range(n_t):
		plt.plot(np.arange(0, e), accuracies[t], color = colors[t])
	plt.plot(np.arange(0, e), accuracies["total"], color = "#FF0000", marker = "o")
	plt.axis([0, e-1, 0, 1])
	plt.xlabel("Epoch")
	plt.ylabel("Accuracy")
	plt.title("Model Accuracy (Tasks 0-8 then 0-9)")
	plt.legend(["Task {0}".format(t) for t in range(n_t)]+["Total"], loc = "lower right")
	plt.show()


if __name__ == "__main__":
	main(sys.argv)