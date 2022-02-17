import config
import logging
import emoji_captcha
from io import BytesIO
import csv
from random import shuffle
from time import gmtime, strftime
import re
import pymysql
from cachetools import cached, TTLCache

import telebot
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

import ssl
from aiohttp import web

telebot.logger.setLevel(logging.INFO)

db_user_cache = TTLCache(maxsize=100, ttl=60)


WEBHOOK_HOST = config.server_ip_address
WEBHOOK_PORT = config.server_port
WEBHOOK_LISTEN = "0.0.0.0"  # In some VPS you may need to put here the IP addr.

WEBHOOK_SSL_CERT = "./webhook_cert.pem"  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = "./webhook_pkey.pem"  # Path to the ssl private key

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(config.api_token)

bot = telebot.TeleBot(config.api_token)

app = web.Application()


def get_connection():
    connection = pymysql.connect(
        host=config.mysql_host,
        user=config.mysql_user,
        password=config.mysql_pw,
        db=config.mysql_db,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
    return connection


def create_tables():
    connection = get_connection()
    with connection.cursor() as cursor:
        table_name = config.db_table_name
        try:
            cursor.execute(
                "	CREATE TABLE `"
                + table_name
                + "` ( `user_id` varchar(15) DEFAULT NULL,  `referrer_user_id` varchar(15) DEFAULT NULL,  `referrer_status` tinyint DEFAULT 0,  `address` varchar(42) DEFAULT NULL,  `changed_status` tinyint DEFAULT 0,  `captcha` varchar(15) DEFAULT NULL )"
            )
            print("Database tables created.")
            return create_tables
        except:
            pass


def get_referrer(text):
    return text.split()[1] if len(text.split()) > 1 else None


def get_airdrop_wallets():
    connection = get_connection()
    with connection.cursor() as cursor:
        sql = f"SELECT address FROM {config.db_table_name} WHERE address IS NOT NULL"
        cursor.execute(sql)
        tmp = []
        for user in cursor.fetchall():
            tmp.append(user["address"].lower())
        return tmp


def get_airdrop_users():
    connection = get_connection()
    with connection.cursor() as cursor:
        sql = f"SELECT user_id FROM {config.db_table_name} WHERE address IS NOT NULL"
        cursor.execute(sql)
        tmp = []
        for user in cursor.fetchall():
            tmp.append(user["user_id"])
        return tmp


def get_captcha_solved_users():
    connection = get_connection()
    with connection.cursor() as cursor:
        sql = f"SELECT user_id FROM {config.db_table_name} WHERE captcha IS NOT NULL"
        cursor.execute(sql)
        tmp = []
        for user in cursor.fetchall():
            tmp.append(user["user_id"])
        return tmp


def get_referral_data(user_id):
    connection = get_connection()
    with connection.cursor() as cursor:
        sql = f"SELECT COUNT(user_id) FROM {config.db_table_name} WHERE referrer_user_id = %s AND referrer_status = 1"
        cursor.execute(sql, user_id)
        referred_users = cursor.fetchone()['COUNT(user_id)']
        referral_bonus = (referred_users * config.referral_bonus) + config.task_bonus
        return {
            "reffered_user": referred_users,
            "referral_bonus": referral_bonus
        }


@cached(db_user_cache)
def get_db_data(user_id):
    connection = get_connection()
    with connection.cursor() as cursor:
        sql = f"SELECT address FROM {config.db_table_name} WHERE user_id = %s"
        cursor.execute(sql, user_id)
        data = cursor.fetchone()
        return {
            "address": data['address']
        }


def captcha_keyboard(captcha_emoji):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    random_emojis = emoji_captcha.EMOJI_RANGES_UNICODE[6]
    shuffle(random_emojis)
    result = list(''.join(random_emojis)[:-26])
    if captcha_emoji in result:
        for i in result:
            buttons.append(
                types.InlineKeyboardButton(text=i, callback_data='captcha_verification|{}|{}'.format(captcha_emoji, i)))
    else:
        new_result = result[:-1]
        new_result.append(captcha_emoji)
        shuffle(new_result)
        for i in new_result:
            buttons.append(
                types.InlineKeyboardButton(text=i, callback_data='captcha_verification|{}|{}'.format(captcha_emoji, i)))
    keyboard.add(*buttons)
    return keyboard


def cancel_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🛑 Cancel", callback_data="cancel_input"))
    return markup


def main_menu_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    return markup


def telegram_buttons():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = []
    for channel in config.telegram_channels:
        buttons.append(types.InlineKeyboardButton(text="🔗 Join {}".format(channel), url=f"https://t.me/{channel}"))
    buttons.append(types.InlineKeyboardButton(text="✅ Done the above!", callback_data="done_requirements_telegram"))
    keyboard.add(*buttons)
    return keyboard


def join_airdrop_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('🚀 Join Airdrop', callback_data='join_airdrop'))
    return markup


def joined_airdrop_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔄 Refresh (Every minute)", callback_data="refresh_data"))
    return markup


@bot.message_handler(func=lambda message: message.chat.type == "private", commands=["start"])
def handle_text(message):
    bot.send_chat_action(message.chat.id, "typing")
    connection = get_connection()
    with connection.cursor() as cursor:
        sql = f"SELECT EXISTS(SELECT user_id FROM {config.db_table_name} WHERE user_id = %s)"
        cursor.execute(sql, message.chat.id)
        result = cursor.fetchone()
        if not list(result.values())[0]:
            sql = f"INSERT INTO {config.db_table_name}(user_id) VALUES (%s)"
            cursor.execute(sql, message.chat.id)
        if message.chat.id in airdrop_users:
            referral_data = get_referral_data(message.chat.id)
            db_data = get_db_data(message.chat.id)
            bot.send_message(
                message.chat.id,
                config.texts["start_2"].format(
                    referral_data['reffered_user'], referral_data['referral_bonus'], config.coin_ticker,
                    db_data['address'], config.referral_bonus, bot.get_me().username.replace("_", "\_"), message.chat.id),
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=joined_airdrop_button()
            )
        elif message.chat.id in captcha_solved_user:
            bot.send_message(
                message.chat.id,
                config.texts["start_1"].format(message.from_user.first_name),
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=join_airdrop_button()
            )
        else:
            referrer = get_referrer(message.text)
            if referrer and referrer.isdigit():
                sql = f"UPDATE {config.db_table_name} SET referrer_user_id = %s WHERE user_id = %s"
                cursor.execute(sql, (int(referrer), message.chat.id))
            get_emoji = emoji_captcha.random_emoji()
            bot.send_message(
                message.chat.id,
                "Hi {},\n\n*Are you realy a human?!*\n\nProve it by clicking on: {} _({})_"
                    .format(message.from_user.first_name, get_emoji['emoji'], get_emoji['emoji_name']),
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=captcha_keyboard(get_emoji['emoji'])
            )


@bot.message_handler(
    func=lambda message: message.chat.type == "private" and message.from_user.id in captcha_solved_user,
    commands=["restart"])
def handle_text(message):
    bot.send_chat_action(message.chat.id, "typing")
    connection = get_connection()
    with connection.cursor() as cursor:
        sql = f"SELECT changed_status, address FROM {config.db_table_name} WHERE user_id = %s"
        cursor.execute(sql, message.chat.id)
        data = cursor.fetchone()
        if data['changed_status'] != config.wallet_changes and message.chat.id in airdrop_users:
            sql = f"UPDATE {config.db_table_name} SET address = NULL, changed_status = changed_status + 1 WHERE user_id = %s"
            cursor.execute(sql, message.chat.id)
            airdrop_users.pop(airdrop_users.index(message.chat.id))
            # airdrop_wallets.pop(airdrop_wallets.index(data['address']))
            bot.reply_to(
                message,
                config.texts["start_1"].format(message.from_user.first_name),
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=join_airdrop_button()
            )
        else:
            bot.reply_to(
                message,
                "⚠️ You either did not join the airdrop or you can't change your address data anymore."
            )


def address_check(message):
    bot.send_chat_action(message.chat.id, "typing")
    connection = get_connection()
    with connection.cursor() as cursor:
        if len(airdrop_users) >= config.airdrop_cap:
            bot.send_message(
                message.chat.id, config.texts["airdrop_max_cap"], parse_mode="Markdown"
            )
            bot.clear_step_handler(message)
        elif message.text.lower() in airdrop_wallets:
            msg = bot.reply_to(
                message,
                config.texts["airdrop_walletused"],
                parse_mode="Markdown",
                reply_markup=cancel_button(),
            )
            bot.register_next_step_handler(msg, address_check)
        elif message.content_type == 'text' and re.match(r"^(?=.{42}$).*", message.text):
            sql = f"UPDATE {config.db_table_name} SET address = %s WHERE user_id = %s"
            cursor.execute(sql, (message.text, message.chat.id))
            referral_data = get_referral_data(message.chat.id)
            db_data = get_db_data(message.chat.id)
            bot.send_message(
                message.chat.id,
                config.texts['airdrop_confirmation'] + config.texts["start_2"].format(
                    referral_data['reffered_user'], referral_data['referral_bonus'], config.coin_ticker,
                    db_data['address'], config.referral_bonus, bot.get_me().username.replace("_", "\_"), message.chat.id),
                parse_mode="Markdown",
                reply_markup=joined_airdrop_button(),
            )
            airdrop_wallets.append(message.text)
            airdrop_users.append(message.chat.id)
            # try:
            #     bot.send_message(
            #         config.log_channel,
            #         "🎈 *#Airdrop_Entry ({0}):*\n"
            #         " • User: [{1}](tg://user?id={2}) (#id{2})\n"
            #         " • Address: `{3}`\n"
            #         " • Time: `{4} UTC`".format(
            #             len(airdrop_users),
            #             bot.get_chat(message.chat.id).first_name,
            #             message.chat.id,
            #             message.text,
            #             strftime("%Y-%m-%d %H:%M:%S", gmtime()),
            #         ),
            #         parse_mode="Markdown",
            #         disable_web_page_preview=True,
            #     )
            # except:
            #     pass

            sql = f"SELECT referrer_user_id FROM {config.db_table_name} WHERE user_id = %s"
            cursor.execute(sql, message.chat.id)
            referrer = cursor.fetchone()['referrer_user_id']
            if referrer:
                sql = f"UPDATE {config.db_table_name} SET referrer_status = 1 WHERE user_id = %s"
                cursor.execute(sql, message.chat.id)

        else:
            msg = bot.reply_to(
                message,
                "❌ Invalid address. Try again:",
                parse_mode="Markdown",
                reply_markup=cancel_button(),
            )
            bot.register_next_step_handler(msg, address_check)


@bot.message_handler(func=lambda message: message.chat.id in config.admins, commands=["airdroplist"])
def handle_text(message):
    bot.send_chat_action(message.chat.id, "upload_document")
    connection = get_connection()
    with connection.cursor() as cursor:
        sql = f"SELECT address, user_id FROM {config.db_table_name}"
        cursor.execute(sql)
        with open('airdrop-list.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "User ID", "Twitter Username", "Wallet address", "Referred Users", "Total Balance"])
            for user in cursor.fetchall():
                if user["address"] is not None:
                    address = user["address"]
                    user_id = user['user_id']
                    user_name = "{}{}".format(bot.get_chat(user_id).first_name,
                                ' {0}'.format(bot.get_chat(user_id).last_name) if bot.get_chat(user_id).last_name else '')
                    referral_data = get_referral_data(user_id)
                    writer.writerow([user_name, user_id, address, referral_data['reffered_user'], referral_data['referral_bonus']])

        airdrop_list = open("airdrop-list.csv", 'rb')
        bot.send_document(message.chat.id, airdrop_list, caption=f"I've attached the airdroplist.")    
    
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    connection = get_connection()
    with connection.cursor() as cursor:
        if "captcha_verification" in call.data:
            clicked_emoji = call.data.split("|")[2]
            verification_emoji = call.data.split("|")[1]
            if call.message.chat.id in captcha_solved_user:
                bot.answer_callback_query(call.id, "❌ You already solved the captcha.", show_alert=True)
            elif verification_emoji == clicked_emoji:
                sql = f"UPDATE {config.db_table_name} SET captcha = 1 WHERE user_id = %s"
                cursor.execute(sql, call.message.chat.id)
                captcha_solved_user.append(call.message.chat.id)
                bot.answer_callback_query(call.id, "✅ Captcha solved.")
                bot.edit_message_text(
                    chat_id=call.message.chat.id, message_id=call.message.message_id,
                    text=config.texts["start_1"].format(call.message.chat.first_name),
                    parse_mode="Markdown", disable_web_page_preview=True, reply_markup=join_airdrop_button()
                )
            else:
                get_emoji = emoji_captcha.random_emoji()
                bot.edit_message_text(
                    chat_id=call.message.chat.id, message_id=call.message.message_id,
                    text="Hi {},\n\n*Are you realy a human?!*\n\nProve it by clicking on: {} _({})_"
                        .format(call.message.chat.first_name, get_emoji['emoji'], get_emoji['emoji_name']),
                    parse_mode="Markdown", disable_web_page_preview=True,
                    reply_markup=captcha_keyboard(get_emoji['emoji'])
                )
                bot.answer_callback_query(call.id, "❌ Invalid Captcha. Please try again.", show_alert=True)

        elif call.data == "join_airdrop":
            if call.message.chat.id in airdrop_users:
                bot.edit_message_text(
                    chat_id=call.message.chat.id, message_id=call.message.message_id,
                    text=config.texts['airdrop_submitted']
                )
            elif not config.airdrop_live:
                bot.answer_callback_query(call.id, config.texts["airdrop_start"], show_alert=True)
            elif len(airdrop_users) >= config.airdrop_cap:
                bot.answer_callback_query(call.id, config.texts["airdrop_max_cap"], show_alert=True)
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id, message_id=call.message.message_id,
                    text=config.texts["telegram_requirements"].format(call.message.from_user.first_name),
                    parse_mode="Markdown", disable_web_page_preview=True, reply_markup=telegram_buttons()
                )

        elif call.data == "refresh_data":
            try:
                referral_data = get_referral_data(call.message.chat.id)
                db_data = get_db_data(call.message.chat.id)
                bot.edit_message_text(
                    chat_id=call.message.chat.id, message_id=call.message.message_id,
                    text=config.texts["start_2"].format(
                        referral_data['reffered_user'], referral_data['referral_bonus'], config.coin_ticker,
                        db_data['address'], config.referral_bonus, bot.get_me().username.replace("_", "\_"),
                        call.message.chat.id),
                    parse_mode="Markdown",
                    disable_web_page_preview=True,
                    reply_markup=joined_airdrop_button()
                )
            except:
                bot.answer_callback_query(call.id, "❌ Nothing to update. Keep sharing :)", show_alert=False)

        elif call.data == "cancel_input":
            if len(airdrop_users) >= config.airdrop_cap:
                bot.edit_message_text(
                    chat_id=call.message.chat.id, message_id=call.message.message_id,
                    text="✅ Operation canceled.\n\nℹ️ The airdrop reached its max cap."
                )
            elif call.message.chat.id in airdrop_users:
                bot.edit_message_text(
                    chat_id=call.message.chat.id, message_id=call.message.message_id,
                    text="✅ Operation canceled.",
                    reply_markup=main_menu_button()
                )
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id, message_id=call.message.message_id,
                    text="✅ Operation canceled.",
                    reply_markup=join_airdrop_button()
                )
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)

        elif call.data == 'submit_wallet_address':
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            if call.message.chat.id in airdrop_users:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=config.texts['airdrop_submitted'])
            elif len(airdrop_wallets) >= config.airdrop_cap:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=config.texts['airdrop_max_cap'], parse_mode='Markdown')
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=config.texts['airdrop_address'], parse_mode='Markdown',
                                      disable_web_page_preview=True)
                bot.register_next_step_handler(call.message, address_check)

        elif call.data == 'done_requirements_telegram':
            #userinfo_1 = bot.get_chat_member("-", call.message.chat.id)
            #memberstatus_1 = userinfo_1.status
            userinfo_2 = bot.get_chat_member(-1001474922733, call.message.chat.id)
            memberstatus_2 = userinfo_2.status

            if call.message.chat.id in airdrop_users:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=config.texts['airdrop_submitted'])
            elif len(airdrop_wallets) >= config.airdrop_cap:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=config.texts['airdrop_max_cap'], parse_mode='Markdown')
            elif memberstatus_2 == 'left': # or memberstatus_1 == 'left':
                bot.answer_callback_query(call.id, "⚠️ You didn't join all Groups/Channels.", show_alert=True)
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=config.texts['airdrop_address'], parse_mode='Markdown',
                                    disable_web_page_preview=True)
                bot.register_next_step_handler(call.message, address_check)


create_db_tables = create_tables()
airdrop_users = get_airdrop_users()
captcha_solved_user = get_captcha_solved_users()
airdrop_wallets = get_airdrop_wallets()

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

create_db_tables


# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(
    url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH, certificate=open(WEBHOOK_SSL_CERT, "r")
)

# Build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

# Process webhook calls
async def handle(request):
    if request.match_info.get("token") == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)


app.router.add_post("/{token}/", handle)

# Start aiohttp server
web.run_app(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT,
    ssl_context=context,
)
