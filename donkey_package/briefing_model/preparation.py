from nltk import word_tokenize
from nltk.corpus import stopwords


def preprocess(doc):
    doc = doc.split(' - ', 1)[0]  # remove news source at end of each headline from NEWS API
    doc = doc.lower()
    doc = word_tokenize(doc)

    commonlist = stopwords.words('english')

    doc = [word for word in doc if word not in commonlist]  # remove common words
    doc = [word for word in doc if word.isalpha()]  # remove numbers and special characters
    return doc
