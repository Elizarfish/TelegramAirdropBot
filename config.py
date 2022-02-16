# Enable / disable the airdrop
airdrop_live = True

# Telegram
api_token = (
    "token"  # More: https://core.telegram.org/bots#3-how-do-i-create-a-bot
)

db_table_name = "AirdropBot"
server_ip_address = "" # Insert your VPS Server IP
server_port = 443 # 443, 80 or 8443 (port needs to be 'open')

log_channel = -1001686083791  # Channel ID. Example: -1001355597767
admins = [1166588731]  # Telegram User ID's. Admins are able to execute command "/airdroplist"
airdrop_cap = 100  # Max airdrop submissions that are being accepted
wallet_changes = 1  # How often a user is allowed to change their wallet address. Command: "/restart"
task_bonus = 100 # Bonus for completing all tasks
referral_bonus = 10 # Bonus for the referrer
coin_ticker = "BTC" # Replace with your own coin ticker

# Requirements
telegram_channels = ["TheRealAirdropTest", "DaRealAirdropGroup"]

# MySQL Database
mysql_host = "localhost"
mysql_db = "TelegramAirdropBot"
mysql_user = "root"
mysql_pw = "toor"

texts = {
    "start_1": "Hello {},\n\nPlease click the button below to enrol into our airdrop.",
    "start_2": "You referred `{0}` people and earned `{1}` {2} tokens.\n\nYour provided data:\n\n - Wallet: `{3}`\n\n🚀 Earn *{4} {2}* for each referral!\n\n🔗 Your personal ref link is:\nhttps://t.me/{5}?start={6}",
    "telegram_requirements": "*Telegram*\n\nPlease join our Telegram Group and Channel.\n\nOnce you're done, click the button below!",
    "start_captcha": "Hi {},\n\n",
    "airdrop_start": "The airdrop didn't start yet.",
    "airdrop_address": "Type in your *ERC-20* wallet address:",
    "airdrop_max_cap": "Thank you for the interest but we reached the maximum cap.",
    "airdrop_walletused": "⚠️ That address has already been used. Use a different one.",
    "airdrop_confirmation": "✅ Your address has been added to airdrop list.",
    "airdrop_wallet_update": "✅ Your address has been updated.",
    "airdrop_submitted": "❌ You have already submitted your airdrop form.",
}