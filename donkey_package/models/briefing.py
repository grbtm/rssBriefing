'''
Requirements:

Briefing

    reference/corpus collection

    similarity score calculation
        - score is always wrt to a given corpus, which is relevant only for a given time until the next corpus update
            -> therefore score inherent to corpus and not property of feed item to which the score is assigned to
            -> score should be saved with Briefing object, not feed items

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


'''


class Briefing(object):

    def __init__(self):
        self.get_reference_corpus()

    def get_reference_corpus(self):
        '''

        :return: [gensim.corpora.Dictionary]
        '''

    def curate(self):
        ''' Use pre-trained Word2Vec model. Calculate similarities. Select items for briefing.

        :return: Reference to the selected items from the "item" database table
        '''

    def save_to_db(self):
        ''' Save given corpus and respective feed item selection to db.

        :return:
        '''
