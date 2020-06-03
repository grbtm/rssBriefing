import newspaper
from tqdm import tqdm
from transformers import pipeline, AutoTokenizer
from rssbriefing.briefing_model.configs import SUMMARIZATION_MODEL, TOKENIZER, MIN_LENGTH, MAX_LENGTH
from rssbriefing.briefing_model.preprocessing import preprocess_for_summarization

COOKIE_RESPONSE = 'Cookies help us deliver our Services.'
SEARCH_RESPONSE = 'What term do you want to search?'


def get_summary(app, url, nlp, tokenizer):
    article = newspaper.Article(url)

    try:

        article.download()
        article.parse()

        text = article.text
        app.logger.info(f"{'-'*40}\n Obtained original text for summarization:\n {text}\n {'-'*40}")
        text = preprocess_for_summarization(text)

        if len(tokenizer.tokenize(text)) > 1024:
            text = text[:4000]
        if len(tokenizer.tokenize(text)) < MIN_LENGTH:
            return None

        output = nlp(text, max_length=MAX_LENGTH, min_length=MIN_LENGTH)
        summary = output[0]['summary_text']

        app.logger.info(f"{'-'*40}\n Summary done. Preprocessed text:\n {text}\n {'-'*40}\n Summary: {summary}\n {'-'*40}")

    except newspaper.article.ArticleException as a_err:

        print(f"Article exception: {a_err}")
        summary = None

    except ValueError as v_err:

        print(f"Value error: {v_err}")
        summary = None

    return summary


def enrich_with_summary(app, briefing_items):

    app.logger.info(f'Loading summarization model: {SUMMARIZATION_MODEL} and tokenizer: {TOKENIZER}...')

    nlp = pipeline('summarization', model=SUMMARIZATION_MODEL)
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER)

    app.logger.info(f'Generating summarization for {len(briefing_items)} briefing items:')

    for item in tqdm(briefing_items):

        summary = get_summary(app, item.link, nlp, tokenizer)

        if not summary or summary.startswith((COOKIE_RESPONSE, SEARCH_RESPONSE)):
            item.summary = item.description
        else:
            item.summary = summary

    return briefing_items
