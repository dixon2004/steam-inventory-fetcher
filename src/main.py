from fastapi import FastAPI, HTTPException
from utils.token import AuthorizationToken
from steam.inventory import SteamAPI
from utils.logger import SyncLogger
import asyncio


app = FastAPI()
steam = SteamAPI()
auth = AuthorizationToken()
logger = SyncLogger("SteamInventoryFetcherAPI")


@app.get("/health")
async def health_check():
    try:
        return {"status": "ok"}
    except Exception as e:
        logger.write_log("error", f"Failed to perform health check: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")


@app.get("/steam/inventory/{steamID64}/{appID}/{contextID}")
async def get_steam_inventory(steamID64, appID, contextID, api_key=""):
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

        logger.write_log("info", f"Successfully fetched user's steam inventory ({steamID64})")
        return inventory_data
    except asyncio.TimeoutError:
        logger.write_log("error", f"Timeout while fetching user's steam inventory ({steamID64})")
        raise HTTPException(status_code=504, detail=f"Timeout while fetching user's steam inventory ({steamID64})")       
    except Exception as e:
        logger.write_log("error", f"Failed to fetch user's steam inventory ({steamID64}): {e}")
        raise HTTPException(status_code=404, detail=f"Failed to fetch user's steam inventory ({steamID64}): {e}")
