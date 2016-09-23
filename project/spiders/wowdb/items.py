from scrapy.item import Item, Field


class QuestItem(Item):
    _id = Field()
    link = Field()
    name = Field()
    description = Field()
    zone = Field()
    side = Field()
    requires_level = Field()
    added_in_patch = Field()

