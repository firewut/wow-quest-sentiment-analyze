"""
Retrieves a list of quests from a Deform.io
"""
from textblob import TextBlob
import datetime
import glob
import ipdb
import json
import logging
import sys

# Logging
log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
log.addHandler(out_hdlr)
log.setLevel(logging.INFO)


# Deform
from pydeform import Client
client = Client(host="deform.io")
token_client = client.auth(
    'token',
    auth_key='----',
    project_id='wow-quests',
)


def dump_from_deform():
    page = 1
    pages_pending_pending = True
    while pages_pending:
        try:
            documents = token_client.documents.find(
                collection="quests",
                page=page,
                per_page=100,
            )
            if int(documents["pages"]) == page:
                pages_pending = False
            for document in documents["items"]:
                f = open("./project/data/wow-quests/%s.txt" %
                         document["_id"], 'w')

                pretty_document = json.dumps(
                    document,
                    sort_keys=True,
                    indent=4,
                )
                f.write(pretty_document)
                f.close()
            page += 1
        except Exception as e:
            print(">>>", e)
            break


def analyze_text(text, exclude_neutral):
    blob = TextBlob(text)

    noun = blob.noun_phrases
    polarities = []
    for sentence in blob.sentences:
        polarities.append(
            sentence.sentiment.polarity
        )
    if exclude_neutral:
        return noun, list(filter(lambda x: x != 0, polarities))
    return noun, polarities


# dump_from_deform()
quests = []

# Load all quests from files
log.info("Loading Quests")
for file in glob.glob('./project/data/wow-quests/*.txt'):
    f = open(file, "r")
    quests.append(
        json.load(f)
    )
    f.close()

MIN_LEVEL = 1
MAX_LEVEL = 111
LEVELS = list(range(MIN_LEVEL, MAX_LEVEL))

SIDES = ['alliance', 'horde']

log.info("... filtering Quests using level bounds")
quests_to_analyze = []
for quest in quests:
    requires_level = 1
    if 'requires_level' in quest:
        requires_level = int(quest['requires_level'])
    quest["requires_level"] = requires_level

    side = 'both'
    if 'side' in quest:
        side = quest['side']
    quest['side'] = side

    # Final check
    if requires_level in LEVELS and (side in SIDES or side == 'both'):
        quests_to_analyze.append(
            quest
        )


stat = {}
verbs = {}
stat_series = [
    {
        "name": "alliance",
        "data": [],
                "color": "blue"
    },
    {
        "name": "horde",
        "data": [],
                "color": "red"
    }
]

for side in SIDES:
    LEVEL_MAPPING = {}
    for i in LEVELS:
        for index, stat_details in enumerate(stat_series):
            if stat_details["name"].lower() == side.lower():
                stat_series[index]["data"].append(0)

        LEVEL_MAPPING[i] = {
            'AVERAGE': 0,
        }
    stat[side] = LEVEL_MAPPING


# Magic begins
log.info("Gathering stat")
log.info("... analyze each quest description")
for quest in quests_to_analyze:
    polarity = []
    if quest["description"] != None and quest["description"] != "":
        noun, polarity = analyze_text(
            quest["description"],
            True,
        )
        # Count verbs
        blob = TextBlob(quest["description"])
        for word, tag in blob.tags:
            if tag == 'VB':
                w = word.singularize().lower()
                if len(w) > 2:
                    if w in verbs:
                        verbs[w] += 1
                    else:
                        verbs[w] = 1


    QUEST_AVG_POLARITY = 0
    if len(polarity) > 0:
        QUEST_AVG_POLARITY = sum(polarity) / float(len(polarity))

    if quest['side'] == 'both':
        stat['alliance'][int(quest["requires_level"])].update({
            quest["_id"]: QUEST_AVG_POLARITY,
        })
        stat['horde'][int(quest["requires_level"])].update({
            quest["_id"]: QUEST_AVG_POLARITY,
        })
    else:
        stat[quest['side']][int(quest["requires_level"])].update({
            quest["_id"]: QUEST_AVG_POLARITY,
        })

log.info("... analyze level AVERAGE polarity")
for side, levels in stat.items():
    for level, quests in levels.items():

        LEVEL_AVG = 0
        polarities = []
        for quest_id, quest_avg in quests.items():
            if quest_id != 'AVERAGE':
                polarities.append(quest_avg)

        if len(polarities) > 0:
            polarities = list(filter(lambda x: x != 0, polarities))
            LEVEL_AVG = sum(polarities) / float(len(polarities))
        levels[level]['AVERAGE'] = LEVEL_AVG

        for index, stat_details in enumerate(stat_series):
            if stat_details["name"].lower() == side.lower():
                stat_series[index]["data"][level - 1] = LEVEL_AVG


log.info("Writing resulting file")
f = open("./project/data/wow-quest-stat.txt", 'w')
pretty_stat = json.dumps(
    stat,
    sort_keys=True,
    indent=4,
)
f.write(pretty_stat)
f.close()


f = open("./project/data/wow-quest-series.txt", 'w')
pretty_stat_series = json.dumps(
    stat_series,
    sort_keys=True,
    indent=4,
)
f.write(pretty_stat_series)
f.close()

import operator
f = open("./project/data/wow-quest-verbs.txt", 'w')
sorted_x = sorted(verbs.items(), key=operator.itemgetter(1))
pretty_verbs = json.dumps(
    sorted_x,
    sort_keys=True,
    indent=4,
)
f.write(pretty_verbs)
f.close()