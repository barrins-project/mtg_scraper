import json
from collections import defaultdict
from pathlib import Path
from queue import Queue
from threading import Lock, Thread
from typing import DefaultDict, List

from scraper.services.mtgo import consumer
from scraper.utils import driver_utils, mtgo_utils


def get_tournaments_without_decks(queue: Queue, lock: Lock) -> None:
    empty_files: List[Path] = []

    for path in mtgo_utils.BASE_PATH.rglob("*.json"):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                if data.get("decks") == []:
                    empty_files.append(path)
                    with lock:
                        queue.put(data.get("tournament").get("url"))
        except Exception as e:
            print(f"Erreur lors de la lecture de {path}: {e}")

    print(f"{len(empty_files)} fichier(s) trouvé(s) avec 'decks': []")

    for file in empty_files:
        file.unlink()


def scrape_tournaments_without_decks(
    num_threads: int = 4,
):
    task_queue = Queue()
    lock = Lock()
    drivers = [driver_utils.init_driver() for _ in range(num_threads)]
    retries: DefaultDict[str, int] = defaultdict(int)

    producer_thread = Thread(
        target=get_tournaments_without_decks,
        args=(task_queue, lock),
    )

    consumer_threads = [
        Thread(
            target=consumer,
            args=(drivers[i], task_queue, lock, i + 1, retries),
        )
        for i in range(num_threads)
    ]

    producer_thread.start()
    producer_thread.join()
    for t in consumer_threads:
        t.start()
    for t in consumer_threads:
        t.join()


if __name__ == "__main__":
    scrape_tournaments_without_decks()
