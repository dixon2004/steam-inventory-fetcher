from proxy.webshare import WebshareAPI
from utils.logger import SyncLogger
import aiohttp
import random
import time


class ProxyManager:

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """
        Initializes the ProxyManager with an aiohttp session and sets up the WebshareAPI client.

        Args:
            session (aiohttp.ClientSession): An aiohttp session for making HTTP requests.
        """
        self.logger = SyncLogger("ProxyManager")
        self.webshare = WebshareAPI(session)

        self.proxies = None
        self.working_proxies = []
        self.cooldown_proxies = []

        self.cooldown_period = 60 * 30
        self.refresh_interval = 60 * 60 * 12


    async def get_proxy_list(self) -> list | None:
        """
        Fetches and caches the proxy list from Webshare, refreshing only when empty or stale.

        Returns:
            list | None: A list of proxy URLs, or None if an error occurs.
        """
        try:
            if not self.proxies or (time.time() - self.proxies["timestamp"]) > self.refresh_interval:
                proxies = await self.webshare.get_proxy_list()
                if not proxies:
                    raise Exception("Empty proxy list from the API")
                self.proxies = {"timestamp": time.time(), "proxies": proxies}

            return self.proxies["proxies"]
        except Exception as e:
            self.logger.write_log("error", f"Failed to get proxy list: {e}")


    async def get_random_proxy(self) -> str | None:
        """
        Retrieves a random proxy, skipping any on cooldown. Falls back to the full list if all are cooling down.

        Returns:
            str | None: A random proxy URL, or None if an error occurs.
        """
        try:
            if not self.proxies or (time.time() - self.proxies["timestamp"]) > self.refresh_interval:
                await self.get_proxy_list()

            self.check_cooldown_proxies()
            on_cooldown = {p["proxy"] for p in self.cooldown_proxies}
            available = [p for p in self.proxies["proxies"] if p not in on_cooldown]
            if not available:
                available = self.proxies["proxies"]

            return random.choice(available)
        except Exception as e:
            self.logger.write_log("error", f"Failed to get random proxy: {e}")


    def remove_proxy_from_list(self, proxy: str) -> None:
        """
        Removes a proxy from the cached proxy list if it exists.

        Args:
            proxy (str): The proxy to be removed from the list.
        """
        try:
            if proxy in self.proxies["proxies"]:
                self.proxies["proxies"].remove(proxy)
        except Exception as e:
            self.logger.write_log("error", f"Failed to remove proxy from list: {e}")


    async def get_working_proxy(self) -> str | None:
        """
        Returns a known working proxy, or falls back to a random proxy if none are available.

        Returns:
            str | None: A proxy URL, or None if an error occurs.
        """
        try:
            if not self.working_proxies:
                return await self.get_random_proxy()

            return random.choice(self.working_proxies)
        except Exception as e:
            self.logger.write_log("error", f"Failed to get working proxy: {e}")


    def add_working_proxy(self, proxy: str) -> None:
        """
        Adds a proxy to the list of working proxies and removes it from the cooldown list if it exists.

        Args:
            proxy (str): The proxy to be added to the working list.
        """
        try:
            if proxy not in self.working_proxies:
                self.working_proxies.append(proxy)

            self.remove_cooldown_proxy(proxy)
        except Exception as e:
            self.logger.write_log("error", f"Failed to add working proxy: {e}")


    def remove_working_proxy(self, proxy: str) -> None:
        """
        Removes a proxy from the list of working proxies if it exists.

        Args:
            proxy (str): The proxy to be removed from the working list.
        """
        try:
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
        except Exception as e:
            self.logger.write_log("error", f"Failed to remove working proxy: {e}")


    def add_cooldown_proxy(self, proxy: str) -> None:
        """
        Adds a proxy to the cooldown list with the current timestamp and removes it from the working list if it exists.
        
        Args:
            proxy (str): The proxy to be added to the cooldown list.
        """
        try:
            if not any(p["proxy"] == proxy for p in self.cooldown_proxies):
                self.cooldown_proxies.append({"proxy": proxy, "timestamp": time.time()})

            self.remove_working_proxy(proxy)
        except Exception as e:
            self.logger.write_log("error", f"Failed to add cooldown proxy: {e}")


    def remove_cooldown_proxy(self, proxy: str) -> None:
        """
        Removes a proxy from the cooldown list if it exists.

        Args:
            proxy (str): The proxy to be removed from the cooldown list.
        """
        try:
            self.cooldown_proxies = [p for p in self.cooldown_proxies if p["proxy"] != proxy]
        except Exception as e:
            self.logger.write_log("error", f"Failed to remove cooldown proxy: {e}")


    def check_cooldown_proxies(self) -> None:
        """
        Checks the cooldown list and removes any proxies that have been on cooldown for longer than the defined cooldown period.
        """
        try:
            if self.cooldown_proxies:
                current_time = time.time()
                self.cooldown_proxies = [p for p in self.cooldown_proxies if current_time - p['timestamp'] < self.cooldown_period]
        except Exception as e:
            self.logger.write_log("error", f"Failed to check cooldown proxies: {e}")
