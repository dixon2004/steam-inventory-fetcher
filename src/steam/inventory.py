from proxy.manager import ProxyManager
from utils.log import write_log
import aiohttp


class SteamAPI:

    def __init__(self) -> None:
        """
        Initialize Steam API.
        """
        self.proxy_manager = ProxyManager()

        self.inventory_url = "http://steamcommunity.com/inventory/"
        self.max_attempts = 20

    
    async def call(self, url: str, proxy: str = None) -> dict:
        """
        Call Steam API.
        
        Args:
            url (str): URL to call.
            
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
            write_log("error", f"[SteamAPI] Failed to call API: {e}")


    async def get_user_inventory(self, steamID64: str, appID: str, contextID: str) -> dict:
        """
        Get user inventory from Steam API.

        Args:
            steamID64 (str): SteamID64 of the user.

        Returns:
            dict: User inventory.
        """
        try:
            for attempt in range(self.max_attempts):
                try:
                    if attempt > 0:
                        proxy = await self.proxy_manager.get_random_proxy()
                        write_log("info", f"[SteamAPI] Attempting to get user inventory with proxy: {proxy}")
                    elif attempt > self.max_attempts / 2:
                        proxy = await self.proxy_manager.get_working_proxy()
                        write_log("info", f"[SteamAPI] Attempting to get user inventory with working proxy: {proxy}")
                    else:
                        proxy = None
                        write_log("info", "[SteamAPI] Attempting to get user inventory without proxy")

                    if appID == 440:
                        count = 3000
                    else:
                        count = 5000

                    url = f"{self.inventory_url}/{steamID64}/{appID}/{contextID}?l=english&count={count}"
                    response = await self.call(url, proxy)
                    if not response:
                        continue

                    if isinstance(response, int):
                        if response == 429:
                            write_log("error", "[SteamAPI] Failed to get user inventory: Rate limit exceeded")
                            if proxy:
                                self.proxy_manager.add_cooldown_proxy(proxy)
                            continue
                        elif response == 407:
                            write_log("error", "[SteamAPI] Failed to get user inventory: Proxy authentication required")
                            if proxy:
                                self.proxy_manager.remove_proxy_from_list(proxy)
                            continue
                        else:
                            if proxy:
                                self.proxy_manager.add_cooldown_proxy(proxy)
                            break

                    self.proxy_manager.add_working_proxy(proxy)
                    return response
                except Exception as e:
                    continue
        except Exception as e:
            write_log("error", f"[SteamAPI] Failed to get user inventory: {e}")
