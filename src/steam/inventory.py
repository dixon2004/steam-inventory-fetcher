from proxy.manager import ProxyManager
from utils.logger import SyncLogger
import aiohttp


class SteamAPI:

    def __init__(self) -> None:
        """
        Initialize Steam API.
        """
        self.logger = SyncLogger("SteamAPI")
        self.proxy_manager = ProxyManager()

        self.inventory_url = "http://steamcommunity.com/inventory/"
        self.max_attempts = 20

    
    async def call(self, url: str, proxy: str = None) -> dict:
        """
        Call Steam API.
        
        Args:
            url (str): URL to call.
            proxy (str, optional): Proxy to use. Defaults to None.
            
        Returns:
            dict: Response from the API.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, proxy=proxy) as response:
                    if response.status != 200:
                        return response.status
                    
                    return await response.json()
        except Exception as e:
            self.logger.write_log("error", f"Failed to call API: {e}")


    async def fetch_user_inventory(self, steamID64: str, appID: str, contextID: str, start_assetid: str = "") -> dict:
        """
        Fetch user inventory from Steam API.

        Args:
            steamID64 (str): SteamID64 of the user.
            appID (str): Application ID of the game.
            contextID (str): Context ID of the inventory.
            start_assetid (str, optional): Asset ID to start fetching from. Defaults to "".

        Returns:
            dict: User inventory.
        """
        try:
            for attempt in range(self.max_attempts):
                try:
                    if attempt > self.max_attempts / 2:
                        proxy = await self.proxy_manager.get_working_proxy()
                        self.logger.write_log("info", f"Attempt {attempt + 1} to fetch user inventory with working proxy: {proxy}")
                    elif attempt > 0:
                        proxy = await self.proxy_manager.get_random_proxy()
                        self.logger.write_log("info", f"Attempt {attempt + 1} to fetch user inventory with random proxy: {proxy}")
                    else:
                        proxy = None
                        self.logger.write_log("info", "Attempting to fetch user inventory without proxy")

                    if appID == "440":
                        count = 2500
                    else:
                        count = 5000

                    url = f"{self.inventory_url}/{steamID64}/{appID}/{contextID}?l=english&count={count}"
                    if start_assetid:
                        url += f"&start_assetid={start_assetid}"

                    response = await self.call(url, proxy)
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
                        else:
                            self.logger.write_log("error", f"Failed to fetch user inventory: Unexpected response code {response}")
                            if proxy:
                                self.proxy_manager.add_cooldown_proxy(proxy)
                            break

                    if not isinstance(response, dict):
                        self.logger.write_log("error", "Failed to fetch user inventory: Invalid response")
                        continue

                    if proxy:
                        self.proxy_manager.add_working_proxy(proxy)

                    return response
                except Exception as e:
                    self.logger.write_log("error", f"Exception during inventory fetch on attempt {attempt}: {e}")
                    continue
        except Exception as e:
            self.logger.write_log("error", f"Failed to fetch user inventory: {e}")


    async def get_user_inventory(self, steamID64: str, appID: str, contextID: str) -> dict:
        """
        Get user inventory from Steam API.

        Args:
            steamID64 (str): SteamID64 of the user.
            appID (str): Application ID of the game.
            contextID (str): Context ID of the inventory.

        Returns:
            dict: User inventory.
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
                if not assets and not descriptions:
                    break
                
                if not inventory_data:
                    inventory_data = response
                else:
                    inventory_data["assets"].extend(assets)
                    inventory_data["descriptions"].extend(descriptions)

                total_inventory_count = response.get("total_inventory_count", 0)
                if (
                    len(inventory_data.get("assets", [])) >= total_inventory_count
                    and len(inventory_data.get("descriptions", [])) >= total_inventory_count
                ):
                    break

                more_items = response.get("more_items", 0)
                last_assetid = response.get("last_assetid")
                if more_items < 1 or not last_assetid:
                    break

                start_assetid = last_assetid

            return inventory_data
        except Exception as e:
            self.logger.write_log("error", f"Failed to get user inventory: {e}")
