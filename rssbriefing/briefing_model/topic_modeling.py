from .data_structures import TopicModel


def preprocess():
    corpus = tokenize_and_lemmatize()

    corpus = compute_bigrams()

    return  corpus


def main():

    posts = collect_posts()

    corpus = preprocess(posts)

    dictionary = get_dictionary(corpus)

    bow_corpus = get_bow_representation(corpus, dictionary)

    model = TopicModel()




if __name__ == '__main__':
    main()
