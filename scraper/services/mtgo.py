import time
from datetime import date
from queue import Queue
from threading import Lock, Thread

from selenium.webdriver.chrome.webdriver import WebDriver

from scraper.utils import driver_utils, mtgo_utils
from scraper.utils.date_parsing import get_month_range


def scrape_mtgo(date_from: date, date_to: date, num_threads: int = 4):
    task_queue = Queue()
    lock = Lock()
    drivers = [driver_utils.init_driver() for _ in range(num_threads)]

    producer_thread = Thread(
        target=producer,
        args=(task_queue, date_from, date_to, drivers[0], lock),
    )

    consumer_threads = [
        Thread(
            target=consumer,
            args=(drivers[i], task_queue, lock, i + 1),
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
    queue: Queue, date_from: date, date_to: date, driver: WebDriver, lock: Lock
) -> None:
    try:
        print("⚙️ Retrieving MTGO tournament links...")
        for year, month in get_month_range(date_from, date_to):
            tournaments_links = driver_utils.get_tournaments(driver, year, month)
            print(f"📅 {year}-{month:02}: Found {len(tournaments_links)} tournaments.")
            for link in tournaments_links:
                if mtgo_utils.we_should_scrape_it(link):
                    with lock:
                        queue.put(link)

    finally:
        print("📤 Producer closed.")


def consumer(driver: WebDriver, queue: Queue, lock: Lock, thread_id: int):
    while True:
        with lock:
            if queue.empty():
                break
            tournament_url = queue.get()

        try:
            print(f"🧵 Thread-{thread_id} scrapping {tournament_url}")
            tournament_scrape = mtgo_utils.scrape_tournament(driver, tournament_url)
            if tournament_scrape:
                mtgo_utils.save_tournament_scrape(tournament_scrape)
        except Exception as e:
            print(f"❌ Error on Thread-{thread_id} handling {tournament_url}: {e}")
        finally:
            queue.task_done()
            time.sleep(1)

    driver.quit()
    print(f"✅ Thread-{thread_id} closed.")
