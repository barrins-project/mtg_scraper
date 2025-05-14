import time
from datetime import date
from queue import Queue
from threading import Lock, Thread
from collections import defaultdict

from selenium.webdriver.chrome.webdriver import WebDriver

from scraper.utils import driver_utils, mtgo_utils
from scraper.utils.date_parsing import get_month_range


def scrape_mtgo(
    date_from: date,
    date_to: date,
    num_threads: int = 4,
):
    task_queue = Queue()
    lock = Lock()
    drivers = [driver_utils.init_driver() for _ in range(num_threads)]
    retries = defaultdict(int)

    producer_thread = Thread(
        target=producer,
        args=(task_queue, date_from, date_to, drivers[0], lock),
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
    queue: Queue,
    date_from: date,
    date_to: date,
    driver: WebDriver,
    lock: Lock,
) -> None:
    try:
        print("⚙️ Retrieving MTGO tournament links...")
        for year, month in get_month_range(date_from, date_to):
            tournaments_links = driver_utils.get_tournaments(driver, year, month)
            to_scrape = 0
            for link in tournaments_links:
                if mtgo_utils.we_should_scrape_it(link):
                    to_scrape += 1
                    with lock:
                        queue.put(link)
            print(f"📅 {year}-{month:02}: Found {to_scrape} tournaments to scrape.")

    finally:
        print("📤 Producer closed.")


def consumer(
    driver: WebDriver,
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
            url_task = queue.get()

        try:
            print(f"🧵 Thread-{thread_id} scrapping {url_task}")
            tournament_scrape = mtgo_utils.scrape_tournament(
                driver=driver,
                url=url_task,
                sleep_time=5 * (retries[url_task] + 1),
            )
            if tournament_scrape:
                mtgo_utils.save_tournament_scrape(tournament_scrape)
                queue.task_done()
            else:
                with lock:
                    retries[url_task] += 1
                    retry = retries[url_task]
                    if retry < max_retries:
                        print(f"↩️ Retrying {url_task} ({retry}/{max_retries})")
                        queue.put(url_task)
                    else:
                        print(f"⏭️ Skipping {url_task} after {max_retries} attempts.")
                        queue.task_done()
        except Exception as e:
            print(f"❌ Error on Thread-{thread_id} handling {url_task}: {e}")
            queue.task_done()
        finally:
            time.sleep(0.5)

    driver.quit()
    print(f"✅ Thread-{thread_id} closed.")
