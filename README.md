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
     - [Clone the Repository](#clone-the-repository)
     - [Set Up a Virtual Environment](#set-up-a-virtual-environment)
     - [Install Dependencies](#install-dependencies)
     - [Configure Environment Variables](#configure-environment-variables)
     - [Run the System](#run-the-system)
   - [Optional: PM2 Setup for Linux Users](#optional-pm2-setup-for-linux-users)
     - [Install PM2](#install-pm2)
     - [Start the System with PM2](#start-the-system-with-pm2)
     - [Configure Log Rotation](#configure-log-rotation)
     - [Enable PM2 on System Startup](#enable-pm2-on-system-startup)
     - [Monitor the System](#monitor-the-system)
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

- **Python 3.8** or higher installed.
- A **WebShare API Key** (obtain from [WebShare API Keys](https://proxy2.webshare.io/userapi/keys)).
- An **Auth Token** for API access (optional but recommended).

### Installation Steps

#### Clone the Repository

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/dixon2004/steam-inventory-fetcher.git
cd steam-inventory-fetcher
```

#### Set Up a Virtual Environment

Create and activate a virtual environment to manage dependencies:

- **Linux/macOS**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

- **Windows**:
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```

#### Install Dependencies

Install the necessary Python packages:

```bash
pip install -r requirements.txt
```

#### Configure Environment Variables

1. **Create and Edit the `.env` File**:
   - Rename `template.env` to `.env` in the root directory.
   - Open `.env` and update the following:

     ```ini
     WEBSHARE_API_KEY = "your_webshare_api_key_here"
     AUTH_TOKEN = "your_auth_token_here"  # Leave empty for auto-generation
     SERVER_PORT = 8000  # Default port; modify if needed
     ```

   - **WEBSHARE_API_KEY**: Insert your WebShare API key obtain from [WebShare API Keys](https://proxy2.webshare.io/userapi/keys).
   - **AUTH_TOKEN**: Optionally, provide an Auth Token. If left empty, the system will generate one automatically and display it in the logs.
   - **SERVER_PORT**: Defaults to `8000`. Modify if required. If the port is in use, the system will automatically select an available one and display it in the logs.

#### Run the System

Start the system with:

```bash
python src/main.py
```

### Optional: PM2 Setup for Linux Users

**PM2** is a process manager that simplifies the management of your application, including automatic restarts and log handling.

#### Install PM2

Install PM2 globally using npm:

```bash
npm install pm2 -g
```

#### Start the System with PM2

Run the system as a background service with PM2:

```bash
pm2 start src/main.py --name steam-inventory-fetcher --interpreter python3
```

#### Configure Log Rotation

For details on setting up log rotation with PM2, refer to the [PM2 Logrotate Documentation](https://github.com/keymetrics/pm2-logrotate).

#### Enable PM2 on System Startup

Ensure PM2 restarts automatically on boot:

```bash
pm2 startup
pm2 save
```

#### Monitor the System

Monitor the system’s status and logs with:

```bash
pm2 status
pm2 logs
```

---

## API Usage

The system includes auto-generated API documentation via Swagger. Access it at:

```
http://localhost:<port>/docs
```

Replace `<port>` with the port number from your `.env` file or the one chosen by the system.

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
                 `http://localhost:<port>/steam/inventory/${steamID64}/${appID}/${contextID}`,
                 { api_key: 'your_actual_auth_token_here' }
             ];
         }
     }
     ```

   - Replace `<port>` with the port number from your `.env` file or the one automatically selected by the system.
   - Substitute `'your_actual_auth_token_here'` with the Auth Token from your `.env` file or the auto-generated one.

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