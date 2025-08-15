import os
import time
from typing import List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

from scraper.utils.mtgo import BASE_URL, MAX_RETRIES


def init_driver() -> webdriver.Chrome:
    # Suppression des logs TensorFlow (si présents)
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

    # Options Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")

    service = Service(
        ChromeDriverManager().install(),
        log_path=os.devnull,  # supprime l’output du service ChromeDriver
    )

    return webdriver.Chrome(service=service, options=options)


def get_mtgo_tournaments(
    driver: WebDriver,
    year: int,
    month: int,
    sleep_time: int = 5,
) -> List[str]:
    tournaments: List[str] = []

    for _ in range(MAX_RETRIES + 1):
        driver.get(BASE_URL + f"{year}/{month:02}")
        time.sleep(sleep_time)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        for link in soup.select(
            "#decklists > div.site-content > div.container-page-fluid.decklists-page > ul > li > a"
        ):
            href = str(link.get("href"))
            t_link = f"https://www.mtgo.com{href}" if href.startswith("/") else href
            tournaments.append(t_link)

        sleep_time *= 2

        if tournaments:
            break

    return tournaments
