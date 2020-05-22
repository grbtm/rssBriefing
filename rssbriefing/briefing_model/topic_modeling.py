import os
import numpy as np
from datetime import datetime
from gensim.models import LdaModel

from rssbriefing import create_app
from rssbriefing.briefing_model.preprocessing import tokenize_and_lemmatize, compute_bigrams, get_dictionary
from rssbriefing.briefing_model.configs import reference_feeds, stop_words, stop_words_to_remove, common_terms, \
    NUM_TOPICS, PASSES
from rssbriefing.briefing_model.ranking import get_candidates


module_path = os.path.abspath(os.path.dirname(__file__))


def collect_posts(app):
    """ Collect RSS and Atom posts from past 24h and store them in rssbriefing.models.Briefing data structure.

    :param app:
    :return: posts: [Lst[rssbriefing.models.Briefing]]
    """
    app.logger.info('Collecting posts from past 24h for topic modeling ... ')
    posts = get_candidates(app, user_id=1)

    posts = [candidate for candidate in posts if candidate.feed_title in reference_feeds]

    # Remove posts with Live updates, since these cover multiple topics and thus deviate from the average post
    posts = [candidate for candidate in posts if 'Live ' not in candidate.title]

    # Remove advertising posts for Bloomberg products
    posts = [candidate for candidate in posts if '(Source: Bloomberg)' not in candidate.description]

    app.logger.info(f'Successfully collected {len(posts)} posts.')
    return posts


def preprocess(app, posts):
    """ Preprocess documents and thus create corpus ready for model training.

    :param posts: [Lst[rssbriefing.models.Briefing]]
    :return: corpus: [Lst[Lst[str]] corpus consisting of documents, each document represented as list of tokens
    """
    app.logger.info('Preprocessing the collected posts ....')
    corpus = tokenize_and_lemmatize(posts=posts)

    corpus = compute_bigrams(tokenized_corpus=corpus)
    app.logger.info('Finished preprocessing.')

    return corpus


def get_bow_representation(corpus, dictionary):
    bow_corpus = [dictionary.doc2bow(doc) for doc in corpus]
    return bow_corpus


def train_model(app, bow_corpus, dictionary):
    """ Initialize and train LDA model. Since no iteration param supplied, it trains until topics converge.

    :param corpus:
    :param dictionary:
    :return: model: [gensim.models.LdaModel]
    """
    app.logger.info(f'Training LDA model with {NUM_TOPICS} topics ...')
    temp = dictionary[0]  # Load dictionary into memory, necessary due to lazy evaluation

    model = LdaModel(
        corpus=bow_corpus,

        # id2word: mapping of id -> token/word
        id2word=dictionary.id2token,

        # alpha: Can be set to an 1D array of length equal to the number of expected topics
        # that expresses our a-priori belief for the each topics’ probability.
        # We initialize it with uniform distribution.
        alpha=np.full(shape=NUM_TOPICS, fill_value=(1 / NUM_TOPICS), dtype=np.float),

        # eta: a-priori belief on word probability, ‘auto’ means: to learn the asymmetric prior from the data.
        eta='auto',

        num_topics=NUM_TOPICS,
        passes=PASSES
    )

    app.logger.info('Finished training.')
    return model


def show_model_stats(app, model, bow_corpus, corpus, dictionary):
    top_topics = model.top_topics(corpus=bow_corpus, texts=corpus, dictionary=dictionary, coherence='c_v')
    avg_topic_coherence = sum([t[1] for t in top_topics]) / NUM_TOPICS

    app.logger.info(f'Topic model training finished. Average topic coherence: {avg_topic_coherence}')
    for idx, topic in enumerate(top_topics):
        app.logger.info(f"Topic {idx + 1}: 'c_v' coherence score: {topic[1]} \n {topic[0]}")


def compute_topics(app):
    """ Train a LDA topic model on posts from the past 24h.

    :param app: [flask.Flask] object which implements a WSGI application
    :return: model: [gensim.models.LdaModel] the trained topic model
    """
    posts = collect_posts(app)

    tokenized_corpus = preprocess(app, posts)

    dictionary = get_dictionary(tokenized_corpus)

    bow_corpus = get_bow_representation(tokenized_corpus, dictionary)

    model = train_model(app, bow_corpus, dictionary)

    model.save(os.path.join(module_path, "models", f"LDA_model_{datetime.now().strftime('%Y-%m-%d')}"))

    show_model_stats(app, model, bow_corpus, tokenized_corpus, dictionary)

    return model


if __name__ == '__main__':
    # Set up app context to be able to access extensions such as SQLAlchemy when this module is run independently
    app = create_app()
    app.app_context().push()

    compute_topics(app)
