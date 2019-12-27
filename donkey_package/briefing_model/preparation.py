from nltk.corpus import stopwords
from gensim.utils import tokenize

def preprocess(doc, encoding='utf8'):
    #doc = doc.split(' - ', 1)[0]  # remove news source at end of each headline from NEWS API

    doc = list(tokenize(doc,
                        lowercase=True,
                        deacc=True,     # Remove accentuation
                        encoding=encoding))

    commonlist = stopwords.words('english')

    doc = [word for word in doc if word not in commonlist]  # remove common words
    doc = [word for word in doc if word.isalpha()]  # remove numbers and special characters
    return doc
