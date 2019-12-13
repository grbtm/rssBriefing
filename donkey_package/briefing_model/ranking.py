import collections
from datetime import datetime, timedelta

import pytz

from donkey_package.briefing_model.preparation import preprocess
from donkey_package.models import Item, Feed, User, Briefing


def get_candidates(user_id):
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

    return candidates


def query_most_similar_reference(briefing_item, docsim, corpus, dictionary):
    """ Get the reference with the highest similarity score for a given candidate <briefing_item>

    Populate the reference and score attributes of the Briefing model.

    :param briefing_item: [models.Briefing] representing an rss feed entry considered a candidate for final briefing
    :param docsim:
    :param corpus:
    :param dictionary:
    :return:
    """
    # TODO fix description html parsing
    query = briefing_item.title  # + ' ' + feeditem.description
    query = dictionary.doc2bow(preprocess(query))

    similarities = docsim[query]
    similarities = sorted(similarities, key=lambda tupl: tupl[1], reverse=True)

    if similarities:
        top_ranked = similarities[0]

        corpus_ref_idx = top_ranked[0]
        reference_words = " ".join(corpus[corpus_ref_idx])
        briefing_item.reference = reference_words

        score = top_ranked[1]
        briefing_item.score = score


def rank_candidates(candidates, docsim, corpus, dictionary):

    # Enrich candidates with most similar reference and respective similarity score
    for candidate in candidates:
        query_most_similar_reference(candidate, docsim, corpus, dictionary)

    # Check for candidates with same reference
    references = [candidate.reference for candidate in candidates if candidate.reference is not 'None']
    multiple_assignments = [item for item, count in collections.Counter(references).items() if count > 1]

    # If multiple candidates with same similarity reference exist, keep only the candidate with highest score
    if multiple_assignments:
        for reference in multiple_assignments:

            same_ref_candidates = [candidate for candidate in candidates if candidate.reference == reference]
            same_ref_candidates = sorted(same_ref_candidates, key=lambda cand: cand.score, reverse=True)

            # Reset the reference for all candidates except for the one with the highest score
            for candidate in same_ref_candidates[1:]:
                candidate.reference = 'None'

        candidates = [candidate for candidate in candidates if candidate.reference is not 'None']

    # Remove candidates with a similarity score below the threshold
    candidates = [candidate for candidate in candidates if candidate.score > 0.9]

    return candidates
