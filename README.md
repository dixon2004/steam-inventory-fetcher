# Steam Inventory Fetcher

## Overview

The **Steam Inventory Fetcher** is a robust tool designed to efficiently retrieve Steam user inventories. It features an advanced **smart proxy rotation system** that effectively manages high request volumes and mitigates rate limiting issues. This system is optimized for use with proxies from [**WebShare**](https://www.webshare.io/?referral_code=kpbfv7hi59qw), ensuring reliable performance and minimizing the risk of IP bans.

### Key Features

- **WebShare Proxy Integration**: Specifically designed to work with proxies from [**WebShare**](https://www.webshare.io/?referral_code=kpbfv7hi59qw).
- **Smart Proxy Rotation**: Automatically rotates proxies to bypass rate limits and increase request success rates.
- **Proxy Cooldown**: Implements a cooldown mechanism for rate-limited proxies to prevent excessive retries.
- **Proxy Caching**: Caches successful proxies to improve efficiency and reduce lookup times for future requests.
- **Fallback Mechanism**: Reverts to the last successful proxy after multiple failed attempts with different proxies.
- **Retry Limit**: Limits the number of attempts to 20 before marking the request as failed, ensuring resilience.

---

## Table of Contents

1. [How It Works](#how-it-works)
2. [Installation](#installation)
   - [Prerequisites](#prerequisites)
   - [Installation Steps](#installation-steps)
3. [API Usage](#api-usage)
4. [TF2Autobot Integration](#tf2autobot-integration)
5. [License](#license)

---

## How It Works

The **Steam Inventory Fetcher** uses a sophisticated proxy management system to handle requests:

1. **Proxy Pool Initialization**: On startup, the system initializes a pool of WebShare proxies.
2. **Request Handling**: For each inventory fetch request, the system selects an available proxy from the pool.
3. **Rate Limit Management**: If a proxy hits a rate limit, it is placed on cooldown, and a new proxy is selected for subsequent requests.
4. **Proxy Caching**: Proxies that successfully complete requests are cached to speed up future requests.
5. **Fallback Mechanism**: After 10 consecutive failed attempts with different proxies, the system reverts to the last successful proxy.
6. **Retry Limit**: The system attempts to fetch inventory data up to 20 times before considering the request failed.

---

## Installation

### Prerequisites

Before installing, ensure you have:

- **Docker** installed on your system.
- A **WebShare API Key** (obtain from [WebShare API Keys](https://proxy2.webshare.io/userapi/keys)).

### Installation Steps

#### Clone the Repository

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/dixon2004/steam-inventory-fetcher.git
cd steam-inventory-fetcher
```

#### Configure Environment Variables

1. **Create and Edit the `.env` File**:

   - Rename `template.env` to `.env` in the root directory.
   - Open `.env` and update the following:

     ```ini
     WEBSHARE_API_KEY = "your_webshare_api_key_here"
     AUTH_TOKEN = "your_auth_token_here"
     ```

   - **WEBSHARE_API_KEY**: Insert your WebShare API key obtain from [WebShare API Keys](https://proxy2.webshare.io/userapi/keys).
   - **AUTH_TOKEN**: If provided, the API will require this token for authentication. If left empty, authentication is disabled, allowing unrestricted access.

#### Run with Docker

1. **Build and Start the Service**:

    ```bash
    docker-compose up --build -d
    ```
    This will build the necessary Docker image and start the Steam Inventory Fetcher as a background service on port 8080.

2. **Stopping the Service**:

    To stop and remove the running containers, execute:
    ```bash
    docker-compose down
    ```

3. **Restarting the Service**:

    If you need to restart the service after making changes to the environment variables or code:
    ```bash
    docker-compose down && docker-compose up --build -d
    ```

4. **Checking Logs**:

    To monitor the service logs in real-time:
    ```bash
    docker-compose logs -f
    ```

---

## API Usage

The system includes auto-generated API documentation via Swagger. Access it at:

```
http://localhost:8080/docs
```

---

## TF2Autobot Integration

To integrate **Steam Inventory Fetcher** with [**TF2Autobot**](https://github.com/TF2Autobot/tf2autobot):

1. **Update Inventory Fetch Logic**:
   - Open `tf2autobot/src/classes/InventoryApis/SteamApis.ts`.

   - Replace the existing code:

     ```typescript
     import { UnknownDictionaryKnownValues } from 'src/types/common';
     import Bot from '../Bot';
     import InventoryApi from './InventoryApi';

     export default class SteamApis extends InventoryApi {
         constructor(bot: Bot) {
             super(bot, 'steamApis');
         }

         protected getURLAndParams(
             steamID64: string,
             appID: number,
             contextID: string
         ): [string, UnknownDictionaryKnownValues] {
             return [
                 `https://api.steamapis.com/steam/inventory/${steamID64}/${appID}/${contextID}`,
                 { api_key: this.getApiKey() }
             ];
         }
     }
     ```

     with:

     ```typescript
     import { UnknownDictionaryKnownValues } from 'src/types/common';
     import Bot from '../Bot';
     import InventoryApi from './InventoryApi';

     export default class SteamApis extends InventoryApi {
         constructor(bot: Bot) {
             super(bot, 'steamApis');
         }

         protected getURLAndParams(
             steamID64: string,
             appID: number,
             contextID: string
         ): [string, UnknownDictionaryKnownValues] {
             return [
                 `http://localhost:8080/steam/inventory/${steamID64}/${appID}/${contextID}`,
                 { api_key: 'your_actual_auth_token_here' }
             ];
         }
     }
     ```

   - Replace `'your_actual_auth_token_here'` with the Auth Token from your `.env` file.

2. **Handle Dependencies**:
   - **On Windows**: Delete `node_modules` and `dist` directories by right-clicking and selecting delete or using:

     ```cmd
     rmdir /s /q node_modules dist
     ```

   - **On Linux**: Remove `node_modules` and `dist` directories with:

     ```bash
     rm -rf node_modules dist
     ```

   - Reinstall dependencies and rebuild the project:

     ```bash
     npm install --no-audit && npm run build
     ```

3. **Test Integration**:
   - Test the updated functionality with TF2Autobot to ensure proper interaction with the new API endpoint and Auth Token.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.