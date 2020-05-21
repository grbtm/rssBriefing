from gensim.models import LdaModel

models_dict = {'lda': LdaModel}


class TopicModel():
    def __init__(self, model_name, path):
        self.path = path

        assert model_name in models_dict, f"Model name has to be one of: {[key for key in models_dict.keys()]}"
        self.model = models_dict[model_name]

    def load(self, path=self.path):
        self.model = self.model.load(path)

    def save(self, path=self.path):
        self.model.save(path)
