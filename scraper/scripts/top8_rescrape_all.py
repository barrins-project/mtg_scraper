import math
import time
from collections import defaultdict
from queue import Queue
from threading import Lock, Thread
from typing import DefaultDict, List

from scraper.services.mtgtop8 import consumer, producer
from scraper.utils.mtgtop8 import BASE_PATH, get_id_from_filepath


def rescrape_files(
    chunk_size: int = 1000,
    num_threads: int = 4,
):
    scraped_ids: List[int] = [
        get_id_from_filepath(json_file) for json_file in BASE_PATH.rglob("*.json")
    ]

    check = input(f"Do you want to rescrape all {len(scraped_ids)} files? (y/n): ")
    if check.lower() != "y":
        print("Aborting rescrape.")
        return

    for chunk_start in range(0, len(scraped_ids), chunk_size):
        print(f"\n🔁 Processing chunk {chunk_start} to {chunk_start + 1000}")
        chunk_ids = scraped_ids[chunk_start : chunk_start + 1000]

        task_queue = Queue()
        lock = Lock()
        retries: DefaultDict[str, int] = defaultdict(int)

        for i in range(0, len(chunk_ids), 10):
            batch = chunk_ids[i : i + 10]
            threads = [
                Thread(target=producer, args=(event_id, task_queue, lock))
                for event_id in batch
            ]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

        print(f"📦 Chunk queued: {task_queue.qsize()} tournaments")

        consumer_threads = [
            Thread(target=consumer, args=(task_queue, lock, i + 1, retries))
            for i in range(num_threads)
        ]
        for t in consumer_threads:
            t.start()
        for t in consumer_threads:
            t.join()

        print("✅ Finished chunk")


if __name__ == "__main__":
    rescrape_files()
    print("🎉 All tournaments reprocessed.")
