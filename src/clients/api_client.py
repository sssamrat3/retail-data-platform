import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config.settings import API_BASE_URL, REQUEST_TIMEOUT
from src.common.logger import logger


class APIClient:
    """
    Reusable HTTP client for communicating with REST APIs.
    """

    def __init__(self):
        self.base_url = API_BASE_URL
        self.timeout = REQUEST_TIMEOUT
        self.session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)


    def get(self, endpoint: str, params: dict = None) -> dict:

        url = f"{self.base_url}/{endpoint}"
        logger.info(f"Calling API: {url} with params={params}")

        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info("API call successful.")
            return response.json()

        except requests.exceptions.Timeout:
            logger.error("Request timed out.")
            raise

        except requests.exceptions.ConnectionError:
            logger.error("Unable to connect to API.")
            raise

        except requests.exceptions.HTTPError as err:
            logger.error(f"HTTP Error: {err}")
            raise

        except Exception as err:
            logger.exception(f"Unexpected Error: {err}")
            raise

