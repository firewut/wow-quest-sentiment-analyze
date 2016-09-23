QUEST_COLLECTION_ID = 'quests'
QUEST_COLLECTION_NAME = 'quests'
QUEST_SCHEMA = {
    "type": "object",
    "description": "WoW Quest Schema",
    "properties": {
        "name": {
            "type": "string",
            "required": True
        },
        "description": {
            "type": ["string", "null"]
        },
        "side": {
            "type": ["string", "null"]
        },
        "zone": {
            "type": ["string", "null"]
        },
        "requires_level": {
            "type": ["number", "null"]
        },
        "added_in_patch": {
            "type": ["number"]
        }
    }
}

QuestCollection = {
    "_id": QUEST_COLLECTION_ID,
    "name": QUEST_COLLECTION_NAME,
    "schema": QUEST_SCHEMA,
    "indexes": [
        {
            "type": "text",
            "property": "name",
            "language": "english"
        }
    ]
}


Collections = [
	QuestCollection
]