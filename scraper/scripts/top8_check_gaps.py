from collections import defaultdict
from queue import Queue
from threading import Lock, Thread
from typing import DefaultDict, List

from scraper.services.mtgtop8 import Top8Queue, consumer, producer
from scraper.utils import mtgtop8_utils


def get_gaps() -> List[int]:
    scrapes = [
        int(file.stem.split("_")[0])
        for file in list(mtgtop8_utils.BASE_PATH.rglob("*.json"))
    ]

    max_id = max(scrapes)
    missings = list(set(range(1, max_id + 1)) - set(scrapes))

    return sorted(missings)


def scrape_gaps(
    chunk_size: int = 100,
    batch_size: int = 10,
    num_threads: int = 4,
) -> None:
    missing_ids = get_gaps()
    print(f"❌ Found {len(missing_ids)} missing tournaments.")
    if not missing_ids:
        print("🎉 No missing tournaments found.")
        return

    for chunk_start in range(0, len(missing_ids), chunk_size):
        print(f"\n🔁 Processing chunk {chunk_start} to {chunk_start + chunk_size}")
        chunk_ids = missing_ids[chunk_start : chunk_start + chunk_size]

        task_queue: Top8Queue = Queue()
        lock = Lock()
        retries: DefaultDict[str, int] = defaultdict(int)

        for i in range(0, len(chunk_ids), batch_size):
            batch = chunk_ids[i : i + batch_size]
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

    still_missing = get_gaps()
    print(f"❌ Still missing {len(still_missing)} tournaments.")


if __name__ == "__main__":
    scrape_gaps()
