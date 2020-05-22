import collections
from datetime import datetime, timedelta

import pytz

from rssbriefing.briefing_model.preprocessing import preprocess, load_current_dictionary
from rssbriefing.models import Item, Feed, Users, Briefing


def get_candidates(app, user_id):
    app.logger.info('Getting briefing candidates from last 24h...')

    # Consider only feed entries from the last 24h
    datetime_24h_ago = datetime.now(pytz.utc) - timedelta(days=1)

    # Get the feed entries from the Item table
    candidates = Item.query. \
        join(Feed). \
        join(Feed.users). \
        filter(Users.id == user_id). \
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


def query_most_similar_reference(briefing_item, model):
    """ Get the topic with the highest probability score for a given briefing_item

    :param briefing_item: [rssbriefing.models.Briefing] representing an rss feed entry considered a candidate for final briefing
    :param model: [gensim.models.doc2vec.Doc2Vec] trained Doc2Vec model
    :return:
    """

    tokenized_doc = preprocess(briefing_item)
    dictionary = load_current_dictionary()
    bow_representation = dictionary.doc2bow(tokenized_doc)

    # If the bag-of-words vector is empty, it doesn't make sense to calculate a probability distribution
    if not bow_representation:
        return

    # Generate a vector representation of the query, based on the trained model
    # Inferred vector is [Lst[tuple(topic_id, probability)]] and represents the topic probability distribution
    inferred_vector = model[bow_representation]

    top_topic = sorted(inferred_vector, key=lambda x: x[1], reverse=True)[0]

    # Update the briefing_item attributes with most probable topic
    topic_id = top_topic[0]
    briefing_item.reference = topic_id

    probability = top_topic[1]
    briefing_item.score = probability


def pick_highest_scoring_candidate_of_each_reference(app, candidates):

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

    return candidates


def rank_candidates(app, candidates, model, similarity_threshold=None):
    """ Takes a list of feed items and returns the subset which is most similar to the given reference docs/vectors.

    :param app: [flask.Flask] The flask object implements a WSGI application
    :param candidates: [lst[rssbriefing.models.Item]]
    :param model: [gensim.models.LdaModel] the trained topic model
    :param corpus: [lst[str]] of tokenized documents
    :param similarity_threshold: [float] optional condition of a minimum threshold for the similarity score
    :return: [lst[rssbriefing.models.Item]]
    """
    # Enrich candidates with most similar reference and respective similarity score
    app.logger.info('Enriching candidates w most similar reference...')

    for candidate in candidates:
        query_most_similar_reference(candidate, model)

    # Check for candidates with same reference
    candidates = pick_highest_scoring_candidate_of_each_reference(app, candidates)

    # Keep only the candidates with an assigned reference document
    candidates = [candidate for candidate in candidates if candidate.reference != 'None']

    app.logger.info(f'After handling of candidates with same reference: {len(candidates)} candidates point to a ref.')
    app.logger.info(f'Scores of the remaining candidates: {[candidate.score for candidate in candidates]}.')

    # Sort candidates according to their similarity score and apply threshold if supplied
    candidates = sorted(candidates, key=lambda cand: cand.score, reverse=True)

    if similarity_threshold:
        candidates = [candidate for candidate in candidates if candidate.score >= similarity_threshold]

    return candidates
