from collections import defaultdict
from queue import Queue
from threading import Lock, Thread
from typing import DefaultDict, List

from scraper.services.mtgtop8 import consumer, producer
from scraper.utils import mtgtop8_utils


def get_gaps() -> List[int]:
    scrapes = [
        int(file.stem.split("_")[0])
        for file in list(mtgtop8_utils.BASE_PATH.rglob("*.json"))
    ]

    max_id = max(scrapes)
    missings = list(set(range(1, max_id + 1)) - set(scrapes))

    return list(missings)


def scrape_gaps(num_threads: int = 4):
    task_queue = Queue()
    lock = Lock()
    retries: DefaultDict[str, int] = defaultdict(int)

    missing_ids = get_gaps()

    producer_threads = [
        Thread(
            target=producer,
            args=(id, task_queue, lock),
        )
        for id in missing_ids
    ]
    for thread in producer_threads:
        thread.start()
    for thread in producer_threads:
        thread.join()

    print(f"📦 Total tournaments queued: {task_queue.qsize()}")

    consumer_threads = [
        Thread(
            target=consumer,
            args=(task_queue, lock, i + 1, retries),
        )
        for i in range(num_threads)
    ]
    for t in consumer_threads:
        t.start()
    for t in consumer_threads:
        t.join()

    still_missing = get_gaps()
    print(f"❌ Still missing {len(still_missing)} tournaments.")


if __name__ == "__main__":
    scrape_gaps()
