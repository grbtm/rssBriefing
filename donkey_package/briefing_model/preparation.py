from gensim.utils import tokenize
from nltk.corpus import stopwords


def preprocess(doc, encoding='utf8'):
    """ Prepare a document for either model training or prediction by tokenizing and applying further filters. """

    doc = list(tokenize(doc,
                        lowercase=True,
                        deacc=True,  # Remove accentuation
                        encoding=encoding))

    commonlist = stopwords.words('english')

    doc = [word for word in doc if word not in commonlist]  # remove common words
    doc = [word for word in doc if word.isalpha()]  # remove numbers and special characters

    return doc
