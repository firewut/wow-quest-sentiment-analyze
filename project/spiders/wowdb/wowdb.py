import ipdb
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from items import QuestItem
from schemas import *

import re
import json
import os

quest_id_regexp = re.compile("http://www.wowdb.com/quests/(\d+)")
added_in_patch_regexp = re.compile("Added in Patch (\d+(?:\.\d+)?)")
requires_level_regexp = re.compile("Requires Level (\d+)")


# Create dirs if missing
WOW_QUEST_DIR = 'project/data/wow-quests/'
os.makedirs(WOW_QUEST_DIR)


class WowDBSpider(CrawlSpider):
    name = 'wowdb'
    allowed_domains = [
        'www.wowdb.com'
    ]
    start_urls = [
        'http://www.wowdb.com/quests'
    ]

    rules = (
        Rule(LinkExtractor(allow=('/quests\?page=\d+', ))),
        Rule(LinkExtractor(allow=('/quests/\d+', ),
                           unique=True), callback='parse_item'),
    )

    def parse_item(self, response):
        self.logger.info('Quest found: %s', response.url)

        match = quest_id_regexp.match(response.url)
        if match:
            item = QuestItem()
            try:
                item['_id'] = match.groups()[0]
                item['name'] = ''.join(response.css('h2.header').css(
                    '::text').extract()).replace('Alliance\r\n','').strip()
                item['description'] = ' '.join(response.css(
                    'p.quest-description ::text').extract())

                try:
                    infobox_ul = response.css(
                        'aside.infobox ul[class!="infobox-prevnext"]'
                    )
                    for li in infobox_ul.css('li'):
                        text = ''.join(li.css(" ::text").extract())
                        try:
                            added_in_patch = added_in_patch_regexp.match(
                                text
                            ).groups()[0]
                            item["added_in_patch"] = float(added_in_patch)
                            continue
                        except:
                            pass
                        if 'side:' in text.lower():
                            if 'horde' in text.lower():
                                item["side"] = "horde"
                            if 'alliance' in text.lower():
                                item["side"] = "alliance"
                            continue
                        try:
                            requires_level = requires_level_regexp.match(text).groups()[
                                0]
                            item["requires_level"] = int(requires_level)
                            continue
                        except:
                            pass
                except:
                    pass

                try:
                    zone = ''.join(
                        response.css(
                            'section.atf ul.b-breadcrumb-wrapper li.b-breadcrumb-item'
                        )[-2].css(
                            '::text'
                        ).extract()
                    ).strip()
                    item["zone"] = zone
                except Exception as e:
                    self.logger.error(e)

                try:
                    text_file_name = "%s/%s.txt" % (
                        WOW_QUEST_DIR,
                        item['_id']
                    )
                    with open(text_file_name, 'w') as quest_file:
                        json.dump(
                            dict(item),
                            quest_file,
                            indent=4,
                            separators=(',', ': ')
                        )
                except Exception as e:
                    self.logger.error(e)
            except Exception as e:
                self.logger.error('Failed to parse %s', e)
            return item
