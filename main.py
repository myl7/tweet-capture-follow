import typing
import time
import os
import re
import logging
import glob
import asyncio

import feedparser
from tweetcapture import TweetCapture

FEED_URL = os.getenv('FEED_URL')
WATCH_INTERVAL = int(os.getenv('WATCH_INTERVAL', '3600'))
CAPTURE_DIR = os.getenv('CAPTURE_DIR', '.')
DEBUG = bool(os.getenv('DEBUG'))

logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)


def watch_feed(kept_ids: typing.Set[str]) -> typing.Set[str]:
    logging.debug(f'New round: kept_ids = {kept_ids}')
    feed: feedparser.FeedParserDict = feedparser.parse(FEED_URL)
    item_map: typing.Dict[str, str] = {item['guid']: item['link'] for item in feed['items']}
    new_ids = set(item_map.keys())
    to_del_ids = kept_ids.difference(new_ids)
    to_dl_ids = new_ids.difference(kept_ids)

    for id in to_del_ids:
        os.remove(os.path.join(CAPTURE_DIR, id2filename(id)))
    logging.debug(f'Deleted: {to_del_ids}')
    logging.info(f'Deleted: {len(to_del_ids)} items')

    tweet = TweetCapture(mode=2, night_mode=0)

    async def task():
        # Can only run one by one otherwise the driver disconnects
        for id in to_dl_ids:
            await tweet.screenshot(id, os.path.join(CAPTURE_DIR, id2filename(id)))

    asyncio.run(task())
    logging.debug(f'Downloaded: {to_dl_ids}')
    logging.info(f'Downloaded: {len(to_dl_ids)} items')

    kept_ids = new_ids


def id2filename(id: str) -> str:
    m = re.match(r'^https://twitter.com/([^/]+)/status/(\d+)$', id)
    if not m:
        raise ValueError(f'Invalid id: {id}')
    return f'{m.group(1)}-{m.group(2)}.png'


def main():
    kept_fnames = glob.glob('*.png', root_dir=CAPTURE_DIR)
    kept_ids = []
    for fname in kept_fnames:
        m = re.match(r'^(.+)-(\d+)\.png$', fname)
        if not m:
            continue
        kept_ids.append(f'https://twitter.com/{m.group(1)}/status/{m.group(2)}')
    kept_ids = set(kept_ids)
    while True:
        kept_ids = watch_feed(kept_ids)
        time.sleep(WATCH_INTERVAL)


if __name__ == '__main__':
    main()
