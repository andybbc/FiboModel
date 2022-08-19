import sys

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder

sys.path.append("..")
import numpy as np
from model.base import Base
from deepctr.models import DeepFM, xDeepFM


class XDeepFMModel(Base):
    def __init__(self, dic_config):
        super().__init__(dic_config)
        self.dic_config = dic_config

    def train(self, train_model_input, train_label):
        self.model = xDeepFM(self.dic_config['linear_feature_columns'],
                            self.dic_config['dnn_feature_columns'],
                             dnn_hidden_units=self.dic_config['model_config']['xdeepfm']['params']['dnn_hidden_units'],
                             cin_layer_size=self.dic_config['model_config']['xdeepfm']['params']['cin_layer_size'],
                             cin_split_half=self.dic_config['model_config']['xdeepfm']['params']['cin_split_half'],
                             cin_activation=self.dic_config['model_config']['xdeepfm']['params']['cin_activation'],
                             dnn_dropout=self.dic_config['model_config']['xdeepfm']['params']['dnn_dropout']
                             )
        self.model.compile(optimizer=self.dic_config['model_config']['xdeepfm']['compile_params']['optimizer'],  # adam
                           loss=self.dic_config['model_config']['xdeepfm']['compile_params']['loss'],  # binary_crossentropy
                           metrics=self.dic_config['model_config']['xdeepfm']['compile_params']['metrics']  # ['binary_crossentropy']
                           )

        self.model.fit(train_model_input, train_label,
                       batch_size=self.dic_config['model_config']['xdeepfm']['fit_params']['batch_size'],
                       epochs=self.dic_config['model_config']['xdeepfm']['fit_params']['epochs'],
                       verbose=self.dic_config['model_config']['xdeepfm']['fit_params']['verbose'],
                       validation_split=self.dic_config['model_config']['xdeepfm']['fit_params']['validation']
                       )

        return self.model

    def predict(self, trained_model, test_model_input):
        pred_ans = trained_model.predict(test_model_input)
        return pred_ans
