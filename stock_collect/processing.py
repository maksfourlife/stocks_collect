from nltk.corpus import stopwords
from nltk import wordnet, pos_tag, WordNetLemmatizer
import re


class Processer:
    _ptag_switch = {t: getattr(wordnet.wordnet, u) for t, u in
                    zip(("J", "V", "N", "R"), ("ADJ", "VERB", "NOUN", "ADV"))}

    def __init__(self):
        self.stop_words = stopwords.words("english")
        self.lem = WordNetLemmatizer()

    def _get_ptag(self, tag):
        for key, item in self._ptag_switch.items():
            if tag.startswith(key):
                return item
        return self._ptag_switch["N"]

    def _lemmatize_words(self, words):
        tagged_words = ((word, self._get_ptag(tag)) for word, (_, tag) in zip(words, pos_tag(words)))
        return [self.lem.lemmatize(word, tag) for word, tag in tagged_words]

    def process_news(self, news):
        pt = re.compile(r"\b([a-zA-Z]+[/\-&][a-zA-Z]+|[a-zA-Z]+|\d{4})\b")
        condition = lambda t: t and t not in self.stop_words and len(t) > 1
        return self._lemmatize_words([t for t in pt.findall(news.replace('\xa0', ' ').lower()) if condition(t)])
