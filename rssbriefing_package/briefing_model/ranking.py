import collections
from datetime import datetime, timedelta

import pytz

from donkey_package.briefing_model.preparation import preprocess
from donkey_package.models import Item, Feed, User, Briefing


def get_candidates(app, user_id):

    app.logger.info('Getting briefing candidates from last 24h...')

    # Consider only feed entries from the last 24h
    datetime_24h_ago = datetime.now(pytz.utc) - timedelta(days=1)

    # Get the feed entries from the Item table
    candidates = Item.query. \
        join(Feed). \
        join(Feed.users). \
        filter(User.id == user_id). \
        filter(Item.created > datetime_24h_ago).all()

    # Instantiate new Briefing items as data structure for processing of the briefing
    # and final write back to db
    candidates = [Briefing(
        title=item.title,
        description=item.description,
        link=item.link,
        reference='None',
        score=0.0,
        created=item.created,
        guid=item.guid,
        feed_title=item.feed.title,
        user_id=user_id
    ) for item in candidates]

    app.logger.info(f'Fetched {len(candidates)} candidates.')

    return candidates


def query_most_similar_reference(briefing_item, keyed_vectors, model, corpus):
    """ Get the reference with the highest similarity score for a given candidate <briefing_item>

    Populate the reference and score attributes of the Briefing model.

    :param briefing_item: [models.Briefing] representing an rss feed entry considered a candidate for final briefing
    :param keyed_vectors: [gensim.models.keyedvectors.WordEmbeddingsKeyedVectors] representing the reference vectors
    :param model: [gensim.models.doc2vec.Doc2Vec] trained Doc2Vec model
    :param corpus: [lst[str]] of tokenized documents
    :return:
    """

    # Concatenate item title and description and preprocess it with the same function used before model training
    query = briefing_item.title + ' ' + briefing_item.description
    tokenized_query = preprocess(query)

    # Generate a vector representation of the query, based on the trained model
    inferred_vector = model.infer_vector(tokenized_query)

    # Compute cosine similarity between set of keyed vectors and inferred vector
    similarities = keyed_vectors.most_similar([inferred_vector], topn=3)
    similarities = sorted(similarities, key=lambda tupl: tupl[1], reverse=True)

    if similarities:
        top_ranked = similarities[0]

        corpus_ref_idx = top_ranked[0]
        reference_words = " ".join(corpus[corpus_ref_idx])
        briefing_item.reference = reference_words

        score = top_ranked[1]
        briefing_item.score = score


def rank_candidates(app, candidates, keyed_vectors, model, corpus):

    # Enrich candidates with most similar reference and respective similarity score
    app.logger.info('Enriching candidates w most similar reference...')

    for candidate in candidates:
        query_most_similar_reference(candidate, keyed_vectors, model, corpus)

    # Check for candidates with same reference
    references = [candidate.reference for candidate in candidates if candidate.reference is not 'None']
    multiple_assignments = [item for item, count in collections.Counter(references).items() if count > 1]

    app.logger.info(f'{len(references)} candidates were assigned a most similar reference item.')
    app.logger.info(f'{len(multiple_assignments)} reference items occurred more than once as highest sim score ref.')

    # If multiple candidates with same similarity reference exist, keep only the candidate with highest score
    if multiple_assignments:

        for reference in multiple_assignments:

            same_ref_candidates = [candidate for candidate in candidates if candidate.reference == reference]
            same_ref_candidates = sorted(same_ref_candidates, key=lambda cand: cand.score, reverse=True)

            # Reset the reference for all candidates except for the one with the highest score
            for candidate in same_ref_candidates[1:]:
                candidate.reference = 'None'

    candidates = [candidate for candidate in candidates if candidate.reference != 'None']

    app.logger.info(f'After handling of candidates with same reference: {len(candidates)} candidates point to a ref.')
    app.logger.info(f'Scores of the remaining candidates: {[candidate.score for candidate in candidates]}.')

    # Sort candidates according to their similarity score and pick only top 10 candidates
    candidates = sorted(candidates, key=lambda cand: cand.score, reverse=True)
    candidates = candidates[:10]

    return candidates