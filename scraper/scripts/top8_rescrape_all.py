import math
import time
from collections import defaultdict
from queue import Queue
from threading import Lock, Thread
from typing import DefaultDict, List

from scraper.services.mtgtop8 import consumer, producer
from scraper.utils.mtgtop8 import BASE_PATH, get_id_from_filepath


def rescrape_files():
    scraped_ids: List[int] = list()
    for json_file in BASE_PATH.rglob("*.json"):
        scraped_ids.append(get_id_from_filepath(json_file))

    check = input(f"Do you want to rescrape all {len(scraped_ids)} files? (y/n): ")
    if check.lower() != "y":
        print("Aborting rescrape.")
        return

    task_queue = Queue()
    lock = Lock()
    retries: DefaultDict[str, int] = defaultdict(int)
    for i in range(int(math.ceil(len(scraped_ids) / 10))):
        threads = [
            Thread(
                target=producer,
                args=(scraped_ids[10 * i + j], task_queue, lock),
            )
            for j in range(10)
            if 10 * i + j < len(scraped_ids)
        ]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    print(f"📦 Total tournaments queued: {task_queue.qsize()}")

    consumer_threads = [
        Thread(
            target=consumer,
            args=(task_queue, lock, i + 1, retries),
        )
        for i in range(4)
    ]

    for t in consumer_threads:
        t.start()
    for t in consumer_threads:
        t.join()


if __name__ == "__main__":
    rescrape_files()
