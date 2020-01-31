"""

Briefing generation module

"""
import argparse
import json
import os
import sys
from datetime import datetime

import pytz
from gensim.corpora import Dictionary
from gensim.models.doc2vec import Doc2Vec
from gensim.models.keyedvectors import WordEmbeddingsKeyedVectors

from rssbriefing_package import create_app
from rssbriefing_package import db
from rssbriefing_package.briefing_model.preparation import preprocess
from rssbriefing_package.briefing_model.ranking import get_candidates, rank_candidates
from rssbriefing_package.briefing_model.summarization import enrich_with_summary
from rssbriefing_package.db_utils import get_user_by_id, get_all_users


def get_reference_documents():
    """ Collect the reference topics for the current Briefing.

    Documents are Strings containing a whole text and represent the gensim objects that make up a corpus.

    :return:
    """

    with open('final.json') as f:
        documents = json.load(f)

    corpus_titles = [doc for doc in documents['articles']]

    return corpus_titles


def get_corpus_dictionary(app, corpus):
    """ Wrapper for gensim Dictionary function.

    From gensim docs: Dictionary encapsulates the mapping between normalized words and their integer ids.

    :return: [gensim.corpora.Dictionary]
    """
    app.logger.info('Creating gensim Dictionary for corpus...')

    dictionary = Dictionary(corpus)

    app.logger.info('Dictionary created.')

    return dictionary


def get_reference_corpus(app):
    """ Load the current corpus.

    Since the corpus is relatively small it can be loaded fully into memory.

    :return: [Lst[Str]] List of Strings containing the preprocessed text bodies
    """

    app.logger.info('Fetching reference corpus for briefing...')

    corpus = [preprocess(doc) for doc in get_reference_documents()]

    app.logger.info(f'Successfully fetched {len(corpus)} reference documents for corpus.')

    return corpus


def load_model(app):
    model_path = os.environ['MODEL_PATH']
    app.logger.info(f'Loading Doc2Vec model from {model_path}')
    model = Doc2Vec.load(model_path)

    return model


def get_ref_vectors(model, corpus):
    """ Project the reference documents into the vector space of the trained Doc2Vec model. """

    inferred_vectors = []

    for doc in corpus:
        vec = model.infer_vector(doc)
        inferred_vectors.append(vec)

    return inferred_vectors


def get_keyed_vectors(vector_size, inferred_vecs):
    """ Use the gensim.models.keyedvectors.WordEmbeddingsKeyedVectors class to store the inferred vectors. """

    vectors = WordEmbeddingsKeyedVectors(vector_size=vector_size)
    labels = list(range(len(inferred_vecs)))
    vectors.add(entities=labels, weights=inferred_vecs)

    return vectors


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

    parser.add_argument('-t', '--similarity_threshold',
                        type=float,
                        help="Supply similarity threshold as necessary condition for briefing items.")

    command_group = parser.add_mutually_exclusive_group(required=True)

    command_group.add_argument('-u', '--user_ids',
                               nargs='+',
                               action='store',  # the default value
                               help="State user_ids for whom briefing should be generated.")
    command_group.add_argument('-A', '--All',
                               action='store_true',
                               help="Generate briefing for all users. Arguments '-u' and '-A' are mutually exclusive.")

    return parser.parse_args()


def generate_briefing():
    # Set up app context to be able to access extensions such as SQLAlchemy when this module is run independently
    app = create_app()
    app.app_context().push()

    try:

        args = parse_args()

        if args.All:

            users = get_all_users()

        else:

            users = [get_user_by_id(user_id) for user_id in args.user_ids]

        # Get the current reference corpus
        corpus = get_reference_corpus(app)

        # Load trained Doc2Vec model
        model = load_model(app)

        # Use the model to infer document vectors from reference corpus
        reference_vectors = get_ref_vectors(model=model, corpus=corpus)

        # Construct Keyed Vectors set of vectors from reference vectors
        keyed_vectors = get_keyed_vectors(vector_size=model.vector_size, inferred_vecs=reference_vectors)

        app.logger.info(f'Generating briefing for users {users}...')

        for user in users:
            app.logger.info(f'Generating briefing for user {user}...')

            candidates = get_candidates(app, user.id)

            selected = rank_candidates(app, candidates, keyed_vectors, model, corpus, args.similarity_threshold)

            selected = enrich_with_summary(selected)

            app.logger.info(f'Writing {len(selected)} briefing items for user {user} to DB...')
            save_to_db(selected)
            app.logger.info('DB write done.')

    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())


if __name__ == '__main__':
    generate_briefing()
