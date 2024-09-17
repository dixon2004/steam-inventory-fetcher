from fastapi import FastAPI, HTTPException
from utils.token import AuthorizationToken
from utils.config import WEBSHARE_API_KEY
from utils.port import PortConfiguration
from steam.inventory import SteamAPI
from utils.log import write_log
import asyncio
import uvicorn


app = FastAPI()
steam = SteamAPI()
auth = AuthorizationToken()
port_config = PortConfiguration()
        

@app.get("/steam/inventory/{steamID64}/{appID}/{contextID}")
async def get_steam_inventory(steamID64, appID, contextID, api_key=None):
    try:
        auth.check_auth_token(api_key)

        inventory_data = await asyncio.wait_for(steam.get_user_inventory(steamID64, appID, contextID), timeout=60)
        inventory_data["steamID"] = str(steamID64)
        inventory_data["appID"] = int(appID)
        inventory_data["contextID"] = int(contextID)

        write_log("info", f"Successfully fetched user's steam inventory ({steamID64})")
        return inventory_data
    except asyncio.TimeoutError:
        write_log("error", f"Timeout while fetching user's steam inventory ({steamID64})")
        raise HTTPException(status_code=504, detail=f"Timeout while fetching user's steam inventory ({steamID64})")       
    except Exception as e:
        write_log("error", f"Failed to fetch user's steam inventory: {e}")
        raise HTTPException(status_code=404, detail=f"Failed to fetch user's steam inventory: {e}")


if __name__ == "__main__":

    if not WEBSHARE_API_KEY:
        write_log("error", "Webshare API key is not set.")
        exit(1)

    port = port_config.get_port()
    if not port:
        write_log("error", "No available port found.")
        exit(1)

    write_log("info", f"Starting the API server on port {port}.")
    uvicorn.run(app, host="127.0.0.1", port=port)
