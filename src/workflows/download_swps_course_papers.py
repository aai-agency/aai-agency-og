"""
This script downloads all the papers from the SWPS short course.
"""

import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
import logging


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create papers directory if it doesn't exist
WORKSPACE_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
PAPERS_DIR = os.path.join(WORKSPACE_ROOT, "output", "papers")
os.makedirs(PAPERS_DIR, exist_ok=True)


def setup_driver():
    """Set up a Chrome webdriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


def download_paper(url, filename):
    """Download a paper given its URL and save it with the specified filename."""
    try:
        base_url = "https://www.swpshortcourse.org"
        full_url = urljoin(base_url, url)
        logger.info(f"Downloading from URL: {full_url}")

        response = requests.get(full_url, stream=True)
        response.raise_for_status()

        filepath = os.path.join(PAPERS_DIR, filename)
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.info(f"Successfully downloaded: {filename}")
        return True
    except Exception as e:
        logger.error(f"Error downloading {filename}: {str(e)}")
        return False


def main():
    base_url = "https://www.swpshortcourse.org/papers"
    page = 0
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)

    try:
        while True:
            url = f"{base_url}?page={page}"
            logger.info(f"Processing page {page}")

            driver.get(url)

            download_links = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//a[text()='Download']")
                )
            )

            if not download_links:
                logger.info("No more papers found. Ending download process.")
                break

            # Process each download link
            for link in download_links:
                try:
                    paper_url = link.get_attribute("href")
                    if not paper_url:
                        continue

                    # Extract paper ID from URL
                    paper_id = paper_url.split("/")[-1]
                    filename = f"paper_{paper_id}.pdf"
                    filepath = os.path.join(PAPERS_DIR, filename)

                    # Check if paper already exists
                    if os.path.exists(filepath):
                        logger.info(f"Paper already exists: {filename}")
                        continue

                    # Download the paper
                    download_paper(paper_url, filename)

                except Exception as e:
                    logger.error(f"Error processing paper: {str(e)}")
                    continue

            page += 1

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
