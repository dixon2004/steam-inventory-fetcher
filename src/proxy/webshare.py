from utils.config import WEBSHARE_API_KEY
from utils.logger import SyncLogger
import aiohttp


class WebshareAPI:

    def __init__(self, session: aiohttp.ClientSession):
        """
        Initializes the WebshareAPI client with an aiohttp session and sets up the API token and endpoint.

        Args:
            session (aiohttp.ClientSession): An aiohttp session for making HTTP requests.
        """
        self.logger = SyncLogger("WebshareAPI")
        self.session = session

        self.token = WEBSHARE_API_KEY
        self.proxy_list_url = "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page_size=100"


    async def call(self, url: str) -> dict | None:
        """
        Makes an authenticated GET request and returns the JSON response.

        Args:
            url (str): The request URL.

        Returns:
            dict | None: The JSON response, or None if an error occurs.
        """
        try:
            async with self.session.get(url, headers={"Authorization": f"Token {self.token}"}, raise_for_status=True) as response:
                return await response.json()
        except Exception as e:
            self.logger.write_log("error", f"Failed to call API: {e}")


    async def get_proxy_list(self) -> list | None:
        """
        Fetches the list of proxies from the Webshare API, handling pagination to retrieve all available proxies.

        Returns:
            list | None: A list of proxy URLs or None if an error occurs.
        """
        try:
            proxies = set()
            page = 1

            while True:
                url = f"{self.proxy_list_url}&page={page}"
                response = await self.call(url)
                if not response:
                    raise Exception("Empty response from the API")

                data = response.get("results")
                if not data:
                    break

                for proxy in data:
                    username = proxy.get("username")
                    password = proxy.get("password")
                    address = proxy.get("proxy_address")
                    port = proxy.get("port")
                    proxy_url = f"http://{username}:{password}@{address}:{port}"
                    proxies.add(proxy_url)

                page += 1

            return list(proxies)
        except Exception as e:
            self.logger.write_log("error", f"Failed to get proxy list: {e}")
