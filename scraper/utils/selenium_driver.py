import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scraper.utils.mtgo import BASE_URL, MAX_RETRIES

TOURNAMENT_LINKS_SELECTOR = "#decklists > div.site-content > div.container-page-fluid.decklists-page > ul > li > a"


def init_driver() -> webdriver.Chrome:
    # Suppression des logs TensorFlow (si présents)
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

    # Options Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")

    # Selenium Manager (intégré depuis Selenium 4.6) résout et télécharge
    # automatiquement le driver Chrome correspondant au navigateur installé,
    # directement depuis les points de distribution officiels de Google.
    service = Service(
        log_output=os.devnull
    )  # supprime l’output du service ChromeDriver

    return webdriver.Chrome(service=service, options=options)


def get_mtgo_tournaments(
    driver: WebDriver,
    year: int,
    month: int,
    timeout: int = 15,
) -> list[str]:
    tournaments: list[str] = []

    for attempt in range(MAX_RETRIES + 1):
        driver.get(BASE_URL + f"{year}/{month:02}")

        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        TOURNAMENT_LINKS_SELECTOR,
                    )
                )
            )
        except TimeoutException:
            print(
                f"⏱️ Timeout ({timeout}s) en attendant la liste des tournois "
                f"{year}-{month:02} (essai {attempt + 1}/{MAX_RETRIES + 1})"
            )
            timeout += 10
            continue

        soup = BeautifulSoup(driver.page_source, "html.parser")
        for link in soup.select(TOURNAMENT_LINKS_SELECTOR):
            href = str(link.get("href"))
            t_link = f"https://www.mtgo.com{href}" if href.startswith("/") else href
            tournaments.append(t_link)

        if tournaments:
            break

        timeout += 10

    return tournaments
