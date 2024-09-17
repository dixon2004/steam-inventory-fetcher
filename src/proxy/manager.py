from proxy.webshare import WebshareAPI
from utils.log import write_log
import random
import time


class ProxyManager:

    def __init__(self) -> None:
        """
        Initialize Proxy Manager.
        """
        self.webshare = WebshareAPI()

        self.proxies = None
        self.working_proxies = list()
        self.cooldown_proxies = list()

        self.cooldown_period = 60 * 30
        self.refresh_interval = 60 * 60 * 12

        
    async def get_proxy_list(self) -> str:
        """
        Get proxy list from cache or Webshare API.

        Returns:
            str: Proxy URL.
        """
        try:
            if not self.proxies or (time.time() - self.proxies["timestamp"]) > self.refresh_interval:
                proxies = await self.webshare.get_proxy_list()
                if not proxies:
                    raise Exception("[ProxyManager] Failed to get proxy list")
                self.proxies = {"timestamp": time.time(), "proxies": proxies}

            return self.proxies["proxies"]
        except Exception as e:
            write_log("error", f"[ProxyManager] Failed to get proxy list: {e}")
    

    async def get_random_proxy(self) -> str:
        """
        Get random proxy from the proxy list.

        Returns:
            str: Proxy URL.
        """
        try:
            if not self.proxies or (time.time() - self.proxies["timestamp"]) > self.refresh_interval:
                await self.get_proxy_list()

            self.check_cooldown_proxies()
            proxies = self.proxies["proxies"]
            return random.choice(proxies)
        except Exception as e:
            write_log("error", f"[ProxyManager] Failed to get random proxy: {e}")


    def remove_proxy_from_list(self, proxy: str) -> None:
        """
        Remove proxy from the proxy list.

        Args:
            proxy (str): Proxy URL.
        """
        try:
            if proxy in self.proxies["proxies"]:
                self.proxies["proxies"].remove(proxy)
        except Exception as e:
            write_log("error", f"[ProxyManager] Failed to remove proxy from list: {e}")


    async def get_working_proxy(self) -> str:
        """
        Get working proxy from the proxy list.

        Returns:
            str: Proxy URL.
        """
        try:
            if not self.working_proxies:
                return await self.get_random_proxy()

            return random.choice(self.working_proxies)
        except Exception as e:
            write_log("error", f"[ProxyManager] Failed to get working proxy: {e}")


    def add_working_proxy(self, proxy: str) -> None:
        """
        Add working proxy to the working proxy list.

        Args:
            proxy (str): Proxy URL.
        """
        try:
            if proxy not in self.working_proxies:
                self.working_proxies.append(proxy)

            self.remove_cooldown_proxy(proxy)
        except Exception as e:
            write_log("error", f"[ProxyManager] Failed to add working proxy: {e}")


    def remove_working_proxy(self, proxy: str) -> None:
        """
        Remove working proxy from the working proxy list.

        Args:
            proxy (str): Proxy URL.
        """
        try:
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
        except Exception as e:
            write_log("error", f"[ProxyManager] Failed to remove working proxy: {e}")


    def add_cooldown_proxy(self, proxy: str) -> None:
        """
        Add cooldown proxy to the cooldown proxy list.

        Args:
            proxy (str): Proxy URL.
        """
        try:
            if proxy not in self.cooldown_proxies:
                self.cooldown_proxies.append({"proxy": proxy, "timestamp": time.time()})

            self.remove_working_proxy(proxy)
        except Exception as e:
            write_log("error", f"[ProxyManager] Failed to add cooldown proxy: {e}")


    def remove_cooldown_proxy(self, proxy: str) -> None:
        """
        Remove cooldown proxy from the cooldown proxy list.

        Args:
            proxy (str): Proxy URL.
        """
        try:
            for cooldown_proxy in self.cooldown_proxies:
                if cooldown_proxy["proxy"] == proxy:
                    self.cooldown_proxies.remove(cooldown_proxy)
        except Exception as e:
            write_log("error", f"[ProxyManager] Failed to remove cooldown proxy: {e}")


    def check_cooldown_proxies(self) -> None:
        """
        Remove proxies from the cooldown list if the cooldown period has expired.
        """
        try:
            if self.cooldown_proxies:
                current_time = time.time()
                self.cooldown_proxies = [p for p in self.cooldown_proxies if current_time - p['timestamp'] < self.cooldown_period]
        except Exception as e:
            write_log("error", f"[ProxyManager] Failed to check cooldown proxies: {e}")
