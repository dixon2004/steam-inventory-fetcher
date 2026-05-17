from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
from utils.token import AuthorizationToken
from steam.inventory import SteamAPI
from utils.logger import SyncLogger
import aiohttp
import asyncio


logger = SyncLogger("SteamInventoryFetcherAPI")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with aiohttp.ClientSession() as session:
        app.state.steam = SteamAPI(session)
        app.state.auth = AuthorizationToken()
        yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint to verify that the API is running and responsive.

    Returns:
        dict: A dictionary containing the status of the API.
    """
    return {"status": "ok"}


@app.get("/steam/inventory/{steamID64}/{appID}/{contextID}")
async def get_steam_inventory(request: Request, steamID64, appID, contextID, api_key: str = "") -> dict:
    """
    Fetches a user's Steam inventory. Requires a valid API key.

    Args:
        request (Request): The incoming HTTP request.
        steamID64 (str): The 64-bit Steam ID of the target user.
        appID (str): Steam application ID (e.g., "440" for TF2).
        contextID (str): Inventory context ID (e.g., "2" for TF2).
        api_key (str, optional): API key for authentication. Defaults to "".

    Returns:
        dict: The user's inventory data.
    """
    steam: SteamAPI = request.app.state.steam
    auth: AuthorizationToken = request.app.state.auth
    try:
        if not auth.check_auth_token(api_key):
            logger.write_log("error", f"Failed to fetch user's steam inventory ({steamID64}): Invalid API key")
            raise HTTPException(status_code=401, detail="Invalid API key")

        inventory_data = await asyncio.wait_for(steam.get_user_inventory(steamID64, appID, contextID), timeout=60)

        if not inventory_data:
            logger.write_log("error", f"Failed to fetch user's steam inventory ({steamID64}): No data found")
            raise HTTPException(status_code=404, detail=f"Failed to fetch user's steam inventory ({steamID64}): No data found")

        inventory_data["steamID"] = str(steamID64)
        inventory_data["appID"] = int(appID)
        inventory_data["contextID"] = int(contextID)

        logger.write_log("info", f"Successfully fetched user's steam inventory ({steamID64}) with {len(inventory_data.get('assets', []))} items")
        return inventory_data
    except HTTPException:
        raise
    except asyncio.TimeoutError:
        logger.write_log("error", f"Timeout while fetching user's steam inventory ({steamID64})")
        raise HTTPException(status_code=504, detail=f"Timeout while fetching user's steam inventory ({steamID64})")
    except Exception as e:
        logger.write_log("error", f"Failed to fetch user's steam inventory ({steamID64}): {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch user's steam inventory ({steamID64}): {e}")
