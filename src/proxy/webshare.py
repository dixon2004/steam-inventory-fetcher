from utils.config import WEBSHARE_API_KEY
from utils.log import write_log
import aiohttp


class WebshareAPI:

    def __init__(self):
        """
        Initialize Webshare API.
        """
        self.proxy_list_url = "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page_size=100"


    async def call(self, url) -> dict:
        """
        Call Webshare API.
        
        Args:
            url (str): URL to call.
            
        Returns:
            dict: Response from the API.
        """
        try:
            async with aiohttp.ClientSession(raise_for_status=True) as session:
                async with session.get(url, headers={"Authorization": f"Token {WEBSHARE_API_KEY}"}) as response:
                    return await response.json()
        except Exception as e:
            write_log("error", f"[WebshareAPI] Failed to call API: {e}")


    async def get_proxy_list(self) -> list:
        """
        Get proxy list from Webshare API.
        """
        try:
            proxies = set()
            page = 1
            
            while True:
                url = f"{self.proxy_list_url}&page={page}"
                response = await self.call(url)
                if not response:
                    raise Exception("[WebshareAPI] Failed to get proxy list")
                
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
            write_log("error", f"[WebshareAPI] Failed to get proxy list: {e}")
