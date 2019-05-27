import Preprocessor
# TODO: dynamic import of framework
import tensorflow.python.keras.models as tfmodels
import json
import tensorflow as tf
from tensorflow.python import keras


class ModelRunner:
    # TODO(qseminq@gmail.com): convenient logging system
    # TODO: send parameters as argument, not read as file
    def __init__(self, base_folder_path='./communities/default/versions/default/',
                 framework='keras', preprocessing_version='keras_v1') -> None:
        """
        This function initializes model runner which loads model from selected path and

        Args:
            base_folder_path: This is the path to model to use in classification.
            framework: This string defines which framework is used by model
            preprocessing_version: This string defines which preprocessing version is applied before running model

        Returns:
            None
        """

        self.framework = framework

        if framework == 'keras':
            self.graph = tf.Graph()
            with self.graph.as_default():
                self.session = tf.Session(graph=self.graph)
                with self.session.as_default():
                    self.model = tfmodels.load_model(base_folder_path + 'model.h5')
        else:
            raise NotImplementedError(f'Initialization for framework {self.framework} is not implemented')

        self.preprocess = Preprocessor.Preprocessor(preprocessing_version,
                                                    base_folder_path + 'preprocessing/').preprocess

        print(f'Model runner loaded from {base_folder_path} folder using {framework} ' +
              f'framework with preprocessing of version {preprocessing_version}')

    def run(self, text) -> float:
        """
        This function makes prediction of `text` toxicity using trained model.

        Args:
            text: This is the text of commentary to be classified.

        Returns:
            probability of `text` to be toxic comment.
        """
        preprocessed = self.preprocess(text)

        if self.framework == 'keras':
            keras.backend.set_session(self.session)
            with self.graph.as_default():
                probability = float(self.model.predict(x=preprocessed))
        else:
            raise NotImplementedError(f'Prediction for framework {self.framework} is not implemented')

        print(f'Comment classification run on `{text}`. Result: {probability}')
        return probability



