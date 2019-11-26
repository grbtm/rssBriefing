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

        -> consider multiple posts (A, B, C) covering same topic (ref1, ref2):
            - additional criteria (e.g. highest similarity score) needed to filter:
                A for ref1
                B for ref2

    view/write to db

    assumption now: briefing calculation to be run once per day, but potentially more often

"""
import json
from threading import Semaphore

from gensim.corpora import Dictionary
from gensim.models import Word2Vec, WordEmbeddingSimilarityIndex, KeyedVectors
from gensim.similarities import SoftCosineSimilarity, SparseTermSimilarityMatrix

from donkey_package.db import get_db
from donkey_package.models.preparation import preprocess
from donkey_package.models.ranking import get_candidates, rank_candidates

MODEL_PATH = '/Users/T/Documents/Programmieren/Python/project_donkey/instance/corpus_word2vec.model'


def get_reference_documents():
    """ Collect the reference topics for the current Briefing.

    Documents are Strings containing a whole text and represent the gensim objects that make up a corpus.

    :return:
    """

    with open('/Users/T/Downloads/test.json') as f:
        news_api = json.load(f)

    corpus_titles = [dictionary['title'] for dictionary in news_api['articles']]

    return corpus_titles


def get_corpus_dictionary(corpus):
    """ Wrapper for gensim Dictionary function.

    From gensim docs: Dictionary encapsulates the mapping between normalized words and their integer ids.

    :return: [gensim.corpora.Dictionary]
    """

    dictionary = Dictionary(corpus)

    return dictionary


def get_reference_corpus():
    """ Load the current corpus.

    Since the corpus is relatively small it can be loaded fully into memory.

    :return: [Lst[Str]] List of Strings containing the preprocessed text bodies
    """

    corpus = [preprocess(doc) for doc in get_reference_documents()]
    return corpus


def load_model(path):
    model = KeyedVectors.load('/Users/T/Documents/Programmieren/Python/models/word2vec-1m-normed/GoogleNews-1mil-vectors-gensim-normed', mmap='r')

    # The vectors can also be instantiated from an existing file on disk
    # in the original Google’s word2vec C format as a KeyedVectors instance
    # model = KeyedVectors.load(
    #         '/Users/T/Documents/Programmieren/Python/models/word2vec-1m-normed/GoogleNews-1k-vectors-gensim-normed')

    #model.syn0norm = model.syn0

    #Semaphore(0).acquire()

    return model


def calculate_similarity_index(corpus, dictionary):
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
    similarity_matrix = SparseTermSimilarityMatrix(similarity_index, dictionary)

    # Convert the corpus into the bag-of-words vector representation
    bow_corpus = [dictionary.doc2bow(document) for document in corpus]

    # Build the similarity index for corpus-based queries
    docsim_index = SoftCosineSimilarity(bow_corpus, similarity_matrix, num_best=10)

    return docsim_index


def save_to_db(briefing_items, user_id):
    db = get_db()

    for item in briefing_items:
        feed_id = item.idx_id
        user_id = user_id
        feed_title = item.feed_title
        title = item.title
        description = item.description
        link = item.link
        reference = item.reference
        score = item.score
        created = item.created
        guid = item.guid

        db.execute(
            'INSERT INTO briefing (feed_id, user_id, feed_title, title, description, link, reference, score, created, guid)'
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (feed_id, user_id, feed_title, title, description, link, reference, score, created, guid)
        )

    db.commit()


def generate_briefing(user_id='public'):

    corpus = get_reference_corpus()

    dictionary = get_corpus_dictionary(corpus)

    docsim = calculate_similarity_index(corpus, dictionary)

    candidates = get_candidates()

    selected = rank_candidates(candidates, docsim, corpus, dictionary)

    save_to_db(selected, user_id)


if __name__ == '__main__':
    generate_briefing()
