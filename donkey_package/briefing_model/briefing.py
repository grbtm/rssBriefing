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
import argparse
import json
import os
import sys
from datetime import datetime

import pytz
from gensim.corpora import Dictionary
from gensim.models import WordEmbeddingSimilarityIndex, KeyedVectors
from gensim.similarities import SoftCosineSimilarity, SparseTermSimilarityMatrix

from donkey_package import create_app
from donkey_package import db
from donkey_package.db_utils import get_user_by_id
from donkey_package.briefing_model.preparation import preprocess
from donkey_package.briefing_model.ranking import get_candidates, rank_candidates


def get_reference_documents():
    """ Collect the reference topics for the current Briefing.

    Documents are Strings containing a whole text and represent the gensim objects that make up a corpus.

    :return:
    """

    with open('final.json') as f:
        documents = json.load(f)

    corpus_titles = [doc for doc in documents['articles']]

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
    model = KeyedVectors.load(path, mmap='r')

    # The vectors can also be instantiated from an existing file on disk
    # in the original Google’s word2vec C format as a KeyedVectors instance
    # model = KeyedVectors.load(
    #         '/Users/T/Documents/Programmieren/Python/models/word2vec-1m-normed/GoogleNews-1k-vectors-gensim-normed')

    # model.syn0norm = model.syn0

    # Semaphore(0).acquire()

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
    model = load_model(os.environ['MODEL_PATH'])

    # Construct the WordEmbeddingSimilarityIndex model based on cosine similarities between word embeddings
    similarity_index = WordEmbeddingSimilarityIndex(model.wv)

    # Construct similarity matrix
    similarity_matrix = SparseTermSimilarityMatrix(similarity_index, dictionary)

    # Convert the corpus into the bag-of-words vector representation
    bow_corpus = [dictionary.doc2bow(document) for document in corpus]

    # Build the similarity index for corpus-based queries
    docsim_index = SoftCosineSimilarity(bow_corpus, similarity_matrix, num_best=10)

    return docsim_index


def save_to_db(briefing_items):
    current_utc_datetime = datetime.now(pytz.utc)

    for item in briefing_items:
        # Enrich the selected briefing items with current datetime for the 'briefing_created' attribute
        item.briefing_created = current_utc_datetime

        db.session.add(item)

    # Commit to db only after looping over all selected Briefing items
    db.session.commit()


def parse_args():
    parser = argparse.ArgumentParser()
    command_group = parser.add_mutually_exclusive_group(required=True)
    command_group.add_argument('-u', '--user_ids',
                               nargs='+',
                               action='store',  # the default value
                               help="State user_ids for whom briefing should be generated.")
    command_group.add_argument('-A', '--All',
                               action='store_true',
                               help="Generate briefing for all users.")

    return parser.parse_args()


def generate_briefing():
    # Set up app context to be able to access extensions such as SQLAlchemy when this module is run independently
    app = create_app()
    app.app_context().push()

    try:

        args = parse_args()

        if args.All:

            users = # TODO

        else:

            users = [get_user_by_id(user_id) for user_id in args.user_ids]

        corpus = get_reference_corpus()

        dictionary = get_corpus_dictionary(corpus)

        docsim = calculate_similarity_index(corpus, dictionary)

        for user in users:

            candidates = get_candidates(user.id)

            selected = rank_candidates(candidates, docsim, corpus, dictionary)

            save_to_db(selected)

    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())


if __name__ == '__main__':
    generate_briefing()
