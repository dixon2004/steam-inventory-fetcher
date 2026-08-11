from proxy.manager import ProxyManager
from utils.logger import SyncLogger
import aiohttp


class SteamAPI:

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """
        Initializes the SteamAPI client with an aiohttp session and sets up the ProxyManager.

        Args:
            session (aiohttp.ClientSession): An aiohttp session for making HTTP requests.
        """
        self.logger = SyncLogger("SteamAPI")
        self.session = session
        self.proxy_manager = ProxyManager(session)

        self.inventory_url = "https://steamcommunity.com/inventory"
        self.max_attempts = 20


    async def call(self, url: str, proxy: str | None = None, headers: dict | None = None) -> dict | int | None:
        """
        Makes a GET request and returns the JSON response or HTTP status code on failure.

        Args:
            url (str): The request URL.
            proxy (str | None): Optional proxy URL. Defaults to None.
            headers (dict | None): Optional request headers. Defaults to None.

        Returns:
            dict | int | None: JSON response, HTTP status code on non-200, or None on exception.
        """
        try:
            timeout = aiohttp.ClientTimeout(total=20)
            async with self.session.get(url, proxy=proxy, headers=headers, timeout=timeout) as response:
                if response.status != 200:
                    return response.status

                return await response.json()
        except Exception as e:
            self.logger.write_log("error", f"Failed to call API: {e}")


    async def fetch_user_inventory(self, steamID64: str, appID: str, contextID: str, start_assetid: str = "") -> dict | None:
        """
        Fetches a single page of a user's inventory with retry logic and proxy rotation.

        Args:
            steamID64 (str): The 64-bit Steam ID of the target user.
            appID (str): Steam application ID (e.g., "440" for TF2).
            contextID (str): Inventory context ID (e.g., "2" for TF2).
            start_assetid (str): Starting asset ID for pagination. Defaults to "".

        Returns:
            dict | None: Inventory page data, or None if all attempts fail.
        """
        for attempt in range(self.max_attempts):
            try:
                if attempt > self.max_attempts // 2:
                    proxy = await self.proxy_manager.get_working_proxy()
                    self.logger.write_log("info", f"Attempt {attempt + 1} to fetch user inventory with working proxy")
                elif attempt > 0:
                    proxy = await self.proxy_manager.get_random_proxy()
                    self.logger.write_log("info", f"Attempt {attempt + 1} to fetch user inventory with random proxy")
                else:
                    proxy = None
                    self.logger.write_log("info", "Attempting to fetch user inventory without proxy")

                count = 2500 if appID == "440" else 5000

                url = f"{self.inventory_url}/{steamID64}/{appID}/{contextID}?l=english&count={count}"
                if start_assetid:
                    url += f"&start_assetid={start_assetid}"

                headers = {
                    "Referer": f"https://steamcommunity.com/profiles/{steamID64}/inventory",
                    "User-Agent": "okhttp/4.12.0",
                }
                response = await self.call(url, proxy, headers)
                if not response:
                    self.logger.write_log("error", "Failed to fetch user inventory: No response")
                    continue

                if isinstance(response, int):
                    if response == 429:
                        self.logger.write_log("error", "Failed to fetch user inventory: Rate limit exceeded")
                        if proxy:
                            self.proxy_manager.add_cooldown_proxy(proxy)
                        continue
                    elif response == 407:
                        self.logger.write_log("error", "Failed to fetch user inventory: Proxy authentication required")
                        if proxy:
                            self.proxy_manager.remove_proxy_from_list(proxy)
                        continue
                    elif response == 400:
                        self.logger.write_log("error", "Failed to fetch user inventory: Bad request")
                        continue
                    elif response == 403:
                        self.logger.write_log("error", "Failed to fetch user inventory: Inventory is private")
                        break
                    else:
                        self.logger.write_log("error", f"Failed to fetch user inventory: Unexpected response code {response}")
                        if proxy:
                            self.proxy_manager.add_cooldown_proxy(proxy)
                        break

                if not isinstance(response, dict):
                    self.logger.write_log("error", "Failed to fetch user inventory: Invalid response")
                    continue

                if not response.get("success"):
                    self.logger.write_log("error", "Failed to fetch user inventory: Steam reported failure")
                    continue

                if proxy:
                    self.proxy_manager.add_working_proxy(proxy)

                return response
            except Exception as e:
                self.logger.write_log("error", f"Exception during inventory fetch on attempt {attempt}: {e}")
                continue


    async def get_user_inventory(self, steamID64: str, appID: str, contextID: str) -> dict | None:
        """
        Retrieves a user's full inventory, handling pagination until all items are collected.

        Args:
            steamID64 (str): The 64-bit Steam ID of the target user.
            appID (str): Steam application ID (e.g., "440" for TF2).
            contextID (str): Inventory context ID (e.g., "2" for TF2).

        Returns:
            dict | None: The complete inventory data, or None if it could not be fetched.
        """
        try:
            inventory_data = {}
            start_assetid = ""

            while True:
                response = await self.fetch_user_inventory(steamID64, appID, contextID, start_assetid)
                if not response or not isinstance(response, dict):
                    raise Exception("No valid response")

                assets = response.get("assets", [])
                descriptions = response.get("descriptions", [])

                if not inventory_data:
                    inventory_data = response
                elif assets or descriptions:
                    inventory_data["assets"].extend(assets)
                    inventory_data["descriptions"].extend(descriptions)

                if not assets and not descriptions:
                    break

                more_items = response.get("more_items", 0)
                last_assetid = response.get("last_assetid")
                if more_items < 1 or not last_assetid:
                    break

                start_assetid = last_assetid

            return inventory_data
        except Exception as e:
            self.logger.write_log("error", f"Failed to get user inventory: {e}")
