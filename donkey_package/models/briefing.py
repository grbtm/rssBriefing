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
from gensim.corpora import Dictionary
from gensim.models import Word2Vec, WordEmbeddingSimilarityIndex
from gensim.similarities import SoftCosineSimilarity, SparseTermSimilarityMatrix
from nltk import word_tokenize
from nltk.corpus import stopwords

MODEL_PATH = ''


def load_model(path):
    model = Word2Vec.load(path)
    return model


def preprocess(doc):
    doc = doc.split(' - ', 1)[0]  # remove news source at end of each headline from NEWS API
    doc = doc.lower()
    doc = word_tokenize(doc)

    commonlist = stopwords.words('english')

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


def get_corpus_dictionary(corpus):
    """ Wrapper for gensim Dictionary function.

    From gensim docs: Dictionary encapsulates the mapping between normalized words and their integer ids.

    :return: [gensim.corpora.Dictionary]
    """

    dictionary = Dictionary(corpus)

    return dictionary


class Briefing(object):

    def __init__(self):
        self.corpus = self.get_reference_corpus()
        self.dictionary = get_corpus_dictionary(self.corpus)
        self.docsim = self.calculate_similarity_index()

    def get_reference_corpus(self):
        """ Load the current corpus.

        Since the corpus is relatively small it can be loaded fully into memory.

        :return: [Lst[Str]] List of Strings containing the preprocessed text bodies
        """

        corpus = [preprocess(doc) for doc in get_reference_documents()]
        return corpus

    def calculate_similarity_index(self):
        """ Use pre-trained Word2Vec model for word embeddings. Calculate similarities based on Soft Cosine Measure.

        References
            Grigori Sidorov et al.
            Soft Similarity and Soft Cosine Measure: Similarity of Features in Vector Space Model, 2014.

            Delphine Charlet and Geraldine Damnati, SimBow at SemEval-2017 Task 3:
            Soft-Cosine Semantic Similarity between Questions for Community Question Answering, 2017.

            Gensim notebook on: Finding similar documents with Word2Vec and Soft Cosine Measure
            https://github.com/RaRe-Technologies/gensim/blob/develop/docs/notebooks/soft_cosine_tutorial.ipynb

        :return: [numpy.ndarray] similarity index matrix, stored in memory
        """

        # Load pre-trained Word2Vec model
        model = load_model(MODEL_PATH)

        # Construct the WordEmbeddingSimilarityIndex model based on cosine similarities between word embeddings
        similarity_index = WordEmbeddingSimilarityIndex(model.wv)

        # Construct similarity matrix
        similarity_matrix = SparseTermSimilarityMatrix(similarity_index, self.dictionary)

        # Convert the corpus into the bag-of-words vector representation
        bow_corpus = [self.dictionary.doc2bow(document) for document in self.corpus]

        # Build the similarity index for corpus-based queries
        docsim_index = SoftCosineSimilarity(bow_corpus, similarity_matrix, num_best=10)

        return docsim_index

    def get_similarities(self, query):
        similarities = self.docsim[query]
        return similarities


    def save_to_db(self):
        """ Save given corpus and respective feed item selection to db.

        :return:
        """
