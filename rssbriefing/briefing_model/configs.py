# List of reference feeds to be considered for topic model training
reference_feeds = [
    'BBC News - Home',  # 1 sentence headline, 1 sentence description
    'NYT > Top Stories',  # 1 sentence headline, 1 sentence description BUT TODO: EXCLUDE 'Live' in title
    'NYT > World News',  # 1 sentence headline, 1 sentence description BUT TODO: EXCLUDE 'Live' or 'Updates' in headline
    'NYT > Business > Economy',  # 1 sentence headline, 1 sentence description
    # 'The Guardian',
    'Reuters: Top News',  # 1 sentence headline, 1 LONG sentence description
    'Reuters: Business News',  # 1 sentence headline, 1 LONG sentence description
    'International homepage',
    # FT - PROBLEM: DUPLICATED POSTS (e.g. 'Paris, Texas offers a cautionary tale on reopening America')
    'Fortune',  # TODO EXCUDE 'Coronavirus latest:' in headline
    # 'VICE US - undefined US', # DOESNT SEEM TO BE RELEVANT GLOBAL NEWS COVERAGE, slightly off
    'Top News and Analysis (pro)',  # CNBC - 1 sentence headline, 1 sentence description
    'U.S. News'  # CNBC; 1 sentence headline, 1 LONG sentence description
    # 'Le Monde diplomatique - English edition', # not trending global news, more long term topics
    'WSJ.com: World News',  # 1 sentence headline, 1 LONG sentence description
    'Economy',  # Politico economy - 1 sentence headline, 1 sentence description
    'Al Jazeera English',  # 1 sentence headline, 1 sentence description,
    'CNN.com - RSS Channel - Politics',  # 1 sentence headline, 1 sentence description
    'International',  # The Economist: International; 1 sentence headline, 1 sentence description
    'Business',  # The Economist: (international) Business; 1 sentence headline, 1 sentence description
    'Bloomberg Politics',  # 1 sentence headline, 1 sentence description
    'Bloomberg.com',  # 1 sentence headline, 1 sentence description
    'World & Nation',  # LA TIMES World and nation, 1 sentence headline, 1 sentence description
    'World',  # Washington Post; 1 sentence headline, 1 sentence description
    'DER SPIEGEL - International',  # 1 sentence headline, 2-3 sentences description
    'CBC | World News',  # 1 sentence headline, 1 LONG sentence description
    'U.S. News',  # CNBC; 1 sentence headline, 1 LONG sentence description
    'The Independent - World',  # 1 sentence headline, 1 LONG sentence description, BUT ENCODING ISSUE
    'World News - Breaking News, Top Stories',
    # Huffington Post; 1 sentence headline, 1 sentence description TODO remove 'Coronavirus Live Updates':
    'Deutsche Welle',  # ALL TOP STORIES AND NEWS UPDATES;  1 sentence headline, 2-3 sentences description
    'The Globe and Mail - World'  # 1 sentence headline, 1 LONG sentence description
]

# Custom stop words for spaCy's English language model
stop_words = ["Mrs.", "Ms.", "Mr.", "say", "WASHINGTON", "'s", "’"]
stop_words_to_remove = ["show"]

# Common terms for gensim's Phrases
common_terms = ("bank_of_america", "new_york", "united_states", "talk_show")

# LDA model parameters
NUM_TOPICS = 18
PASSES = 30

# RSS/Atom feeds to discard for briefing generation
DISCARD_FEEDS = ["Bloomberg.com", "Bloomberg Politics"]

# Black list of keywords to filter for topic modeling
DISCARD_KEYWORDS = ["Live ", "Coronavirus latest"]

# Regexes and phrases for preprocessing before summarization
SUMM_PREPROCESSING_RAW_TEXT_REGEXES = ["Read more:.+?\n\n"]
SUMM_PREPROCESSING_REGEXES = ["FILE PHOTO:[\s\S]*\\bREUTERS\/\\b", "[\s\S]*WASHINGTON —"]
SUMM_PREPROCESSING_PHRASES = ["Read More", "(The refiled story fixes spelling error in first paragraph)",
                              "[L8N2DC056]", "<U+200B>"]

# transformers BERT summarization model parameters
SUMMARIZATION_MODEL = "bart-large-cnn"
TOKENIZER = "facebook/bart-large-cnn"
MIN_LENGTH = 190
MAX_LENGTH = 300
