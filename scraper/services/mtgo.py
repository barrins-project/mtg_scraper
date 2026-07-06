import time
from collections import defaultdict
from datetime import date
from queue import Queue
from threading import Lock, Thread
from typing import DefaultDict

from selenium.webdriver.chrome.webdriver import WebDriver

from scraper.utils import driver_utils, mtgo_utils
from scraper.utils.date_parsing import get_month_range

type MTGTOQueue = Queue[str]


def scrape_mtgo(
    date_from: date,
    date_to: date,
    force: bool = False,
    num_threads: int = 4,
) -> None:
    task_queue: MTGTOQueue = Queue()
    lock = Lock()
    drivers = [driver_utils.init_driver() for _ in range(num_threads)]
    retries: DefaultDict[str, int] = defaultdict(int)

    producer_thread = Thread(
        target=producer,
        args=(task_queue, date_from, date_to, drivers[0], lock, force),
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


def producer(
    queue: MTGTOQueue,
    date_from: date,
    date_to: date,
    driver: WebDriver,
    lock: Lock,
    force: bool = False,
) -> None:
    try:
        print("⚙️ Retrieving MTGO tournament links...")
        for year, month in get_month_range(date_from, date_to):
            tournaments_links = driver_utils.get_mtgo_tournaments(driver, year, month)
            to_scrape = 0
            for link in tournaments_links:
                if force or mtgo_utils.we_should_scrape_it(link):
                    to_scrape += 1
                    with lock:
                        queue.put(link)
            print(f"📅 {year}-{month:02}: Found {to_scrape} tournaments to scrape.")

    finally:
        print("📤 Producer closed.")


def consumer(
    driver: WebDriver,
    queue: MTGTOQueue,
    lock: Lock,
    thread_id: int,
    retries: defaultdict[str, int],
) -> None:
    while True:
        with lock:
            if queue.empty():
                break
            url_task = queue.get()

        try:
            print(f"🧵 Thread-{thread_id} scrapping {url_task}")
            tournament_scrape = mtgo_utils.scrape_tournament(
                driver=driver,
                url=url_task,
                timeout=mtgo_utils.DEFAULT_RENDER_TIMEOUT + 10 * retries[url_task],
            )
            if tournament_scrape:
                mtgo_utils.save_tournament_scrape(tournament_scrape)
                queue.task_done()
            else:
                with lock:
                    retries[url_task] += 1
                    retry = retries[url_task]
                    if retry < mtgo_utils.MAX_RETRIES:
                        print(
                            f"↩️ Retrying {url_task} ({retry}/{mtgo_utils.MAX_RETRIES})"
                        )
                        queue.put(url_task)
                    else:
                        print(
                            f"⏭️ Skipping {url_task} after {mtgo_utils.MAX_RETRIES} attempts."
                        )
                        queue.task_done()
        except Exception as e:
            print(f"❌ Error on Thread-{thread_id} handling {url_task}: {e}")
            queue.task_done()
        finally:
            time.sleep(0.5)

    driver.quit()
    print(f"✅ Thread-{thread_id} closed.")
