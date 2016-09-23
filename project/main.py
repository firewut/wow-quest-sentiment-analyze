from textblob import TextBlob

import numpy
import nltk
import sklearn


text = """At eight o'clock on Thursday morning. Arthur didn't feel very good."""
blob = TextBlob(text)

for sentence in blob.sentences:
    print(sentence.sentiment.polarity, sentence)
