## Pre-Installation
1. For best performance I recommend to run the bot on a VPS.
   1. I personally use Hetzner. By using my referral link you would get a free 20 EUR credit: https://hetzner.cloud/?ref=tQ1NdT8zbfNY
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


## Предварительная установка
1. Для лучшей производительности я рекомендую запускать бота на VPS.
   1. Я лично пользуюсь Hetzner. Используя мою реферальную ссылку, вы получите бесплатный кредит в размере 20 евро: https://hetzner.cloud/?ref=tQ1NdT8zbfNY.
2. Рекомендуется использовать Ubuntu 19 или 20 с оперативной памятью не менее 1 ГБ и жестким диском или твердотельным накопителем емкостью 10 ГБ.
3. Установите MySQL: https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04.
4. Добавьте своего Airdrop Bot в свои каналы/группы и сделайте его **АДМИНИСТРАТОРОМ**.


## Установка
1. Войдите в MySQL (`sudo mysql`) и создайте выделенную базу данных и пользователя с помощью следующих команд:
   1. `СОЗДАТЬ БАЗА ДАННЫХ TelegramAirdropBot;`
   2. `СОЗДАЙТЕ ПОЛЬЗОВАТЕЛЯ 'AirdropUser'@'localhost', ИДЕНТИФИЦИРОВАННОГО '<ВАШ-ПАРОЛЬ>';`
   3. ПРЕДОСТАВЬТЕ ВСЕ ПРИВИЛЕГИИ НА TelegramAirdropBot. * TO 'AirdropUser'@'localhost';`
   4. «выход»;
2. Загрузите версию Pro на свой VPS с помощью такой программы, как Putty (для Windows) или Cyberduck (для Mac).
3. Создайте виртуальную среду `python3 -m venv Telegram-Airdrop-Bot-PRO`
4. Активируйте его `source Telegram-Airdrop-Bot-PRO/bin/activate && cd Telegram-Airdrop-Bot-PRO`
5. Установите все требования `pip install -r requirements.txt`
6. Бот работает через веб-перехватчик, поэтому сначала необходимо создать сертификат SSL:
   1. `openssl genrsa -out webhook_pkey.pem 2048`
   2. `openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem`
      1. !! Когда вас спросят «Общее имя (например, полное доменное имя сервера или ВАШЕ имя)», вы должны ответить своим ** IP-адресом сервера **.
7. Отредактируйте и обновите файл config.py.
8. Запустите бота `python main.py`
9. Для запуска бота в фоновом режиме могу порекомендовать **systemd** или **PM2**.
   1. Руководство по PM2: https://pm2.io/blog/2018/09/19/Manage-Python-Processes
      1. Полезная команда:
         1. Запустите бота: pm2 stat main.py --name Telegram-Airdrop-Bot-PRO
         2. Остановить/запустить бота: pm2 stop Telegram-Airdrop-Bot-PRO / pm2 start Telegram-Airdrop-Bot-PRO
         3. Просмотр логов: журнал pm2 Telegram-Airdrop-Bot-PRO