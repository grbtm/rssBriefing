"""
Requirements:

Briefing

    reference/corpus collection

    similarity score calculation
        - score is always wrt to a given corpus, which is relevant only for a given time until the next corpus update
            -> therefore score inherent to corpus and not property of feed item to which the score is assigned to
            -> score should be saved with Briefing object -> Briefing db table, not feed items

        many to many:
            ref1               ref2
            / | \              / | \

           /  |  \           /   |  \

        A     B    C        A    B    C
        0.9   0.2  0.9      0.0  0.9  0.8

        -> briefing ranking w threshold e.g. 0.7:
            A
            C
            B
            C

        -> consider multiple posts (A, B, C) covering same topic (ref1, ref2):
            - additional criteria (e.g. highest similarity score) needed to filter:
                A for ref1
                B for ref2

    view/write to db

    assumption now: briefing calculation to be run once per day, but potentially more often

Entry

    similarity score wrt ref

    attributes as given from db


"""

from gensim.models import Word2Vec, WordEmbeddingSimilarityIndex
from nltk import word_tokenize

MODEL_PATH = ''


def load_model(path):
    model = Word2Vec.load(path)
    return model


def preprocess(doc):
    doc = doc.split(' - ', 1)[0]  # remove news source at end of each headline from NEWS API
    doc = doc.lower()
    doc = word_tokenize(doc)

    commonlist = set('for a of the and to in'.split())

    doc = [word for word in doc if word not in commonlist]  # remove common words
    doc = [word for word in doc if word.isalpha()]  # remove numbers and special characters
    return doc


def get_reference_documents():
    """ Collect the reference topics for the current Briefing.

    Documents are Strings containing a whole text and represent the gensim objects that make up a corpus.

    :return:
    """
    documents =
    return documents


class Briefing(object):

    def __init__(self):
        self.corpus_dict = self.get_reference_corpus()

    def get_reference_corpus(self):
        """ Load the current corpus as a Dictionary.

        Since the corpus is relatively small it can be loaded fully into memory.

        :return: [gensim.corpora.Dictionary]
        """

    def curate(self):
        """ Use pre-trained Word2Vec model. Calculate similarities. Select items for briefing.

        :return: Reference to the selected items from the "item" database table
        """

        model = load_model(MODEL_PATH)

        # Construct the WordEmbeddingSimilarityIndex model based on cosine similarities between word embeddings
        termsim_index = WordEmbeddingSimilarityIndex(model.wv)

        dictionary = self.get_reference_corpus()

        # TODO need the corpus once as preprossed and tokenized and once it respective mapping as a dictionary!
        bow_corpus = [dictionary.doc2bow(document) for document in preprocessed]

    def save_to_db(self):
        """ Save given corpus and respective feed item selection to db.

        :return:
        """
