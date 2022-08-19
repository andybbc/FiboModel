import itertools
import numpy as np
import matplotlib.pyplot as plt

from sklearn import svm, datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix


class confusion_matrix_(object):

    def __init__(self, y_test: np.ndarray, y_pred: np.ndarray, class_names: np.ndarray):
        self.y_test = y_test
        self.y_pred = y_pred
        self.class_names = class_names

    def plot_confusion_matrix(self, cm,
                              normalize=False,
                              title='Confusion matrix',
                              cmap=plt.cm.Blues):
        """
        This function prints and plots the confusion matrix.
        Normalization can be applied by setting `normalize=True`.
        """
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            print("Normalized confusion matrix")
        else:
            print('Confusion matrix, without normalization')

        print(cm)

        plt.imshow(cm, interpolation='nearest', cmap=cmap)
        plt.title(title)
        plt.colorbar()
        tick_marks = np.arange(len(self.class_names))
        plt.xticks(tick_marks, self.class_names, rotation=45)
        plt.yticks(tick_marks, self.class_names)

        fmt = '.2f' if normalize else 'd'
        thresh = cm.max() / 2.
        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            plt.text(j, i, format(cm[i, j], fmt),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")

        plt.tight_layout()
        plt.ylabel('True label')
        plt.xlabel('Predicted label')

    def compute(self):

        # Compute confusion matrix
        cnf_matrix = confusion_matrix(self.y_test, self.y_pred)
        np.set_printoptions(precision=2)

        # Plot non-normalized confusion matrix
        plt.figure()
        self.plot_confusion_matrix(cnf_matrix,
                                   title='Confusion matrix, without normalization')

        # Plot normalized confusion matrix
        plt.figure()
        self.plot_confusion_matrix(cnf_matrix, normalize=True,
                                   title='Normalized confusion matrix')

        plt.show()
        return cnf_matrix
