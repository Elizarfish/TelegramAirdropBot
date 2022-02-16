## Pre-Installation
1. For best performance I recommend to run the bot on a VPS.
   1. I personally use Hetzner. 
2. Recommended are Ubuntu 19 or 20 with at least 1GB Ram and 10 GB HDD/SDD.
3. Install MySQL: https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04
4. Add your Airdrop Bot to your Channels / Groups and make it **ADMIN**.


## Installation
1. Log into MySQL (`sudo mysql`) and create a dedicated database and user with the following commands:
   1. `CREATE DATABASE TelegramAirdropBot;`
   2. `CREATE USER 'AirdropUser'@'localhost' IDENTIFIED BY '<YOUR-PASSWORD>';`
   3. `GRANT ALL PRIVILEGES ON TelegramAirdropBot . * TO 'AirdropUser'@'localhost';`
   4. `exit;`
2. Upload the Pro version to your VPS by using a program like Putty (for Windows) or Cyberduck (for Mac)
3. Create your virtual environment `python3 -m venv Telegram-Airdrop-Bot-PRO` 
4. Activate it `source Telegram-Airdrop-Bot-PRO/bin/activate && cd Telegram-Airdrop-Bot-PRO`
5. Install all requirements `pip install -r requirements.txt`
6. The bot runs behind a webhook, so you have to create a SSL cert first:
   1. `openssl genrsa -out webhook_pkey.pem 2048`
   2. `openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem`
      1. !! When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply with your **Server IP**.
7. Edit and update the `config.py` file.
8. Run the bot `python main.py`
9. To run the bot in the background I can recommend **systemd** or **PM2**.
   1. PM2 Guide: https://pm2.io/blog/2018/09/19/Manage-Python-Processes
      1. Useful command:
         1. Start the bot: pm2 stat main.py --name Telegram-Airdrop-Bot-PRO
         2. Stop/Start the bot: pm2 stop Telegram-Airdrop-Bot-PRO / pm2 start Telegram-Airdrop-Bot-PRO
         3. View logs: pm2 log Telegram-Airdrop-Bot-PRO
