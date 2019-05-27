import pickle
from tensorflow.python.keras.preprocessing import sequence


class Preprocessor:
    def __init__(self, version, base_preprocessing_path):
        if version == 'keras_v1':
            # load tokenizer
            with open(base_preprocessing_path + 'tokenizer.pickle', 'rb') as f:
                self.tokenizer = pickle.load(f)
            self.preprocess = self.keras_v1
        else:
            raise NotImplementedError(f'No such version of preprocessing is implemented: {version}')

    def keras_v1(self, text, padding_len=100):
        """

        :type padding_len: int
        :type text: str
        """
        tokenized = self.tokenizer.texts_to_sequences([text])
        padded = sequence.pad_sequences(tokenized, maxlen=padding_len)
        return padded
