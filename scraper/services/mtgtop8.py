import time
from collections import defaultdict
from queue import Queue
from threading import Lock, Thread
from typing import DefaultDict


from scraper.utils import mtgtop8_utils


def scrape_mtgtop8(
    span: int = 1000,
    num_threads: int = 4,
):
    task_queue = Queue()
    lock = Lock()
    retries: DefaultDict[str, int] = defaultdict(int)

    first_id = mtgtop8_utils.get_id_scraped() + 1
    for i in range(span // 10):
        threads = [
            Thread(
                target=producer,
                args=(first_id + 10 * i + j + 1, task_queue, lock),
            )
            for j in range(10)
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
        for i in range(num_threads)
    ]

    for t in consumer_threads:
        t.start()
    for t in consumer_threads:
        t.join()


def producer(
    id_to_scrape: int,
    queue: Queue,
    lock: Lock,
):
    tournament_url = mtgtop8_utils.get_tournament_url(id_to_scrape)
    tournament_soup = mtgtop8_utils.get_tournament_soup(tournament_url)

    if "No event could be found." in tournament_soup.text:
        print(f"❌ Tournament {id_to_scrape} not scrapable.")
        return

    if mtgtop8_utils.we_should_scrape_it(tournament_url):
        with lock:
            queue.put((tournament_url, tournament_soup))
        print(f"✅ Tournament {id_to_scrape} queued for scraping.")
    else:
        print(f"❌ Tournament {id_to_scrape} already scraped.")


def consumer(
    queue: Queue,
    lock: Lock,
    thread_id: int,
    retries: defaultdict[str, int],
    max_retries: int = 3,
):
    while True:
        with lock:
            if queue.empty():
                break
            url_task, soup_task = queue.get()

        try:
            print(f"🧵 Thread-{thread_id} scraping {url_task}")
            tournament_scrape = mtgtop8_utils.scrape_tournament(
                url=url_task,
                soup=soup_task,
                sleep_time=5 * (retries[url_task] + 1),
            )
            if tournament_scrape:
                mtgtop8_utils.save_tournament_scrape(tournament_scrape)
                queue.task_done()
            else:
                with lock:
                    retries[url_task] += 1
                    retry = retries[url_task]
                    if retry < max_retries:
                        print(f"↩️ Retrying {url_task} ({retry}/{max_retries})")
                        queue.put((url_task, soup_task))
                    else:
                        print(f"⏭️ Skipping {url_task} after {max_retries} attempts.")
                        queue.task_done()
        except Exception as e:
            print(f"❌ Error on Thread-{thread_id} handling {url_task}: {e}")
            queue.task_done()
        finally:
            time.sleep(0.5)

    print(f"✅ Thread-{thread_id} closed.")
