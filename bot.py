# -----------------------------------------------------------------------------------
# 👑 𝗚𝗔𝗗𝗚𝗘𝗧 𝗚𝗜𝗩𝗘𝗔𝗪𝗔𝗬 𝗕𝗢𝗧 𝗛𝗨𝗕 (v22.0 - The 'Quantum-Flux' Build) 👑
# 𝗗𝗘𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡: v21.0 এর উপর ভিত্তি করে তৈরি।
#
# 𝗙𝗘𝗔𝗧𝗨𝗥𝗘𝗦 (v22.0):
#   1. [ULTRA-PREMIUM] 🚀 Interactive Redeem Flow: ইউজাররা এখন
#      বাটন চেপে সরাসরি কোড পাঠাতে পারবে, /redeem কমান্ডের দরকার নেই।
#      এটি ইউজার এক্সপেরিয়েন্সকে একটি অ্যাপের মতো 'ফ্লুইড' করে তোলে।
#
#   2. [ULTRA-PREMIUM] 💎 Admin Prize Search: অ্যাডমিন প্যানেলে
#      "🔍 Search Stock" বাটন যোগ করা হয়েছে, যা দিয়ে অ্যাডমিনরা
#      যেকোনো প্রাইজ বা কোড মুহূর্তের মধ্যে খুঁজে বের করতে পারবে।
#
#   3. [ULTRA-PREMIUM] ⚡ Quantum User Analytics: ইউজার ম্যানেজমেন্ট
#      প্যানেলে "🎁 View User Winnings" বাটন যোগ করা হয়েছে, যা
#      যেকোনো ইউজারের জেতা সকল প্রাইজের রিপোর্ট দেখায়।
#
#   4. [PREMIUM] 📊 Enhanced Statistics: স্ট্যাটস প্যানেল এখন
#      "Top 3 Most Redeemed Giveaways"-এর লিস্ট দেখায়।
#
#   5. [KEPT] ✨ 'Quantum' User Management (Forward & Reply) (v21.0)
#   6. [KEPT] 🚀 One-Click Smart Post (v21.0)
#   7. [KEPT] 💎 Dual-Mode Stocking (v21.0)
#   8. [KEPT] ⚡ Dynamic 'Live' UI (v21.0)
#   9. [KEPT] 🚀 Multi-Threaded Core (v20.0)
#
# 𝗔𝗨𝗧𝗛𝗢𝗥: Shuvo Hassan (Concept & Vision)
# 𝗗𝗘𝗩𝗘𝗟𝗢𝗣𝗘𝗗 𝗕𝗬: Your AI Assistant (The 'Quantum-Flux' Build v22.0)
# -----------------------------------------------------------------------------------

import os
import telebot
from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, BotCommand,
    InlineQueryResultArticle, InputTextMessageContent
)
import random
import time
import json
import threading # v20.0: For Multi-Threading
import uuid
from datetime import datetime
import re
import pytz
import io
import math
import html
import requests
from collections import defaultdict # v22.0: For stats

# -----------------------------------------------------------------------------------
# ⚙️ --- MAIN CONFIGURATION --- ⚙️
# -----------------------------------------------------------------------------------

# --- v5.0: The Bot Owner (YOU) ---
OWNER_ID = 6074463370  # ⚠️ This is YOUR ID.

# --- Bot Token ---
BOT_TOKEN = "7984240580:AAEth0NgopkraueMYdTwHq5JDGYfICqxge0"  # ⚠️ Put your bot's token here

# --- Database file name ---
DATA_FILE = "ultimate_giveaway_db_v22.json"  # v22.0 Database

# --- v3.0 Timezone Configuration ---
BOT_TIMEZONE = pytz.timezone("Asia/Dhaka")

# --- Global Bot Variables ---
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML', threaded=False)
data_lock = threading.Lock()
# v22.0: Split task queues for Admins and Users for clarity and stability
admin_task_queue = {}
user_task_queue = {}

# --- v12.0: Constants ---
PRIZES_PER_PAGE = 5 
LEADERBOARD_COUNT = 5
TOP_GIVEAWAY_COUNT = 3 # v22.0

# --- URL Regex for validation ---
URL_REGEX = re.compile(
    r'^(?:http|ftp)s?://'
    r'(?:(?:[A-Z09](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    r'(?::\d+)?'
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

# -----------------------------------------------------------------------------------
# 🚀 --- v20.0: THREADING HELPER --- 🚀
# -----------------------------------------------------------------------------------

def process_threaded(target_func, *args):
    """
    v20.0: Runs any function in a new thread to keep the bot responsive.
    """
    try:
        threading.Thread(target=target_func, args=args).start()
    except Exception as e:
        print(f"!!! THREADING ERROR: Failed to start thread for {target_func.__name__}: {e} !!!")

# -----------------------------------------------------------------------------------
# 🛠️ --- v14.0: CORE HELPER FUNCTIONS --- 🛠️
# -----------------------------------------------------------------------------------

def escape(text):
    if text is None:
        return ""
    return html.escape(str(text))

def get_live_time():
    return datetime.now(BOT_TIMEZONE).strftime("%d-%b-%Y %I:%M %p")

# -----------------------------------------------------------------------------------
# 🎨 --- PREMIUM UI FACTORY (v22.0 - 'Quantum-Flux' UI) --- 🎨
# -----------------------------------------------------------------------------------
class UIFactory:
    EMOJIS = {
        'crown': '👑', 'gift': '🎁', 'ticket': '🎟️', 'success': '✅', 'error': '🚫',
        'warn': '⚠️', 'admin': '🛡️', 'user': '👤', 'db': '💾', 'stats': '📊',
        'broadcast': '📡', 'settings': '⚙️', 'link': '🔗', 'check': '🔍',
        'pic': '🖼️', 'export': '📤', 'owner': '💎', 'group': '👥', 'post': '📢',
        'upload': '📤', 'star': '✨', 'rocket': '🚀', 'party': '🎉', 'back': '«',
        'plus': '➕', 'trash': '🗑️', 'list': '🗃️', 'download': '📥', 'alert': '🔔',
        'ban': '🚫', 'unban': '✅', 'edit': '✏️', 'users': '👥', 'clone': '🧬',
        'welcome': '👋', 'clock': '🕑', 'confirm': '❓', 'rename': '📝',
        'lock': '🔒', 'unlock': '🔓', 'new': '🌟', 'search': '🔍', 'home': '🏠',
        'pro': '🧑‍💻', 'magic': '🪄', 'trophy': '🏆' # v22.0
    }
    
    DIVIDER = "────────────────────"

    # --- User Messages ---
    @staticmethod
    def welcome_message(user, stats):
        """
        v22.0: 'Dynamic Live' UI.
        """
        user_name = escape(user.first_name.encode('utf-8').decode('utf-8'))
        user_id = user.id
        user_link = f'<a href="tg://user?id={user_id}">{user_name}</a>'

        title = f"𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗧𝗛𝗘 𝗕𝗢𝗧 𝗛𝗨𝗕 {UIFactory.EMOJIS['crown']}"
        body = (f"Hello <b>{user_link}</b>! {UIFactory.EMOJIS['welcome']}\n"
                f"Welcome to the <b>Gadget Giveaway Bot Hub</b>.\n\n"
                f"ℹ️  Use the buttons below to get started or\n"
                f"   manually send <code>/redeem CODE-XXXX-XXXX</code>")
        
        footer = (
            f"{UIFactory.EMOJIS['rocket']} <b>Active:</b> {stats['active']} | "
            f"{UIFactory.EMOJIS['party']} <b>Redeemed:</b> {stats['redeemed']} | "
            f"{UIFactory.EMOJIS['users']} <b>Users:</b> {stats['users']}"
        )

        markup = InlineKeyboardMarkup(row_width=3)
        markup.add(
            # v22.0: Interactive Redeem
            InlineKeyboardButton(f"{UIFactory.EMOJIS['ticket']} Redeem", callback_data="user_redeem_start"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['gift']} My Winnings", callback_data="user_my_winnings"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['stats']} Live Stats", callback_data="user_public_stats")
        )
        markup.add(
            InlineKeyboardButton(f"{UIFactory.EMOJIS['crown']} Top Winners", callback_data="user_top_winners"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['home']} Main Menu", callback_data="user_main_menu")
        )

        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}", markup
    
    # v22.0: New prompt for Interactive Redeem
    @staticmethod
    def redeem_prompt_message():
        title = f"{UIFactory.EMOJIS['ticket']} 𝗥𝗘𝗗𝗘𝗘𝗠 𝗖𝗢𝗗𝗘"
        body = "💬 <b>Please send me your redeem code.</b>\n\n(Send <code>/cancel</code> to return to the menu.)"
        footer = "Your code will be processed instantly."
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}"

    @staticmethod
    def redeem_success_message(user_name, prize_name, prize_text, admin_username, redeem_code):
        title = f"{UIFactory.EMOJIS['party']} 𝗖𝗢𝗡𝗚𝗥𝗔𝗧𝗨𝗟𝗔𝗧𝗜𝗢𝗡𝗦, {escape(user_name)}!"
        body = (f"You have successfully redeemed:\n"
                f"<b>{escape(prize_name)}</b>\n"
                f"<i>(Code: <code>{escape(redeem_code)}</code>)</i>\n\n"
                f"<b>{UIFactory.EMOJIS['gift']} Here is your prize:</b>\n"
                f"<pre>{escape(prize_text)}</pre>\n"
                f"{UIFactory.DIVIDER}\n"
                f"<b>{UIFactory.EMOJIS['alert']} PLEASE PROVIDE PROOF {UIFactory.EMOJIS['alert']}</b>\n"
                f"Please send a screenshot to <b>{escape(admin_username)}</b> as proof!\n\n"
                f"<b>{UIFactory.EMOJIS['warn']} Warning:</b> Failure to send a review may result in\n"
                f"a ban from future giveaways.")
        footer = "Thank you for participating!"
        
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}"

    @staticmethod
    def my_winnings_message(user_name, winnings):
        title = f"{UIFactory.EMOJIS['gift']} {escape(user_name)}'s 𝗪𝗜𝗡𝗡𝗜𝗡𝗚𝗦"
        if not winnings:
            body = f"{UIFactory.EMOJIS['error']} You haven't won any prizes yet."
        else:
            body = f"Here is a list of all <b>{len(winnings)}</b> prizes you have redeemed:\n"
            for i, win in enumerate(winnings, 1):
                body += (
                    f"\n<b>{i}. {escape(win['giveaway_name'])}</b>\n"
                    f"   <pre>{escape(win['prize_text'])}</pre>\n"
                    f"   <pre>Code: {escape(win['code'])}</pre>\n"
                    f"   <pre>Redeemed on: {escape(win['date'])}</pre>"
                )
        footer = "Your personal prize vault."
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}"

    @staticmethod
    def public_stats_message(total_users, total_redeemed, active_giveaways):
        title = f"{UIFactory.EMOJIS['stats']} 𝗟𝗜𝗩𝗘 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦"
        body = (f"Building trust with our community!\n\n"
                f"{UIFactory.EMOJIS['users']} <b>Total Bot Users:</b> {total_users}\n"
                f"{UIFactory.EMOJIS['party']} <b>Total Prizes Redeemed:</b> {total_redeemed}\n"
                f"{UIFactory.EMOJIS['rocket']} <b>Active Giveaways:</b> {active_giveaways}\n\n"
                f"Stay active to be the next winner!")
        footer = f"{UIFactory.EMOJIS['clock']} <b>Live Time:</b> {get_live_time()}"
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}"

    @staticmethod
    def top_winners_message(top_users):
        title = f"{UIFactory.EMOJIS['crown']} 𝗧𝗢𝗣 {len(top_users)} 𝗪𝗜𝗡𝗡𝗘𝗥𝗦 𝗟𝗘𝗔𝗗𝗘𝗥𝗕𝗢𝗔𝗥𝗗"
        if not top_users:
            body = f"{UIFactory.EMOJIS['error']} No winners found yet."
        else:
            body = "Here are our most dedicated winners:\n"
            medals = [f"{UIFactory.EMOJIS['crown']}", '🥈', '🥉', '4.', '5.']
            
            for i, user_data in enumerate(top_users):
                name = escape(user_data.get('first_name', 'User'))
                username = f"(@{escape(user_data.get('username', 'N/A'))})" if user_data.get('username') else ""
                wins = len(user_data.get('winnings', []))
                medal = medals[i] if i < len(medals) else f"{i+1}."
                
                body += (
                    f"\n<b>{medal} {name}</b> {username}\n"
                    f"   <b>Wins:</b> {wins}"
                )
                
        footer = "Keep participating to get on the list!"
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}"

    @staticmethod
    def force_join_message(channel_username, group_username):
        title = f"{UIFactory.EMOJIS['warn']} 𝗠𝗘𝗠𝗕𝗘𝗥𝗦𝗛𝗜𝗣 𝗥𝗘𝗤𝗨𝗜𝗥𝗘𝗗"
        body = (f"To use this bot, you must be a member of our\n"
                f"channel <b>and</b> group.\n\n"
                f"Please join both, then click 'Verify Membership'.")
        footer = "Thank you for your support!"
        
        markup = InlineKeyboardMarkup(row_width=1)
        if channel_username:
            markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['link']} Join Our Channel", url=f"https://t.me/{channel_username.replace('@', '')}"))
        if group_username:
            markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['link']} Join Our Group", url=f"https://t.me/{group_username.replace('@', '')}"))
        
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['check']} Verify Membership", callback_data="user_verify_join"))
        
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}", markup

    @staticmethod
    def error_message(details):
        title = f"{UIFactory.EMOJIS['error']} 𝗔𝗡 𝗘𝗥𝗥𝗢𝗥 𝗢𝗖𝗖𝗨𝗥𝗥𝗘𝗗"
        body = f"<b>Reason:</b> <code>{details}</code>"
        footer = "If this persists, please contact the admin."
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}"
        
    @staticmethod
    def success_message(details):
        title = f"{UIFactory.EMOJIS['success']} 𝗦𝗨𝗖𝗖𝗘𝗦𝗦"
        body = f"{UIFactory.EMOJIS['star']} {details}"
        footer = "Action completed successfully."
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}"

    @staticmethod
    def prompt_message(details):
        title = f"{UIFactory.EMOJIS['warn']} 𝗔𝗖𝗧𝗜𝗢𝗡 𝗥𝗘𝗤𝗨𝗜𝗥𝗘𝗗"
        body = f"💬 {details}"
        footer = "Please reply to this message."
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}"
        
    @staticmethod
    def cancelled_message():
        title = f"{UIFactory.EMOJIS['error']} 𝗔𝗖𝗧𝗜𝗢𝗡 𝗖𝗔𝗡𝗖𝗘𝗟𝗟𝗘𝗗"
        body = f"{UIFactory.EMOJIS['back']} The previous action has been cancelled."
        footer = "No changes were made."
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}"
        
    @staticmethod
    def confirmation_message(action_name, callback_yes, callback_no):
        title = f"{UIFactory.EMOJIS['confirm']} 𝗖𝗢𝗡𝗙𝗜𝗥𝗠 𝗔𝗖𝗧𝗜𝗢𝗡"
        body = (f"Are you sure you want to <b>{escape(action_name)}</b>?\n\n"
                f"<b>This action cannot be undone.</b>")
        footer = "Please confirm your choice."
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(f"{UIFactory.EMOJIS['success']} Yes, Confirm", callback_data=callback_yes),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['error']} No, Cancel", callback_data=callback_no)
        )
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}", markup

    @staticmethod
    def locked_panel_message():
        title = f"{UIFactory.EMOJIS['lock']} 𝗣𝗔𝗡𝗘𝗟 𝗟𝗢𝗖𝗞𝗘D"
        body = (f"The admin panel is currently locked for security.\n\n"
                f"Click the button below to unlock.")
        footer = f"{UIFactory.EMOJIS['clock']} <b>Live Time:</b> {get_live_time()}"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['unlock']} Unlock Panel", callback_data="admin_unlock_panel"))
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}", markup

    @staticmethod
    def generate_giveaway_post(giveaway_name, code_count, codes_list, bot_username, markup=None):
        example_code = "CODE-XXXX-XXXX"
        if codes_list:
            example_code = escape(codes_list[0])
            
        codes_block = "\n".join([f"<code>{escape(code)}</code>" for code in codes_list])

        post = (
            f"🎁 <b>{escape(giveaway_name.upper())} GIVEAWAY</b> 🎁\n\n"
            f"{UIFactory.EMOJIS['star']} We are giving away <b>{code_count}</b> new Redeem Code(s):\n"
            f"{codes_block}\n\n"
            f"🏆 <b>Winner Receives:</b>\n"
            f"  •  <i>{escape(giveaway_name)}</i>\n\n"
            f"{UIFactory.EMOJIS['rocket']} <b>How to Redeem?</b>\n"
            f"  1. Start our official bot below.\n"
            f"  2. Click 'Redeem' and send the code.\n"
            f"  (Example: <code>{example_code}</code>)\n\n" # v22.0: Updated text
            f"👇 <b>REDEEM BOT:</b>\n"
            f"@{bot_username}\n"
            f"@{bot_username}\n\n"
            f"🔺 <b>FIRST {code_count} USERS WILL WIN!</b> 🔺\n"
            f"Hurry Up! {UIFactory.EMOJIS['party']}\n\n"
            f"Bot Powered by @shuvohassan00"
        )
        return post, markup

    # --- Admin Panel Messages ---
    @staticmethod
    def admin_panel_message(is_owner):
        title = f"{UIFactory.EMOJIS['admin']} 𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 𝗖𝗘𝗡𝗧𝗘𝗥 {UIFactory.EMOJIS['admin']}"
        body = "Welcome back, <b>Admin</b>.\nThe Command Center is at your disposal."
        footer = f"{UIFactory.EMOJIS['clock']} <b>Live Time:</b> {get_live_time()}"
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(f"{UIFactory.EMOJIS['gift']} Create Giveaway", callback_data="admin_create_giveaway"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['list']} Manage Giveaways", callback_data="admin_manage_giveaways"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['broadcast']} Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['stats']} Statistics", callback_data="admin_stats"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['users']} User Management", callback_data="admin_user_manage"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['settings']} Bot Settings", callback_data="admin_settings"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['db']} Global Stock", callback_data="admin_global_stock"),
            # v22.0: Admin Search
            InlineKeyboardButton(f"{UIFactory.EMOJIS['search']} Search Stock", callback_data="admin_search_stock")
        )
        if is_owner:
            markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['crown']} Manage Admins", callback_data="admin_manage_admins"))
        
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['lock']} Lock Panel", callback_data="admin_lock_panel"))
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}", markup

    @staticmethod
    def settings_panel_message(settings):
        title = f"{UIFactory.EMOJIS['settings']} 𝗕𝗢𝗧 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦"
        
        channel = escape(settings.get('force_channel') or "Not Set")
        group = escape(settings.get('force_group') or "Not Set")
        fjoin_status_emoji = f"{UIFactory.EMOJIS['success']}" if settings.get('force_join_enabled', False) else f"{UIFactory.EMOJIS['error']}"
        fjoin_status_text = "ON" if settings.get('force_join_enabled', False) else "OFF"
        admin_user = escape(settings.get('admin_username') or "Not Set")
        brand_img = escape(settings.get('welcome_image_url') or "Not Set")
        welcome_img = escape(settings.get('user_welcome_image_url') or "Not Set")
        
        body = (
            f"<b>Force Join:</b> {fjoin_status_emoji} {fjoin_status_text}\n"
            f"<b>Channel:</b> <code>{channel}</code>\n"
            f"<b>Group:</b> <code>{group}</code>\n\n"
            f"<b>Admin User:</b> <code>{admin_user}</code>\n"
            f"<b>Branding Img:</b> <code>{brand_img if len(brand_img) < 30 else brand_img[:30] + '...'}</code>\n"
            f"<b>Welcome Img:</b> <code>{welcome_img if len(welcome_img) < 30 else welcome_img[:30] + '...'}</code>"
        )
        footer = "Manage bot behavior"
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("Set Channel", callback_data="admin_set_channel"),
            InlineKeyboardButton("Set Group", callback_data="admin_set_group"),
            InlineKeyboardButton(f"Toggle Force Join", callback_data="admin_toggle_forcejoin"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['check']} Check Setup", callback_data="admin_check_setup"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['pic']} Set Branding Image", callback_data="admin_set_welcome_image"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['welcome']} Set Welcome Image", callback_data="admin_set_user_welcome_image"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['user']} Set Admin User", callback_data="admin_set_admin_user"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Panel", callback_data="admin_main_panel")
        )
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}", markup

    @staticmethod
    def manage_admins_panel(admin_ids):
        title = f"{UIFactory.EMOJIS['crown']} 𝗠𝗔𝗡𝗔𝗚𝗘 𝗔𝗗𝗠𝗜𝗡𝗦"
        body = (f"Here you can add or remove other admins.\n\n"
                f"<b>To Add:</b> Reply to a user's message with <code>/promote</code>\n"
                f"<b>To Remove:</b> Reply to an admin's message with <code>/demote</code>\n"
                f"You can also add manually below.")
        footer = "Owner-Only Access"
        
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['user']} Add Admin by ID", callback_data="admin_add_admin"))
        if admin_ids:
            body += "\n\n<b>Current Admins:</b>"
            for admin_id in admin_ids:
                markup.add(InlineKeyboardButton(f"🚫 Remove {admin_id}", callback_data=f"admin_confirm_remove_admin_{admin_id}"))
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Panel", callback_data="admin_main_panel"))
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}", markup

    @staticmethod
    def manage_giveaways_panel(giveaways_data):
        title = f"{UIFactory.EMOJIS['list']} 𝗠𝗔𝗡𝗔𝗚𝗘 𝗚𝗜𝗩𝗘𝗔𝗪𝗔𝗬𝗦"
        footer = "Select a giveaway to manage"
        markup = InlineKeyboardMarkup(row_width=1)
        
        if not giveaways_data:
            body = f"{UIFactory.EMOJIS['error']} No giveaways created yet. Use 'Create Giveaway' to start."
        else:
            body = "Select a giveaway to add prizes or manage it:\n"
            for gid, data in giveaways_data.items():
                total = len(data['prizes'])
                redeemed = sum(1 for p in data['prizes'].values() if p['redeemed'])
                remaining = total - redeemed
                markup.add(InlineKeyboardButton(f"{escape(data['name'])} ({remaining} left | {redeemed} redeemed)", callback_data=f"admin_view_giveaway_{gid}"))
        
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Panel", callback_data="admin_main_panel"))
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}", markup

    @staticmethod
    def giveaway_details_panel(gid, gdata):
        title = f"{UIFactory.EMOJIS['gift']} 𝗠𝗔𝗡𝗔𝗚𝗘: {escape(gdata['name'])}"
        total = len(gdata['prizes'])
        redeemed = sum(1 for p in gdata['prizes'].values() if p['redeemed'])
        remaining = total - redeemed
        
        body = (f"<b>Giveaway ID:</b> <code>{gid}</code>\n\n"
                f"{UIFactory.EMOJIS['rocket']} <b>Remaining Stock:</b> {remaining}\n"
                f"{UIFactory.EMOJIS['party']} <b>Total Redeemed:</b> {redeemed}\n"
                f"{UIFactory.EMOJIS['db']} <b>Total Prizes:</b> {total}\n\n"
                f"Use the buttons below to manage this giveaway.")
        footer = "Giveaway Management"
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(f"{UIFactory.EMOJIS['rocket']} Smart Stock", callback_data=f"admin_smart_stock_{gid}"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['pro']} Pro Stock", callback_data=f"admin_pro_stock_{gid}")
        )
        markup.add(
            InlineKeyboardButton(f"{UIFactory.EMOJIS['upload']} Batch Add", callback_data=f"admin_batch_add_prize_{gid}"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['edit']} View/Edit Prizes", callback_data=f"admin_prize_list_{gid}_0")
        )
        markup.add(
            InlineKeyboardButton(f"{UIFactory.EMOJIS['magic']} Generate Smart Post", callback_data=f"admin_generate_smart_post_{gid}")
        )
        markup.add(
            InlineKeyboardButton(f"{UIFactory.EMOJIS['rename']} Edit Name", callback_data=f"admin_edit_giveaway_name_{gid}"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['clone']} Clone Giveaway", callback_data=f"admin_clone_giveaway_{gid}"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['download']} Export Codes", callback_data=f"admin_export_codes_{gid}"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['stats']} Full Report", callback_data=f"admin_export_full_report_{gid}"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['trash']} Delete Giveaway", callback_data=f"admin_confirm_delete_giveaway_{gid}")
        )
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to List", callback_data="admin_manage_giveaways"))
        
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}", markup

    @staticmethod
    def prize_list_panel(gid, gdata, page=0):
        title = f"{UIFactory.EMOJIS['edit']} 𝗘𝗗𝗜𝗧 𝗣𝗥𝗜𝗭𝗘𝗦: {escape(gdata['name'])}"
        footer = "Manage individual prize stock"
        
        prizes = gdata.get('prizes', {})
        if not prizes:
            body = "This giveaway has no prizes."
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Giveaway", callback_data=f"admin_view_giveaway_{gid}"))
            return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}", markup
            
        sorted_prizes = sorted(prizes.items(), key=lambda item: item[1]['redeemed'])
        
        start_index = page * PRIZES_PER_PAGE
        end_index = start_index + PRIZES_PER_PAGE
        prizes_on_page = sorted_prizes[start_index:end_index]
        total_pages = math.ceil(len(sorted_prizes) / PRIZES_PER_PAGE)

        markup = InlineKeyboardMarkup(row_width=2)
        body = f"Page {page + 1} of {total_pages}. Showing {len(prizes_on_page)} of {len(sorted_prizes)} prizes.\n"
        
        if not prizes_on_page:
                body = "No prizes on this page."
        
        for code, prize_data in prizes_on_page:
            prize_text_escaped = escape(prize_data['prize_text'])
            code_escaped = escape(code)
            
            body += f"\n{UIFactory.DIVIDER}\n"
            if prize_data['redeemed']:
                username_escaped = escape(prize_data.get('redeemed_by_username', 'N/A'))
                body += (
                    f"<s>{code_escaped}</s>\n"
                    f"<i>{UIFactory.EMOJIS['user']} Redeemed by @{username_escaped}</i>\n"
                    f"{UIFactory.EMOJIS['gift']} <pre>{prize_text_escaped}</pre>"
                )
            else:
                body += (
                    f"<b>{code_escaped}</b>\n"
                    f"{UIFactory.EMOJIS['gift']} Prize: <pre>{prize_text_escaped}</pre>"
                )
                markup.add(
                    InlineKeyboardButton(f"{UIFactory.EMOJIS['edit']} Edit", callback_data=f"admin_edit_prize_text_{gid}_{code}"),
                    InlineKeyboardButton(f"{UIFactory.EMOJIS['trash']} Delete", callback_data=f"admin_confirm_delete_prize_{gid}_{code}_{page}")
                )

        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("« Prev", callback_data=f"admin_prize_list_{gid}_{page - 1}"))
        
        nav_row.append(InlineKeyboardButton(f"Page {page + 1}/{total_pages}", callback_data="admin_noop"))
        
        if end_index < len(sorted_prizes):
            nav_row.append(InlineKeyboardButton("Next »", callback_data=f"admin_prize_list_{gid}_{page + 1}"))
        
        if nav_row:
            markup.add(*nav_row)
            
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Giveaway", callback_data=f"admin_view_giveaway_{gid}"))
        return f"<b>{title}</b>\n{body}\n{UIFactory.DIVIDER}\n{footer}", markup

    @staticmethod
    def user_manage_panel(user_id, user_data, is_banned):
        if not user_data:
            title = f"{UIFactory.EMOJIS['error']} 𝗨𝗦𝗘𝗥 𝗡𝗢𝗧 𝗙𝗢𝗨𝗡𝗗"
            body = f"No user found with ID or Username: <code>{escape(user_id)}</code>\nThey must /start the bot first."
            footer = "User Management"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Panel", callback_data="admin_main_panel"))
            return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}", markup

        name = escape(user_data.get('first_name', 'N/A'))
        username = escape(user_data.get('username', 'N/A'))
        wins = len(user_data.get('winnings', []))
        status = "BANNED" if is_banned else "Active"
        
        joined_at_str = "Unknown"
        if user_data.get('joined_at'):
            try:
                joined_at_str = datetime.fromisoformat(user_data['joined_at']).strftime("%d-%b-%Y")
            except:
                pass
        
        user_id_from_data = user_data.get('user_id') 
        
        title = f"{UIFactory.EMOJIS['users']} 𝗠𝗔𝗡𝗔𝗚𝗘 𝗨𝗦𝗘𝗥: {name}"
        body = (f"<b>User ID:</b> <code>{user_id_from_data}</code>\n"
                f"<b>Username:</b> @{username}\n"
                f"<b>Total Wins:</b> {wins}\n"
                f"<b>Joined On:</b> {joined_at_str}\n"
                f"<b>Status:</b> <b>{status}</b>")
        footer = "User Management"
        
        markup = InlineKeyboardMarkup(row_width=1)
        # v22.0: Add View Winnings button
        if wins > 0:
            markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['gift']} View User Winnings ({wins})", callback_data=f"admin_view_user_winnings_{user_id_from_data}"))
            
        if is_banned:
            markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['unban']} Unban User", callback_data=f"admin_unban_user_{user_id_from_data}"))
        else:
            markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['ban']} Ban User", callback_data=f"admin_confirm_ban_user_{user_id_from_data}"))
            
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Panel", callback_data="admin_main_panel"))
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}", markup
    
    # v22.0: New UI for User Winnings Report
    @staticmethod
    def user_winnings_report(user_data, winnings):
        name = escape(user_data.get('first_name', 'N/A'))
        title = f"{UIFactory.EMOJIS['gift']} 𝗪𝗜𝗡𝗡𝗜𝗡𝗚𝗦 𝗥𝗘𝗣𝗢𝗥𝗧: {name}"
        
        if not winnings:
            body = f"{UIFactory.EMOJIS['error']} This user has not won any prizes."
        else:
            body = f"This user has redeemed <b>{len(winnings)}</b> prizes:\n"
            for i, win in enumerate(winnings, 1):
                body += (
                    f"\n<b>{i}. {escape(win['giveaway_name'])}</b>\n"
                    f"   <pre>{escape(win['prize_text'])}</pre>\n"
                    f"   <pre>Code: {escape(win['code'])}</pre>\n"
                    f"   <pre>Date: {escape(win['date'])}</pre>"
                )
        footer = f"Report for User ID: {user_data.get('user_id')}"
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}"

    @staticmethod
    def stock_success_message(name, prize_text, new_code):
        title = f"{UIFactory.EMOJIS['success']} 𝗣𝗥𝗜𝗭𝗘 𝗦𝗧𝗢𝗖𝗞𝗘D!"
        body = (f"Successfully added 1 new prize to:\n"
                f"<b>{escape(name)}</b>\n\n"
                f"<b>Prize Text:</b>\n"
                f"<pre>{escape(prize_text)}</pre>\n\n"
                f"<b>{UIFactory.EMOJIS['ticket']} Redeem Code:</b>\n"
                f"<code>{escape(new_code)}</code>\n\n"
                f"⬆️ You can now post this code in your channel.")
        footer = "Admin Notification"
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}"
        
    @staticmethod
    def stock_multi_success_message(name, count):
        title = f"{UIFactory.EMOJIS['success']} 𝗕𝗔𝗧𝗖𝗛 𝗦𝗧𝗢𝗖𝗞 𝗦𝗨𝗖𝗖𝗘𝗦𝗦!"
        body = (f"Successfully stocked <b>{count}</b> new prizes\n"
                f"from the .txt file for '<b>{escape(name)}</b>'.\n\n"
                f"Use 'View/Edit Prizes' or 'Generate Post' to see\n"
                f"the new auto-generated codes.")
        footer = "Admin Notification"
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}"

    @staticmethod
    def stats_message(total_users, total_giveaways, total_prizes, total_redeemed, remaining_prizes, top_giveaways):
        title = f"{UIFactory.EMOJIS['stats']} 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦"
        body = (f"<b>{UIFactory.EMOJIS['users']} Total Bot Users:</b> {total_users}\n"
                f"<b>{UIFactory.EMOJIS['list']} Total Giveaways Created:</b> {total_giveaways}\n\n"
                f"<b>{UIFactory.EMOJIS['gift']} Total Prizes Stocked:</b> {total_prizes}\n"
                f"<b>{UIFactory.EMOJIS['party']} Total Prizes Redeemed:</b> {total_redeemed}\n"
                f"<b>{UIFactory.EMOJIS['rocket']} Prizes Remaining:</b> {remaining_prizes}")
        
        # v22.0: Enhanced Stats
        if top_giveaways:
            body += f"\n\n<b>{UIFactory.EMOJIS['trophy']} Top {len(top_giveaways)} Most Redeemed:</b>\n"
            for i, g in enumerate(top_giveaways, 1):
                body += f"{i}. <b>{escape(g['name'])}</b> ({g['redeemed']} redeemed)\n"
        
        footer = f"{UIFactory.EMOJIS['clock']} <b>Live Time:</b> {get_live_time()}"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Panel", callback_data="admin_main_panel"))
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}", markup
    
    # v22.0: New UI for Search Results
    @staticmethod
    def search_results_message(search_term, results):
        title = f"{UIFactory.EMOJIS['search']} 𝗦𝗘𝗔𝗥𝗖𝗛 𝗥𝗘𝗦𝗨𝗟𝗧𝗦"
        
        if not results:
            body = f"{UIFactory.EMOJIS['error']} No unredeemed prizes found matching: <code>{escape(search_term)}</code>"
            footer = "Try a different search term."
        else:
            body = f"Found <b>{len(results)}</b> unredeemed prizes for: <code>{escape(search_term)}</code>\n"
            current_gname = ""
            for item in results:
                gname = item['gname']
                if gname != current_gname:
                    body += f"\n<b>{UIFactory.EMOJIS['gift']} {escape(gname)}</b>\n"
                    current_gname = gname
                
                body += (
                    f"   - <code>{escape(item['code'])}</code>\n"
                    f"     <pre>{escape(item['prize'])}</pre>"
                )
            footer = "Search completed successfully."

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Panel", callback_data="admin_main_panel"))
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}", markup

    @staticmethod
    def global_stock_message(global_stock_list):
        title = f"{UIFactory.EMOJIS['db']} 𝗚𝗟𝗢𝗕𝗔𝗟 𝗦𝗧𝗢𝗖𝗞 𝗥𝗘𝗣𝗢𝗥𝗧"
        
        if not global_stock_list:
            body = f"{UIFactory.EMOJIS['success']} All prizes have been redeemed! Stock is empty."
            footer = "Great job!"
        else:
            body = f"Here are all <b>{len(global_stock_list)}</b> unredeemed prizes in the bot:\n"
            current_gname = ""
            for item in global_stock_list:
                gname = item['gname']
                if gname != current_gname:
                    body += f"\n<b>{UIFactory.EMOJIS['gift']} {escape(gname)}</b>\n"
                    current_gname = gname
                
                body += (
                    f"   - <code>{escape(item['code'])}</code>\n"
                    f"     <pre>{escape(item['prize'])}</pre>"
                )
            footer = "Report generated successfully."

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Panel", callback_data="admin_main_panel"))
        return f"<b>{title}</b>\n{UIFactory.DIVIDER}\n{body}\n{UIFactory.DIVIDER}\n{footer}", markup

# -----------------------------------------------------------------------------------
# 💾 --- DATABASE MANAGEMENT (v22.0) --- 💾
# -----------------------------------------------------------------------------------

def load_data():
    """Thread-safe function to load the JSON database file."""
    with data_lock:
        defaults = {
            "settings": {
                "force_channel": None, "force_group": None,
                "force_join_enabled": False,
                "welcome_image_url": None,
                "user_welcome_image_url": None,
                "admin_username": None, "admin_ids": [],
                "banned_users": [],
            },
            "giveaways": {},
            "users": {}
        }
        
        if not os.path.exists(DATA_FILE):
            print(f"Database file not found. Creating new one: {DATA_FILE}")
            return defaults
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            settings_data = data.get("settings", defaults["settings"])
            
            for key, value in defaults["settings"].items():
                if key not in settings_data:
                    settings_data[key] = value
            
            obsolete_keys = ["welcome_gift_enabled", "welcome_gift_name", "welcome_gift_prize"]
            keys_to_remove = [k for k in settings_data if k in obsolete_keys]
            
            if keys_to_remove:
                print(f"Removing obsolete settings: {keys_to_remove}")
                for key in keys_to_remove:
                    del settings_data[key]
                    
            data["settings"] = settings_data
            if "giveaways" not in data: data["giveaways"] = defaults["giveaways"]
            if "users" not in data: data["users"] = defaults["users"]
            
            return data
            
        except json.JSONDecodeError:
            print(f"!!! CRITICAL: JSONDecodeError reading {DATA_FILE}. Loading defaults. !!!")
            return defaults
        except Exception as e:
            print(f"!!! CRITICAL: Error reading {DATA_FILE}: {e}. Loading defaults. !!!")
            return defaults

def save_data(data):
    """Thread-safe function to save the JSON database file."""
    with data_lock:
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"!!! CRITICAL: Failed to save data to {DATA_FILE}: {e} !!!")

# -----------------------------------------------------------------------------------
# 🛠️ --- HELPER FUNCTIONS (v22.0) --- 🛠️
# -----------------------------------------------------------------------------------

def is_owner(user_id):
    return user_id == OWNER_ID

def is_admin(user_id):
    if user_id == OWNER_ID:
        return True
    data = load_data()
    return user_id in data["settings"].get("admin_ids", [])

def is_banned(user_id):
    if is_admin(user_id):
        return False
    data = load_data()
    return user_id in data["settings"].get("banned_users", [])

def create_prefix(name):
    prefix_raw = name.split(' ')[0]
    prefix_clean = re.sub(r'[^A-Z0-9]', '', prefix_raw.upper())
    prefix_limited = prefix_clean[:8]
    if not prefix_limited:
        return "GIFT"
    return prefix_limited

def generate_code(giveaway_name):
    prefix = create_prefix(giveaway_name)
    random_part_1 = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=4))
    random_part_2 = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=4))
    return f"{prefix}-{random_part_1}-{random_part_2}"

def is_code_unique(code_to_check, data):
    code_upper = code_to_check.upper()
    for gdata in data['giveaways'].values():
        if code_upper in gdata['prizes']:
            return False
    return True

def register_user(user):
    data = load_data()
    user_id_str = str(user.id)
    user_data = data["users"].get(user_id_str)
    
    needs_save = False
    
    if not user_data:
        data["users"][user_id_str] = {
            "user_id": user.id, 
            "username": user.username,
            "first_name": user.first_name,
            "winnings": [],
            "joined_at": datetime.now(BOT_TIMEZONE).isoformat()
        }
        needs_save = True
    
    elif (user_data.get("username") != user.username or
          user_data.get("first_name") != user.first_name or
          "user_id" not in user_data): 
        
        user_data["username"] = user.username
        user_data["first_name"] = user.first_name
        user_data["user_id"] = user.id 
        if "joined_at" not in user_data:
            user_data["joined_at"] = datetime.now(BOT_TIMEZONE).isoformat()
        needs_save = True
        
    if needs_save:
        save_data(data)
        
    return

def check_membership(user_id):
    if is_admin(user_id):
        return True
        
    data = load_data()
    settings = data["settings"]
    
    if not settings["force_join_enabled"]:
        return True
        
    channel_ok = True
    group_ok = True

    if settings["force_channel"]:
        try:
            member = bot.get_chat_member(chat_id=settings["force_channel"], user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                channel_ok = False
        except Exception as e:
            print(f"Error checking channel {settings['force_channel']}: {e}")
            channel_ok = False

    if settings["force_group"]:
        try:
            member = bot.get_chat_member(chat_id=settings["force_group"], user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                group_ok = False
        except Exception as e:
            print(f"Error checking group {settings['force_group']}: {e}")
            group_ok = False

    return channel_ok and group_ok

def send_branded_message(chat_id, text, reply_markup=None, is_reply=False, reply_to_id=None, image_url=None):
    if image_url is None:
        data = load_data()
        image_url = data["settings"].get("welcome_image_url")
    
    try:
        if image_url and image_url.upper() != 'NONE':
            if is_reply:
                bot.send_photo(chat_id, image_url, caption=text, reply_to_message_id=reply_to_id, reply_markup=reply_markup)
            else:
                bot.send_photo(chat_id, image_url, caption=text, reply_markup=reply_markup)
        else:
            if is_reply:
                bot.send_message(chat_id, text, reply_to_message_id=reply_to_id, reply_markup=reply_markup)
            else:
                bot.send_message(chat_id, text, reply_markup=reply_markup)
    except Exception as e:
        print(f"send_branded_message error (falling back to text): {e}")
        try:
            if is_reply:
                bot.send_message(chat_id, text, reply_to_message_id=reply_to_id, reply_markup=reply_markup)
            else:
                bot.send_message(chat_id, text, reply_markup=reply_markup)
        except Exception as e2:
            print(f"Fallback send_message also failed: {e2}")
            
# v21.0: New helper to get all stats at once
def get_live_stats():
    """
    v21.0: Fetches all key stats in one go for the Dynamic UI.
    """
    data = load_data()
    total_users = len(data.get('users', {}))
    total_redeemed = 0
    active_giveaways = 0
    
    for gdata in data.get('giveaways', {}).values():
        redeemed_count = sum(1 for p in gdata.get('prizes', {}).values() if p.get('redeemed'))
        total_redeemed += redeemed_count
        if len(gdata.get('prizes', {})) > redeemed_count:
            active_giveaways += 1
            
    return {
        "users": total_users,
        "redeemed": total_redeemed,
        "active": active_giveaways
    }

# v22.0: New helper for the interactive redeem flow
def process_redeem_attempt(user, redeem_code):
    """
    v22.0: Core logic for redeeming a code.
    Returns (status_code, message_text, success_data)
    status_code 0: Error
    status_code 1: Success
    """
    if not redeem_code:
        return (0, UIFactory.error_message("Please provide a gift code."))

    data = load_data()
    
    found_code = False
    for giveaway_id, giveaway_data in data.get('giveaways', {}).items():
        if redeem_code in giveaway_data.get('prizes', {}):
            found_code = True
            prize_data = giveaway_data["prizes"][redeem_code]
            
            if prize_data.get("redeemed", False):
                return (0, UIFactory.error_message(f"This gift code has already been redeemed by @{escape(prize_data.get('redeemed_by_username', 'N/A'))}!"))

            redeemed_at_time = datetime.now(BOT_TIMEZONE)
            
            prize_data["redeemed"] = True
            prize_data["redeemed_by_user_id"] = user.id
            prize_data["redeemed_by_username"] = user.username or user.first_name
            prize_data["redeemed_at"] = redeemed_at_time.isoformat()
            
            prize_name = giveaway_data["name"]
            prize_text = prize_data["prize_text"]
            
            win_record = {
                "giveaway_name": prize_name,
                "prize_text": prize_text,
                "code": redeem_code,
                "date": redeemed_at_time.strftime("%d-%b-%Y at %I:%M %p %Z")
            }
            
            user_id_str = str(user.id)
            if user_id_str not in data["users"]: 
                register_user(user)
                data = load_data()
            
            data["users"][user_id_str]["winnings"].append(win_record)
            
            save_data(data)
            
            admin_username = data["settings"].get("admin_username", "the Admin")
            success_text = UIFactory.redeem_success_message(user.first_name, prize_name, prize_text, admin_username, redeem_code)
            return (1, success_text)
            
    if not found_code:
        return (0, UIFactory.error_message("Invalid or expired gift code. Please check the code and try again."))

# -----------------------------------------------------------------------------------
# 🤖 --- USER COMMAND HANDLERS (v22.0 - Threaded) --- 🤖
# -----------------------------------------------------------------------------------

@bot.message_handler(commands=['start'])
def start_command(message):
    process_threaded(handle_start, message)

def handle_start(message):
    try:
        user = message.from_user
        
        if is_banned(user.id):
            bot.reply_to(message, f"🚫 You have been banned from using this bot.")
            return
        
        register_user(user)
        
        data = load_data()
        settings = data["settings"]
        
        if is_admin(user.id):
            panel_text, panel_markup = UIFactory.admin_panel_message(is_owner(user.id))
            send_branded_message(message.chat.id, panel_text, reply_markup=panel_markup)
        else:
            if not check_membership(user.id):
                channel = settings.get("force_channel")
                group = settings.get("force_group")
                error_text, error_markup = UIFactory.force_join_message(channel, group)
                bot.reply_to(message, error_text, reply_markup=error_markup)
                return
            
            stats = get_live_stats()
            welcome_text, welcome_markup = UIFactory.welcome_message(message.from_user, stats)
            user_welcome_image = settings.get("user_welcome_image_url")
            
            send_branded_message(message.chat.id, welcome_text, reply_markup=welcome_markup, image_url="USER_WELCOME")
    except Exception as e:
        print(f"Error in handle_start: {e}")

@bot.message_handler(commands=['redeem'])
def redeem_command(message):
    process_threaded(handle_redeem_command, message)

def handle_redeem_command(message):
    """
    v22.0: This is now just a fallback for manual typing.
    The main flow is handle_user_input's 'user_redeem_code'.
    """
    try:
        user = message.from_user
        chat_id = message.chat.id

        if is_banned(user.id):
            bot.reply_to(message, f"🚫 You are banned and cannot redeem codes.")
            return
        
        register_user(user)
        
        if not check_membership(user.id):
            data = load_data()
            channel = data["settings"].get("force_channel")
            group = data["settings"].get("force_group")
            error_text, error_markup = UIFactory.force_join_message(channel, group)
            bot.reply_to(message, error_text, reply_markup=error_markup)
            return
        
        try:
            redeem_code = message.text.split(' ', 1)[1].strip().upper()
        except IndexError:
            error_text = UIFactory.error_message("Please provide a gift code.\nExample: <code>/redeem CODE-XXXX-XXXX</code>")
            bot.reply_to(message, error_text)
            return

        # Use the new core logic
        status, message_text = process_redeem_attempt(user, redeem_code)
        
        if status == 1: # Success
            send_branded_message(chat_id, message_text)
        else: # Error
            bot.reply_to(message, message_text)
            
    except Exception as e:
        print(f"Error in handle_redeem_command: {e}")

@bot.message_handler(commands=['mywinnings'])
def my_winnings_command(message):
    process_threaded(handle_my_winnings, message)

def handle_my_winnings(message):
    try:
        user = message.from_user

        if is_banned(user.id):
            bot.reply_to(message, f"🚫 You are banned from using this bot.")
            return
        
        register_user(user)
        
        if not check_membership(user.id):
            data = load_data()
            channel = data["settings"].get("force_channel")
            group = data["settings"].get("force_group")
            error_text, error_markup = UIFactory.force_join_message(channel, group)
            bot.reply_to(message, error_text, reply_markup=error_markup)
            return

        data = load_data()
        winnings = data["users"][str(user.id)]["winnings"]
        
        winnings_text = UIFactory.my_winnings_message(user.first_name, winnings)
        send_branded_message(message.chat.id, winnings_text)
    except Exception as e:
        print(f"Error in handle_my_winnings: {e}")

# -----------------------------------------------------------------------------------
# 💎 --- ADMIN/OWNER: GODMODE COMMANDS (v22.0 - Threaded) --- 💎
# -----------------------------------------------------------------------------------
@bot.message_handler(commands=['promote'])
def owner_promote_command(message):
    process_threaded(handle_promote, message)

def handle_promote(message):
    try:
        if not is_owner(message.from_user.id):
            return

        if not message.reply_to_message:
            bot.reply_to(message, "<b>Owner Command:</b> Reply to a user's message with <code>/promote</code> to make them an admin.")
            return
            
        new_admin_user = message.reply_to_message.from_user
        new_admin_id = new_admin_user.id
        new_admin_name = escape(new_admin_user.first_name)
        
        if new_admin_id == OWNER_ID:
            bot.reply_to(message, "You are already the Owner.")
            return
        
        data = load_data()
        admin_ids = data["settings"]["admin_ids"]
        if new_admin_id in admin_ids:
            bot.reply_to(message, f"User {new_admin_name} (<code>{new_admin_id}</code>) is already an admin.")
            return
            
        admin_ids.append(new_admin_id)
        save_data(data)
        bot.reply_to(message, f"✅ Success! User <b>{new_admin_name}</b> (<code>{new_admin_id}</code>) has been promoted to Admin.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {escape(e)}")

@bot.message_handler(commands=['demote'])
def owner_demote_command(message):
    process_threaded(handle_demote, message)

def handle_demote(message):
    try:
        if not is_owner(message.from_user.id):
            return

        if not message.reply_to_message:
            bot.reply_to(message, "<b>Owner Command:</b> Reply to an admin's message with <code>/demote</code> to remove them.")
            return
            
        admin_to_remove_user = message.reply_to_message.from_user
        admin_to_remove_id = admin_to_remove_user.id
        admin_to_remove_name = escape(admin_to_remove_user.first_name)

        data = load_data()
        admin_ids = data["settings"]["admin_ids"]
        
        if admin_to_remove_id not in admin_ids:
            bot.reply_to(message, f"User {admin_to_remove_name} (<code>{admin_to_remove_id}</code>) is not an admin.")
            return
            
        admin_ids.remove(admin_to_remove_id)
        save_data(data)
        bot.reply_to(message, f"✅ Success! User <b>{admin_to_remove_name}</b> (<code>{admin_to_remove_id}</code>) has been demoted.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {escape(e)}")

@bot.message_handler(commands=['userinfo'])
def userinfo_command(message):
    process_threaded(handle_userinfo, message)

def handle_userinfo(message):
    try:
        admin_id = message.from_user.id
        if not is_admin(admin_id):
            return

        if not message.reply_to_message or not message.reply_to_message.forward_from:
            bot.reply_to(message, f"<b>{UIFactory.EMOJIS['magic']} Quantum User Management</b>\n\nTo use this command, forward a message from any user and reply to that forwarded message with <code>/userinfo</code>.")
            return
            
        user_to_manage = message.reply_to_message.forward_from
        user_id_to_manage = user_to_manage.id
        
        if (is_admin(user_id_to_manage) or is_owner(user_id_to_manage)) and not is_owner(admin_id):
            bot.reply_to(message, UIFactory.error_message("Access Denied! You cannot manage another Admin or the Owner."))
            return
            
        data = load_data()
        user_data = data.get("users", {}).get(str(user_id_to_manage))
        
        if not user_data:
            register_user(user_to_manage)
            data = load_data() 
            user_data = data.get("users", {}).get(str(user_id_to_manage))
            
        is_banned = user_id_to_manage in data["settings"].get("banned_users", [])
        
        panel_text, panel_markup = UIFactory.user_manage_panel(user_id_to_manage, user_data, is_banned)
        send_branded_message(message.chat.id, panel_text, reply_markup=panel_markup)

    except Exception as e:
        bot.reply_to(message, UIFactory.error_message(f"An error occurred: {escape(e)}"))
        print(f"Error in handle_userinfo: {e}")


# -----------------------------------------------------------------------------------
# ✨ --- INLINE SHARING HANDLER (v20.0 - Threaded) --- ✨
# -----------------------------------------------------------------------------------
@bot.inline_handler(lambda query: True)
def inline_query_handler(query):
    process_threaded(handle_inline_query, query)

def handle_inline_query(query):
    try:
        user_id = query.from_user.id
        if not is_admin(user_id):
            bot.answer_inline_query(query.id, [], cache_time=1,
                                    switch_pm_text="Only admins can use inline sharing.",
                                    switch_pm_parameter="inline_denied")
            return
            
        data = load_data()
        bot_username = bot.get_me().username
        results = []
        
        default_thumb_url = "https://i.imgur.com/gJ6nL6X.png"  

        for gid, gdata in data.get('giveaways', {}).items():
            total = len(gdata.get('prizes', {}))
            redeemed = sum(1 for p in gdata.get('prizes', {}).values() if p.get('redeemed'))
            remaining = total - redeemed

            if remaining > 0:
                giveaway_name = gdata.get("name", "Giveaway")
                
                message_content = (
                    f"🎁 <b>{escape(giveaway_name.upper())} GIVEAWAY!</b> 🎁\n\n"
                    f"🏆 We are giving away <b>{escape(giveaway_name)}</b>!\n"
                    f"There are <b>{remaining}</b> prizes left!\n\n"
                    f"👇 <b>Redeem From Our Bot:</b>\n"
                    f"@{bot_username} 👈\n\n"
                    f"Good luck! 🎉"
                )
                
                article = InlineQueryResultArticle(
                    id=gid,
                    title=f"🎁 {escape(giveaway_name)}",
                    description=f"{remaining} prizes remaining. Click to share!",
                    input_message_content=InputTextMessageContent(message_content, parse_mode='HTML'),
                    thumb_url=default_thumb_url
                )
                results.append(article)

        if not results:
            article = InlineQueryResultArticle(
                id="none",
                title="No Active Giveaways",
                description="Create a new giveaway to share it.",
                input_message_content=InputTextMessageContent(f"There are no active giveaways right now. Check back later! @{bot_username}")
            )
            results.append(article)
            
        bot.answer_inline_query(query.id, results, cache_time=10)

    except Exception as e:
        print(f"Inline query error: {e}")

# -----------------------------------------------------------------------------------
# 👤 --- USER: BUTTON HANDLERS (v22.0 - Threaded) --- 👤
# -----------------------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith('user_'))
def user_callback_handler(call):
    bot.answer_callback_query(call.id, text="⏳ Loading...")
    process_threaded(handle_user_callback, call)

def handle_user_callback(call):
    try:
        user = call.from_user
        action = call.data
        chat_id = call.message.chat.id

        if is_banned(user.id):
            bot.answer_callback_query(call.id, "🚫 You are banned from using this bot.", show_alert=True)
            return
        
        pre_check_needed = action not in ["user_verify_join", "user_main_menu", "user_redeem_start"]
        
        if pre_check_needed:
            if not check_membership(user.id):
                bot.answer_callback_query(call.id, "Please join our Channel and Group first!", show_alert=True)
                data = load_data()
                channel = data["settings"].get("force_channel")
                group = data["settings"].get("force_group")
                error_text, error_markup = UIFactory.force_join_message(channel, group)
                try:
                    bot.send_message(chat_id, error_text, reply_markup=error_markup)
                except Exception as e:
                    print(f"Error sending force join message: {e}")
                return
        
        # --- Handle Actions ---
        
        if action == "user_main_menu":
            data = load_data()
            settings = data["settings"]
            stats = get_live_stats()
            welcome_text, welcome_markup = UIFactory.welcome_message(user, stats)
            edit_panel_message(call, welcome_text, welcome_markup, "USER_WELCOME")
            return 
        
        # v22.0: Interactive Redeem Start
        elif action == "user_redeem_start":
            if not check_membership(user.id): # Check membership HERE
                bot.answer_callback_query(call.id, "Please join our Channel and Group first!", show_alert=True)
                return
            prompt_text = UIFactory.redeem_prompt_message()
            bot.send_message(chat_id, prompt_text)
            user_task_queue[chat_id] = "user_redeem_code"
        
        elif action == "user_my_winnings":
            data = load_data()
            winnings = data["users"][str(user.id)]["winnings"]
            winnings_text = UIFactory.my_winnings_message(user.first_name, winnings)
            send_branded_message(chat_id, winnings_text)
            
        elif action == "user_public_stats":
            stats = get_live_stats()
            stats_text = UIFactory.public_stats_message(stats['users'], stats['redeemed'], stats['active'])
            bot.send_message(chat_id, stats_text)
            
        elif action == "user_top_winners":
            data = load_data()
            all_users = list(data.get('users', {}).values())
            winners = [user for user in all_users if user.get('winnings')]
            sorted_users = sorted(winners, key=lambda u: len(u.get('winnings', [])), reverse=True)
            top_users = sorted_users[:LEADERBOARD_COUNT]
            leaderboard_text = UIFactory.top_winners_message(top_users)
            bot.send_message(chat_id, leaderboard_text)
        
        elif action == "user_verify_join":
            if check_membership(user.id):
                data = load_data()
                settings = data["settings"]
                stats = get_live_stats()
                welcome_text, welcome_markup = UIFactory.welcome_message(user, stats)
                edit_panel_message(call, welcome_text, welcome_markup, "USER_WELCOME")
            else:
                bot.answer_callback_query(call.id, "🚫 You have not joined yet. Please join both and try again.", show_alert=True)
            
    except Exception as e:
        print(f"User Callback Error: {e}")
        try:
            bot.answer_callback_query(call.id, "An error occurred.")
        except: pass

# -----------------------------------------------------------------------------------
# 🛡️ --- ADMIN: SMART EDIT HELPER (v22.0) --- 🛡️
# -----------------------------------------------------------------------------------

def edit_panel_message(call, new_text, new_markup, image_mode=None):
    """
    v22.0: Smartly edits a panel message.
    image_mode=None: Admin default image
    image_mode="USER_WELCOME": User welcome image
    """
    try:
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        is_currently_photo = call.message.content_type == 'photo'

        data = load_data()
        new_image_url = None
        if image_mode == "USER_WELCOME":
            new_image_url = data["settings"].get("user_welcome_image_url")
        else: # Admin panels
            new_image_url = data["settings"].get("welcome_image_url")
            
        is_target_photo = new_image_url and new_image_url.upper() != 'NONE'

        if is_currently_photo == is_target_photo:
            # No type change, just edit
            if is_target_photo:
                bot.edit_message_caption(caption=new_text, chat_id=chat_id, message_id=message_id, reply_markup=new_markup)
            else:
                bot.edit_message_text(text=new_text, chat_id=chat_id, message_id=message_id, reply_markup=new_markup)
        else:
            # Type change required, delete and send new
            bot.delete_message(chat_id, message_id)
            if is_target_photo:
                bot.send_photo(chat_id, new_image_url, caption=new_text, reply_markup=new_markup)
            else:
                bot.send_message(chat_id, new_text, reply_markup=new_markup)
                
    except Exception as e:
        if "message is not modified" in str(e):
            pass 
        elif "message to edit not found" in str(e) or "message can't be edited" in str(e):
            try:
                print("Fallback: Sending new panel message.")
                send_branded_message(call.message.chat.id, new_text, reply_markup=new_markup, image_url=new_image_url)
            except Exception as e2:
                print(f"Fallback send_branded_message failed: {e2}")
        else:
            print(f"Error in edit_panel_message: {e}")

# -----------------------------------------------------------------------------------
# 🛡️ --- ADMIN: PANEL & BUTTON HANDLERS (v22.0 - Threaded) --- 🛡️
# -----------------------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def admin_callback_handler(call):
    bot.answer_callback_query(call.id, text="⏳ Processing...")
    process_threaded(handle_admin_callback, call)

def handle_admin_callback(call):
    try:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "🚫 Access Denied.", show_alert=True)
            return

        action = call.data
        chat_id = call.message.chat.id
        user_id = call.from_user.id

        def send_premium_prompt(text):
            prompt_text = UIFactory.prompt_message(f"{text}<pre>\n\nOr send /cancel to abort.</pre>")
            bot.send_message(chat_id, prompt_text)

        if action == "admin_noop":
            return

        # --- Main Panel & Lock ---
        if action == "admin_main_panel":
            panel_text, panel_markup = UIFactory.admin_panel_message(is_owner(user_id))
            edit_panel_message(call, panel_text, panel_markup)

        elif action == "admin_lock_panel":
            panel_text, panel_markup = UIFactory.locked_panel_message()
            edit_panel_message(call, panel_text, panel_markup)

        elif action == "admin_unlock_panel":
            panel_text, panel_markup = UIFactory.admin_panel_message(is_owner(user_id))
            edit_panel_message(call, panel_text, panel_markup)

        # --- Settings Panel ---
        elif action == "admin_settings":
            data = load_data()
            settings_text, settings_markup = UIFactory.settings_panel_message(data["settings"])
            edit_panel_message(call, settings_text, settings_markup)
        
        elif action == "admin_set_channel":
            send_premium_prompt("Please send the channel username (e.g., @YourChannelName).")
            admin_task_queue[chat_id] = "set_channel_name"
            
        elif action == "admin_set_group":
            send_premium_prompt("Please send the group username (e.g., @YourGroupName).")
            admin_task_queue[chat_id] = "set_group_name"
            
        elif action == "admin_set_admin_user":
            send_premium_prompt("Please send your admin username (e.g., @shuvohassan00).\nThis will be shown to winners.")
            admin_task_queue[chat_id] = "set_admin_user"
            
        elif action == "admin_set_welcome_image":
            send_premium_prompt("Please send a direct URL for the <b>Branding Image</b>.\nThis image will be used on all admin panels and bot replies.\nSend 'NONE' to remove the image.")
            admin_task_queue[chat_id] = "set_welcome_image"

        elif action == "admin_set_user_welcome_image":
            send_premium_prompt("Please send a direct URL for the <b>User Welcome Image</b>.\nThis will be shown *only* to users on the /start command.\nSend 'NONE' to remove the image.")
            admin_task_queue[chat_id] = "set_user_welcome_image"

        elif action == "admin_toggle_forcejoin":
            data = load_data()
            settings = data["settings"]
            if not settings["force_channel"] or not settings["force_group"]:
                bot.answer_callback_query(call.id, "Error: Please set BOTH channel and group first!", show_alert=True)
                return
            
            settings["force_join_enabled"] = not settings["force_join_enabled"]
            save_data(data)
            
            settings_text, settings_markup = UIFactory.settings_panel_message(settings)
            edit_panel_message(call, settings_text, settings_markup)
            status = "ON" if settings['force_join_enabled'] else "OFF"
            bot.answer_callback_query(call.id, f"Force Join turned {status}.")
            
        elif action == "admin_check_setup":
            data = load_data()
            settings = data["settings"]
            
            channel = settings.get("force_channel")
            group = settings.get("force_group")
            
            if not channel or not group:
                bot.send_message(chat_id, UIFactory.error_message("Please set both Channel and Group usernames first."))
                return

            report = f"<b>{UIFactory.EMOJIS['check']} Setup Check Report (v22.0)</b>\n{UIFactory.DIVIDER}\n"
            
            try:
                bot_member_channel = bot.get_chat_member(chat_id=channel, user_id=bot.get_me().id)
                if bot_member_channel.status == 'administrator' and bot_member_channel.can_restrict_members:
                    report += f"✅  <b>Force Channel ({escape(channel)}):</b> OK! Bot is admin with 'Ban Users' permission.\n"
                elif bot_member_channel.status == 'administrator':
                    report += f"🚫  <b>Force Channel ({escape(channel)}):</b> FAILED! Bot is admin, but lacks 'Ban Users' permission.\n"
                else:
                    report += f"🚫  <b>Force Channel ({escape(channel)}):</b> FAILED! Bot is NOT an admin here.\n"
            except Exception as e:
                report += f"🚫  <b>Force Channel ({escape(channel)}):</b> FAILED! Bot not in channel or username is wrong. Error: {escape(e)}\n"
                
            try:
                bot_member_group = bot.get_chat_member(chat_id=group, user_id=bot.get_me().id)
                if bot_member_group.status == 'administrator' and bot_member_group.can_restrict_members:
                    report += f"✅  <b>Force Group ({escape(group)}):</b> OK! Bot is admin with 'Ban Users' permission.\n"
                elif bot_member_group.status == 'administrator':
                    report += f"🚫  <b>Force Group ({escape(group)}):</b> FAILED! Bot is admin, but lacks 'Ban Users' permission.\n"
                else:
                    report += f"🚫  <b>Force Group ({escape(group)}):</b> FAILED! Bot is NOT an admin here.\n"
            except Exception as e:
                report += f"🚫  <b>Force Group ({escape(group)}):</b> FAILED! Bot not in group or username is wrong. Error: {escape(e)}\n"
            
            report += f"{UIFactory.DIVIDER}\n<pre>'Ban Users' permission is REQUIRED for Force Join to work.</pre>"
            bot.send_message(chat_id, report)

        # --- Admin Management ---
        elif action == "admin_manage_admins":
            if not is_owner(user_id):
                bot.answer_callback_query(call.id, "🚫 Owner-Only Access.", show_alert=True)
                return
            
            data = load_data()
            admin_ids = data["settings"].get("admin_ids", [])
            admin_text, admin_markup = UIFactory.manage_admins_panel(admin_ids)
            edit_panel_message(call, admin_text, admin_markup)

        elif action == "admin_add_admin":
            if not is_owner(user_id):
                bot.answer_callback_query(call.id, "🚫 Owner-Only Access.", show_alert=True)
                return
            send_premium_prompt("Please send the **User ID** of the person you want to make an admin.\n(Or reply <code>/promote</code> to their message).")
            admin_task_queue[chat_id] = "add_admin_id"
            
        elif action.startswith("admin_confirm_remove_admin_"):
            if not is_owner(user_id):
                bot.answer_callback_query(call.id, "🚫 Owner-Only Access.", show_alert=True)
                return
            admin_id_to_remove = int(action.split('_')[-1])
            confirm_text, confirm_markup = UIFactory.confirmation_message(
                f"remove admin status from {admin_id_to_remove}",
                callback_yes=f"admin_do_remove_admin_{admin_id_to_remove}",
                callback_no="admin_manage_admins"
            )
            edit_panel_message(call, confirm_text, confirm_markup)

        elif action.startswith("admin_do_remove_admin_"):
            if not is_owner(user_id):
                bot.answer_callback_query(call.id, "🚫 Owner-Only Access.", show_alert=True)
                return
                
            admin_id_to_remove = int(action.split('_')[-1])
            data = load_data()
            admin_ids = data["settings"].get("admin_ids", [])
            
            if admin_id_to_remove in admin_ids:
                admin_ids.remove(admin_id_to_remove)
                save_data(data)
            else:
                bot.answer_callback_query(call.id, "Error: Admin not found.")
                
            admin_text, admin_markup = UIFactory.manage_admins_panel(data["settings"].get("admin_ids", []))
            edit_panel_message(call, admin_text, admin_markup)

        # --- User Management ---
        elif action == "admin_user_manage":
            send_premium_prompt(f"{UIFactory.EMOJIS['users']} <b>User Management</b>\n\nPlease send the <b>User ID</b> (e.g., <code>12345678</code>) or <b>Username</b> (e.g., <code>@shuvohassan00</code>).\n\nOr, forward a user's message and reply to it with <code>/userinfo</code>.")
            admin_task_queue[chat_id] = "user_manage_check"

        # v22.0: View User Winnings
        elif action.startswith("admin_view_user_winnings_"):
            user_to_view_id = int(action.split('_')[-1])
            data = load_data()
            user_data = data.get("users", {}).get(str(user_to_view_id))
            if not user_data:
                bot.answer_callback_query(call.id, "Error: User not found in database.", show_alert=True)
                return
            
            winnings = user_data.get("winnings", [])
            report_text = UIFactory.user_winnings_report(user_data, winnings)
            bot.send_message(chat_id, report_text) # Send as new message

        elif action.startswith("admin_confirm_ban_user_"):
            user_to_ban_id = int(action.split('_')[-1])
            confirm_text, confirm_markup = UIFactory.confirmation_message(
                f"BAN user {user_to_ban_id}",
                callback_yes=f"admin_do_ban_user_{user_to_ban_id}",
                callback_no=f"admin_user_manage_refresh_{user_to_ban_id}"
            )
            edit_panel_message(call, confirm_text, confirm_markup)
            
        elif action.startswith("admin_do_ban_user_"):
            user_to_ban_id = int(action.split('_')[-1])
            
            if user_to_ban_id == OWNER_ID or user_to_ban_id in load_data()["settings"]["admin_ids"]:
                bot.answer_callback_query(call.id, "🚫 You cannot ban an Admin or the Owner.", show_alert=True)
                return
            
            data = load_data()
            if user_to_ban_id not in data["settings"]["banned_users"]:
                data["settings"]["banned_users"].append(user_to_ban_id)
                save_data(data)
            
            user_data = data.get("users", {}).get(str(user_to_ban_id))
            panel_text, panel_markup = UIFactory.user_manage_panel(user_to_ban_id, user_data, is_banned=True)
            edit_panel_message(call, panel_text, panel_markup)
            
        elif action.startswith("admin_unban_user_"):
            user_to_unban_id = int(action.split('_')[-1])
            data = load_data()
            if user_to_unban_id in data["settings"]["banned_users"]:
                data["settings"]["banned_users"].remove(user_to_unban_id)
                save_data(data)
            
            user_data = data.get("users", {}).get(str(user_to_unban_id))
            panel_text, panel_markup = UIFactory.user_manage_panel(user_to_unban_id, user_data, is_banned=False)
            edit_panel_message(call, panel_text, panel_markup)
            
        elif action.startswith("admin_user_manage_refresh_"):
            user_to_refresh_id = int(action.split('_')[-1])
            data = load_data()
            user_data = data.get("users", {}).get(str(user_to_refresh_id))
            is_banned = user_to_refresh_id in data["settings"].get("banned_users", [])
            panel_text, panel_markup = UIFactory.user_manage_panel(user_to_refresh_id, user_data, is_banned)
            edit_panel_message(call, panel_text, panel_markup)

        # --- Giveaway Management ---
        elif action == "admin_create_giveaway":
            send_premium_prompt("Please send the name for the new giveaway (e.g., 'Netflix Premium Account').")
            admin_task_queue[chat_id] = "create_giveaway_name"

        elif action == "admin_manage_giveaways":
            data = load_data()
            list_text, list_markup = UIFactory.manage_giveaways_panel(data["giveaways"])
            edit_panel_message(call, list_text, list_markup)

        elif action.startswith("admin_view_giveaway_"):
            gid = action.split('_')[-1]
            data = load_data()
            if gid not in data["giveaways"]:
                bot.answer_callback_query(call.id, "Error: This giveaway was deleted.", show_alert=True)
                list_text, list_markup = UIFactory.manage_giveaways_panel(data["giveaways"])
                edit_panel_message(call, list_text, list_markup)
                return
            gdata = data["giveaways"][gid]
            manage_text, manage_markup = UIFactory.giveaway_details_panel(gid, gdata)
            edit_panel_message(call, manage_text, manage_markup)

        # v22.0: Dual-Mode Stocking
        elif action.startswith("admin_smart_stock_"):
            gid = action.split('_')[-1]
            data = load_data()
            giveaway_name = data["giveaways"].get(gid, {}).get("name", "Unknown Giveaway")
            send_premium_prompt(f"<b>🚀 Smart Stocking</b>\nReady to add a prize to <b>{escape(giveaway_name)}</b>.\n\nPlease send the <b>Prize Text</b> (e.g., <code>user@pass.com</code>).\n\nA unique code will be <b>auto-generated</b>.")
            admin_task_queue[chat_id] = f"add_prize_smart_stock_{gid}"
        
        elif action.startswith("admin_pro_stock_"):
            gid = action.split('_')[-1]
            data = load_data()
            giveaway_name = data["giveaways"].get(gid, {}).get("name", "Unknown Giveaway")
            send_premium_prompt(f"<b>🧑‍💻 Pro Stocking (Step 1/2)</b>\nReady to add a prize to <b>{escape(giveaway_name)}</b>.\n\nPlease send the <b>Prize Text</b> (e.g., <code>user@pass.com</code>).")
            admin_task_queue[chat_id] = f"pro_stock_prize_text_{gid}"
            
        elif action.startswith("admin_batch_add_prize_"):
            gid = action.split('_')[-1]
            data = load_data()
            giveaway_name = data["giveaways"].get(gid, {}).get("name", "Unknown Giveaway")
            send_premium_prompt(f"{UIFactory.EMOJIS['upload']} <b>Batch Upload to {escape(giveaway_name)}</b>\n\nPlease upload a <code>.txt</code> file.\nEach line of the file should contain one prize text.")
            admin_task_queue[chat_id] = f"batch_add_prize_{gid}"
            
        elif action.startswith("admin_edit_giveaway_name_"):
            gid = action.split('_')[-1]
            data = load_data()
            giveaway_name = data["giveaways"].get(gid, {}).get("name", "Unknown Giveaway")
            send_premium_prompt(f"Ready to edit name for <b>{escape(giveaway_name)}</b>.\n\nPlease send the new name.")
            admin_task_queue[chat_id] = f"edit_giveaway_name_{gid}"
            
        elif action.startswith("admin_clone_giveaway_"):
            gid = action.split('_')[-1]
            data = load_data()
            if gid not in data["giveaways"]:
                bot.answer_callback_query(call.id, "Error: Giveaway not found.", show_alert=True)
                return
            
            gdata = data["giveaways"][gid]
            if not gdata["prizes"]:
                bot.answer_callback_query(call.id, "Error: Cannot clone an empty giveaway.", show_alert=True)
                return
            
            new_gid = str(uuid.uuid4())[:6]
            new_giveaway_name = f"{gdata['name']} (Clone)"
            
            new_giveaway = {
                "name": new_giveaway_name,
                "created_at": datetime.now(BOT_TIMEZONE).isoformat(),
                "prizes": {}
            }
            
            stocked_count = 0
            for old_code, old_prize in gdata["prizes"].items():
                prize_text = old_prize["prize_text"]
                new_code = generate_code(new_giveaway_name)
                while not is_code_unique(new_code, data) and new_code not in new_giveaway["prizes"]:
                    new_code = generate_code(new_giveaway_name)
                
                new_giveaway["prizes"][new_code] = {
                    "prize_text": prize_text, "redeemed": False, "redeemed_by_user_id": None,
                    "redeemed_by_username": None, "redeemed_at": None
                }
                stocked_count += 1
                
            data["giveaways"][new_gid] = new_giveaway
            save_data(data)
            
            bot.send_message(chat_id, UIFactory.success_message(f"<b>Giveaway Cloned!</b>\nCreated '<b>{escape(new_giveaway_name)}</b>' (ID: <code>{new_gid}</code>) with <b>{stocked_count}</b> new prizes."))
            
            list_text, list_markup = UIFactory.manage_giveaways_panel(data["giveaways"])
            edit_panel_message(call, list_text, list_markup)

        elif action.startswith("admin_prize_list_"):
            parts = action.split('_')
            gid = parts[3]
            page = int(parts[4])
            
            data = load_data()
            if gid not in data["giveaways"]:
                bot.answer_callback_query(call.id, "Error: Giveaway not found.", show_alert=True)
                return
            
            gdata = data["giveaways"][gid]
            panel_text, panel_markup = UIFactory.prize_list_panel(gid, gdata, page)
            edit_panel_message(call, panel_text, panel_markup)
            
        elif action.startswith("admin_edit_prize_text_"):
            parts = action.split('_')
            gid = parts[4]
            code = "_".join(parts[5:]) 
            data = load_data()
            prize_text = data["giveaways"][gid]["prizes"][code]["prize_text"]
            send_premium_prompt(f"Ready to edit prize text for code <code>{escape(code)}</code>.\n\nThe current text is:\n<pre>{escape(prize_text)}</pre>\n\nPlease send the new prize text.")
            admin_task_queue[chat_id] = f"edit_prize_text_{gid}_{code}"
            
        elif action.startswith("admin_confirm_delete_prize_"):
            parts = action.split('_')
            gid = parts[4]
            page = int(parts[-1])
            code = "_".join(parts[5:-1])
            
            confirm_text, confirm_markup = UIFactory.confirmation_message(
                f"delete prize code {escape(code)}",
                callback_yes=f"admin_do_delete_prize_{gid}_{code}_{page}",
                callback_no=f"admin_prize_list_{gid}_{page}"
            )
            edit_panel_message(call, confirm_text, confirm_markup)
            
        elif action.startswith("admin_do_delete_prize_"):
            parts = action.split('_')
            gid = parts[4]
            page = int(parts[-1])
            code = "_".join(parts[5:-1])
            
            data = load_data()
            if gid not in data["giveaways"]:
                bot.answer_callback_query(call.id, "Error: Giveaway not found.", show_alert=True)
                return
            if code not in data["giveaways"][gid]["prizes"]:
                bot.answer_callback_query(call.id, "Error: Prize code already deleted.", show_alert=True)
                return
            if data["giveaways"][gid]["prizes"][code]["redeemed"]:
                bot.answer_callback_query(call.id, "Error: Cannot delete a prize that is already redeemed.", show_alert=True)
                return
                
            del data["giveaways"][gid]["prizes"][code]
            save_data(data)
            
            gdata = data["giveaways"][gid]
            total_prizes = len(gdata.get('prizes', {}))
            total_pages = math.ceil(total_prizes / PRIZES_PER_PAGE) if total_prizes > 0 else 1
            if page >= total_pages and page > 0:
                page -= 1 

            panel_text, panel_markup = UIFactory.prize_list_panel(gid, gdata, page)
            edit_panel_message(call, panel_text, panel_markup)

        elif action.startswith("admin_export_codes_"):
            gid = action.split('_')[-1]
            data = load_data()
            if gid not in data["giveaways"]:
                bot.answer_callback_query(call.id, "Error: Giveaway not found.", show_alert=True)
                return
            
            gdata = data["giveaways"][gid]
            unredeemed_codes = []
            for code, prize in gdata["prizes"].items():
                if not prize["redeemed"]:
                    unredeemed_codes.append(code)
            
            if not unredeemed_codes:
                bot.answer_callback_query(call.id, "No unredeemed codes found for this giveaway.", show_alert=True)
                return
            
            file_content = "\n".join(unredeemed_codes)
            file_stream = io.StringIO(file_content)
            file_stream.name = f"unredeemed_codes_{escape(gdata['name'])}.txt"
            
            bot.send_document(chat_id, file_stream, caption=f"✅ Here are the <b>{len(unredeemed_codes)}</b> unredeemed codes for '<b>{escape(gdata['name'])}</b>'.")
            
        elif action.startswith("admin_export_full_report_"):
            gid = action.split('_')[-1]
            data = load_data()
            if gid not in data["giveaways"]:
                bot.answer_callback_query(call.id, "Error: Giveaway not found.", show_alert=True)
                return
            
            gdata = data["giveaways"][gid]
            if not gdata["prizes"]:
                bot.answer_callback_query(call.id, "This giveaway has no prizes to report.", show_alert=True)
                return

            report_lines = [f"Full Report for: {gdata['name']}", f"Giveaway ID: {gid}", f"Total Prizes: {len(gdata['prizes'])}", "="*30, ""]
            
            redeemed_count = 0
            for code, prize in gdata["prizes"].items():
                report_lines.append(f"Code: {code}")
                report_lines.append(f"Prize: {prize['prize_text']}")
                if prize["redeemed"]:
                    redeemed_count += 1
                    redeemed_at = "Unknown Date"
                    try:
                        redeemed_at = datetime.fromisoformat(prize['redeemed_at']).strftime("%d-%b-%Y %I:%M %p")
                    except:
                        pass
                    report_lines.append(f"Status: REDEEMED")
                    report_lines.append(f"By: @{prize.get('redeemed_by_username', 'N/A')} (ID: {prize.get('redeemed_by_user_id', 'N/A')})")
                    report_lines.append(f"On: {redeemed_at}")
                else:
                    report_lines.append(f"Status: UNREDEEMED")
                report_lines.append("-"*20)
            
            report_lines.insert(3, f"Redeemed: {redeemed_count}")
            report_lines.insert(4, f"Remaining: {len(gdata['prizes']) - redeemed_count}")

            file_content = "\n".join(report_lines)
            file_stream = io.StringIO(file_content)
            file_stream.name = f"full_report_{escape(gdata['name'])}.txt"
            
            bot.send_document(chat_id, file_stream, caption=f"✅ Here is the <b>Full Report</b> for '<b>{escape(gdata['name'])}</b>'.")

        elif action.startswith("admin_generate_smart_post_"):
            gid = action.split('_')[-1]
            data = load_data()
            if gid not in data["giveaways"]:
                bot.answer_callback_query(call.id, "Error: Giveaway not found.", show_alert=True)
                return
            
            gdata = data["giveaways"][gid]
            unredeemed_codes = [code for code, prize in gdata["prizes"].items() if not prize["redeemed"]]
            
            if not unredeemed_codes:
                bot.answer_callback_query(call.id, "🚫 Error: There are no unredeemed codes in this giveaway to generate a post for. Please stock some prizes first.", show_alert=True)
                return

            code_count = len(unredeemed_codes)
            example_code = unredeemed_codes[0] 
            giveaway_name = gdata["name"]
            bot_username = bot.get_me().username
            
            post_text, _ = UIFactory.generate_giveaway_post(giveaway_name, code_count, [example_code], bot_username)
            
            bot.send_message(chat_id, post_text, reply_markup=None) 
            
            send_premium_prompt(f"<b>{UIFactory.EMOJIS['magic']} Smart Post Generated!</b> ⬆️\n\nI have generated the post text for <b>{code_count}</b> prizes.\n\nNow, do you want to add a <b>Custom Button</b> or <b>Image</b>?\n\n<b>Reply with:</b>\n1. <b>Button:</b> <code>Join | https://t.me/...</code>\n2. <b>Image:</b> <code>https://i.imgur.com/...</code>\n3. Send <code>skip</code> to do nothing.")
            admin_task_queue[chat_id] = f"generate_post_extras_{gid}"


        elif action.startswith("admin_confirm_delete_giveaway_"):
            gid = action.split('_')[-1]
            gdata = load_data().get("giveaways", {}).get(gid)
            gname = gdata['name'] if gdata else "DELETED"
            
            confirm_text, confirm_markup = UIFactory.confirmation_message(
                f"DELETE the giveaway '{escape(gname)}' (ID: {gid})",
                callback_yes=f"admin_do_delete_giveaway_{gid}",
                callback_no=f"admin_view_giveaway_{gid}" if gdata else "admin_manage_giveaways"
            )
            edit_panel_message(call, confirm_text, confirm_markup)
            
        elif action.startswith("admin_do_delete_giveaway_"):
            gid = action.split('_')[-1]
            data = load_data()
            if gid in data["giveaways"]:
                deleted_name = data["giveaways"].pop(gid)
                save_data(data)
            else:
                bot.answer_callback_query(call.id, "Error: Giveaway already deleted.")
                
            list_text, list_markup = UIFactory.manage_giveaways_panel(data["giveaways"])
            edit_panel_message(call, list_text, list_markup)

        # --- Broadcast & Stats & Global Stock ---
        elif action == "admin_broadcast":
            send_premium_prompt("<b>Step 1/2: Broadcast Message</b>\n\nPlease send the message you want to broadcast to all users.\n(Supports HTML formatting).")
            admin_task_queue[chat_id] = "broadcast_message"

        elif action == "admin_global_stock":
            data = load_data()
            global_stock = []
            
            sorted_giveaways = sorted(data.get('giveaways', {}).items(), key=lambda item: item[1]['name'])
            
            for gid, gdata in sorted_giveaways:
                gname = gdata['name']
                sorted_prizes = sorted(gdata.get('prizes', {}).items())
                
                for code, prize in sorted_prizes:
                    if not prize.get('redeemed', False):
                        global_stock.append({'gname': gname, 'code': code, 'prize': prize['prize_text']})

            stock_text, stock_markup = UIFactory.global_stock_message(global_stock)
            bot.send_message(chat_id, stock_text, reply_markup=stock_markup)
        
        # v22.0: Admin Search
        elif action == "admin_search_stock":
            send_premium_prompt(f"{UIFactory.EMOJIS['search']} <b>Search Stock</b>\n\nPlease send a search term. I will search for this text in all unredeemed prize codes and prize texts.")
            admin_task_queue[chat_id] = "admin_do_search"

        elif action == "admin_stats":
            data = load_data()
            total_users = len(data.get('users', {}))
            
            all_giveaways = data.get('giveaways', {})
            total_giveaways_count = len(all_giveaways)
            
            total_prizes, total_redeemed = 0, 0
            giveaway_redeem_counts = defaultdict(lambda: {'name': '', 'redeemed': 0})
            
            for gid, gdata in all_giveaways.items():
                redeemed_count = 0
                total_prizes += len(gdata.get('prizes', {}))
                for p in gdata.get('prizes', {}).values():
                    if p.get('redeemed'):
                        redeemed_count += 1
                
                total_redeemed += redeemed_count
                giveaway_redeem_counts[gid]['name'] = gdata.get('name', 'Unknown')
                giveaway_redeem_counts[gid]['redeemed'] = redeemed_count
            
            remaining_prizes = total_prizes - total_redeemed
            
            # Sort and get top giveaways
            sorted_g_stats = sorted(giveaway_redeem_counts.values(), key=lambda x: x['redeemed'], reverse=True)
            top_giveaways = [g for g in sorted_g_stats if g['redeemed'] > 0][:TOP_GIVEAWAY_COUNT]
            
            stats_text, stats_markup = UIFactory.stats_message(total_users, total_giveaways_count, total_prizes, total_redeemed, remaining_prizes, top_giveaways)
            edit_panel_message(call, stats_text, stats_markup)

    except Exception as e:
        print(f"Admin Callback Error: {e}")
        try:
            bot.answer_callback_query(call.id, "An error occurred.")
        except: pass

# -----------------------------------------------------------------------------------
# 🛡️ --- ADMIN: TASK HANDLER (v22.0 - Threaded) --- 🛡️
# -----------------------------------------------------------------------------------
@bot.message_handler(
    func=lambda message: admin_task_queue.get(message.chat.id) is not None and is_admin(message.from_user.id),
    content_types=['text', 'document']
)
def admin_input_handler(message):
    process_threaded(handle_admin_input, message)

def handle_admin_input(message):
    chat_id = message.chat.id
    step = admin_task_queue.get(chat_id) 
    text_input = message.text

    if text_input and text_input == "/cancel":
        admin_task_queue.pop(chat_id, None)
        admin_task_queue.pop(f"{chat_id}_pro_prize_text", None)
        bot.send_message(chat_id, UIFactory.cancelled_message())
        return

    def send_premium_reply(text):
        bot.send_message(chat_id, UIFactory.success_message(text))
    def send_premium_error(text):
        bot.send_message(chat_id, UIFactory.error_message(text))
    def send_premium_prompt(text):
        prompt_text = UIFactory.prompt_message(f"{text}<pre>\n\nOr send /cancel to abort.</pre>")
        bot.send_message(chat_id, prompt_text)
        
    try:
        if step.startswith("batch_add_prize_"):
            if message.document:
                if message.document.mime_type != 'text/plain':
                    send_premium_error("Invalid file type. Please upload a <code>.txt</code> file only.")
                    return
                
                gid = step.split('_')[-1]
                admin_task_queue.pop(chat_id)
                bot.send_message(chat_id, f"{UIFactory.EMOJIS['db']} File received. Processing... this may take a moment.")
                
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                
                prize_list = downloaded_file.decode('utf-8').splitlines()
                prize_list = [prize.strip() for prize in prize_list if prize.strip()]
                
                if not prize_list:
                    send_premium_error("The file is empty or contains only blank lines.")
                    return
                
                data = load_data()
                if gid not in data["giveaways"]:
                    send_premium_error("Giveaway ID not found. Action cancelled.")
                    return
                
                giveaway_name = data["giveaways"][gid]["name"]
                
                stocked_count = 0
                for prize_text in prize_list:
                    new_code = generate_code(giveaway_name)
                    while not is_code_unique(new_code, data):
                        new_code = generate_code(giveaway_name)
                    
                    data["giveaways"][gid]["prizes"][new_code] = {
                        "prize_text": prize_text, "redeemed": False, "redeemed_by_user_id": None,
                        "redeemed_by_username": None, "redeemed_at": None
                    }
                    stocked_count += 1

                save_data(data)
                
                bot.reply_to(message, UIFactory.stock_multi_success_message(giveaway_name, stocked_count))
                return

            elif text_input:
                send_premium_error("Please upload a <code>.txt</code> file, or send /cancel.")
                return
        
        if not text_input:
             send_premium_error("Invalid input. Please send text or /cancel.")
             return
             
        step = admin_task_queue.pop(chat_id)
        text_input = text_input.strip()

        if step == "set_channel_name":
            if not text_input.startswith('@'):
                send_premium_error("Invalid username. It must start with @. Action cancelled.")
                return
            data = load_data()
            data["settings"]["force_channel"] = text_input
            save_data(data)
            send_premium_reply(f"Force join channel set to <b>{escape(text_input)}</b>.")

        elif step == "set_group_name":
            if not text_input.startswith('@'):
                send_premium_error("Invalid username. It must start with @. Action cancelled.")
                return
            data = load_data()
            data["settings"]["force_group"] = text_input
            save_data(data)
            send_premium_reply(f"Force join group set to <b>{escape(text_input)}</b>.")
            
        elif step == "set_admin_user":
            if not text_input.startswith('@'):
                send_premium_error("Invalid username. It must start with @. Action cancelled.")
                return
            data = load_data()
            data["settings"]["admin_username"] = text_input
            save_data(data)
            send_premium_reply(f"Admin username for screenshot proof set to <b>{escape(text_input)}</b>.")
        
        elif step == "set_welcome_image":
            data = load_data()
            if text_input.upper() == 'NONE':
                data["settings"]["welcome_image_url"] = "NONE"
                save_data(data)
                send_premium_reply("Branding image has been removed.")
                return

            if not re.match(URL_REGEX, text_input):
                send_premium_error("Invalid URL. Please send a valid direct image link. Action cancelled.")
                return
                
            try:
                bot.send_photo(chat_id, text_input, caption="✅ Branding image set successfully! This is how all admin panels and replies will look.")
                data["settings"]["welcome_image_url"] = text_input
                save_data(data)
            except Exception as e:
                send_premium_error(f"Could not load this image URL. Please check the link and try again.\n<pre>{escape(e)}</pre>")
                
        elif step == "set_user_welcome_image":
            data = load_data()
            if text_input.upper() == 'NONE':
                data["settings"]["user_welcome_image_url"] = "NONE"
                save_data(data)
                send_premium_reply("User Welcome Image has been removed.")
                return

            if not re.match(URL_REGEX, text_input):
                send_premium_error("Invalid URL. Please send a valid direct image link. Action cancelled.")
                return
                
            try:
                bot.send_photo(chat_id, text_input, caption="✅ User Welcome Image set successfully! This is what users will see on /start.")
                data["settings"]["user_welcome_image_url"] = text_input
                save_data(data)
            except Exception as e:
                send_premium_error(f"Could not load this image URL. Please check the link and try again.\n<pre>{escape(e)}</pre>")
                
        elif step == "add_admin_id":
            if not is_owner(message.from_user.id):
                send_premium_error("This action is for the Owner only.")
                return
            
            try:
                new_admin_id = int(text_input)
                if new_admin_id == OWNER_ID:
                    send_premium_error("You are already the Owner.")
                    return
                
                data = load_data()
                admin_ids = data["settings"]["admin_ids"]
                if new_admin_id in admin_ids:
                    send_premium_error(f"This user ({new_admin_id}) is already an admin.")
                    return
                
                admin_ids.append(new_admin_id)
                save_data(data)
                send_premium_reply(f"Success! User <code>{new_admin_id}</code> is now an admin.")
            except ValueError:
                send_premium_error("Invalid User ID. Please send only the numerical ID. Action cancelled.")
            except Exception as e:
                send_premium_error(f"An error occurred: {escape(e)}")

        elif step == "user_manage_check":
            user_to_check_id = None
            user_data = None
            data = load_data()
            
            if text_input.startswith('@'):
                target_username = text_input[1:].lower()
                for uid_str, udata in data.get("users", {}).items():
                    if udata.get('username', '').lower() == target_username:
                        user_to_check_id = int(uid_str) 
                        user_data = udata
                        break
            else:
                try:
                    user_to_check_id = int(text_input)
                    user_data = data.get("users", {}).get(str(user_to_check_id))
                except ValueError:
                    send_premium_error("Invalid input. Please send a numerical User ID or an @username. Action cancelled.")
                    return
                except Exception as e:
                    send_premium_error(f"An error occurred: {escape(e)}")
                    return
            
            if user_data and user_to_check_id:
                if (is_admin(user_to_check_id) or is_owner(user_to_check_id)) and not is_owner(message.from_user.id):
                    send_premium_error("🚫 Access Denied!\nYou cannot manage another Admin or the Owner.")
                    return
                    
                is_banned = user_to_check_id in data.get("settings", {}).get("banned_users", [])
                panel_text, panel_markup = UIFactory.user_manage_panel(user_to_check_id, user_data, is_banned)
            else:
                panel_text, panel_markup = UIFactory.user_manage_panel(text_input, None, is_banned=False)
                
            send_branded_message(chat_id, panel_text, reply_markup=panel_markup)

        elif step == "create_giveaway_name":
            giveaway_name = text_input
            data = load_data()
            giveaway_id = str(uuid.uuid4())[:6]
            data["giveaways"][giveaway_id] = {"name": giveaway_name, "created_at": datetime.now(BOT_TIMEZONE).isoformat(), "prizes": {}}
            save_data(data)
            send_premium_reply(f"Giveaway '<b>{escape(giveaway_name)}</b>' created with ID: <code>{giveaway_id}</code>\n\nYou can now manage it from the panel.")

        elif step.startswith("add_prize_smart_stock_"):
            gid = step.split('_')[-1]
            prize_text = message.text 
            
            data = load_data()
            if gid not in data["giveaways"]:
                send_premium_error("Giveaway ID not found. Action cancelled.")
                return
                
            giveaway_name = data["giveaways"][gid]["name"]
            
            new_code = generate_code(giveaway_name)
            while not is_code_unique(new_code, data):
                new_code = generate_code(giveaway_name)
            
            data["giveaways"][gid]["prizes"][new_code] = {
                "prize_text": prize_text, "redeemed": False, "redeemed_by_user_id": None,
                "redeemed_by_username": None, "redeemed_at": None
            }
            save_data(data)
            
            bot.reply_to(message, UIFactory.stock_success_message(giveaway_name, prize_text, new_code))

        elif step.startswith("pro_stock_prize_text_"):
            gid = step.split('_')[-1]
            prize_text = message.text
            
            admin_task_queue[f"{chat_id}_pro_prize_text"] = prize_text
            admin_task_queue[chat_id] = f"pro_stock_prize_code_{gid}"
            send_premium_prompt(f"<b>🧑‍💻 Pro Stocking (Step 2/2)</b>\nPrize text set to:\n<pre>{escape(prize_text)}</pre>\n\nPlease send the <b>Custom Redeem Code</b> for this prize (e.g., <code>MY-CODE-123</code>).")

        elif step.startswith("pro_stock_prize_code_"):
            gid = step.split('_')[-1]
            prize_text = admin_task_queue.pop(f"{chat_id}_pro_prize_text", None)
            redeem_code = text_input.strip().upper()
            
            if not prize_text:
                send_premium_error("An error occurred (prize text was lost). Please start over.")
                return
            
            data = load_data()
            if gid not in data["giveaways"]:
                send_premium_error("Giveaway ID not found. Action cancelled.")
                return
                
            giveaway_name = data["giveaways"][gid]["name"]
            
            if not is_code_unique(redeem_code, data):
                send_premium_error("This code is already in use. Please send a different code.")
                admin_task_queue[f"{chat_id}_pro_prize_text"] = prize_text
                admin_task_queue[chat_id] = f"pro_stock_prize_code_{gid}"
                return
            
            data["giveaways"][gid]["prizes"][redeem_code] = {
                "prize_text": prize_text, "redeemed": False, "redeemed_by_user_id": None,
                "redeemed_by_username": None, "redeemed_at": None
            }
            save_data(data)
            
            bot.reply_to(message, UIFactory.stock_success_message(giveaway_name, prize_text, redeem_code))

        elif step.startswith("edit_giveaway_name_"):
            gid = step.split('_')[-1]
            new_name = text_input
            
            data = load_data()
            if gid not in data["giveaways"]:
                send_premium_error("Giveaway ID not found. Action cancelled.")
                return
            
            data["giveaways"][gid]["name"] = new_name
            save_data(data)
            send_premium_reply(f"Giveaway name has been updated to <b>{escape(new_name)}</b>.")

        elif step.startswith("edit_prize_text_"):
            parts = step.split('_')
            gid = parts[3]
            code = "_".join(parts[4:])
            new_prize_text = message.text
            
            data = load_data()
            if gid not in data["giveaways"] or code not in data["giveaways"][gid]["prizes"]:
                send_premium_error("Prize or Giveaway not found. Action cancelled.")
                return
            
            data["giveaways"][gid]["prizes"][code]["prize_text"] = new_prize_text
            save_data(data)
            send_premium_reply(f"Prize text for code <code>{escape(code)}</code> has been updated.")

        elif step.startswith("generate_post_extras_"):
            gid = step.split('_')[-1]
            button_input = text_input
            
            post_markup = None
            post_image_url = None
            
            if button_input.upper() == 'SKIP':
                send_premium_reply("<b>Smart Post Complete!</b>\nYour post is ready to be forwarded.")
                return

            elif button_input.startswith('http'):
                if not re.match(URL_REGEX, button_input):
                    send_premium_error("Invalid URL. Action cancelled. Please start over.")
                    return
                post_image_url = button_input
            
            elif '|' in button_input:
                try:
                    button_parts = button_input.split('|')
                    button_text = button_parts[0].strip()
                    button_url = button_parts[1].strip()
                    if not re.match(URL_REGEX, button_url):
                         send_premium_error("Invalid URL in button. Action cancelled. Please start over.")
                         return
                    
                    post_markup = InlineKeyboardMarkup()
                    post_markup.add(InlineKeyboardButton(button_text, url=button_url))
                except Exception as e:
                    send_premium_error(f"Invalid button format. It must be <code>Text | URL</code>. Action cancelled.\n<pre>{escape(e)}</pre>")
                    return
            else:
                send_premium_error("Invalid input. Please send an image URL, a button (<code>Text | URL</code>), or <code>skip</code>.")
                admin_task_queue[chat_id] = f"generate_post_extras_{gid}" # Reset step
                return

            data = load_data()
            gdata = data["giveaways"][gid]
            unredeemed_codes = [code for code, prize in gdata["prizes"].items() if not prize["redeemed"]]
            
            code_count = len(unredeemed_codes)
            example_code = unredeemed_codes[0]
            giveaway_name = gdata["name"]
            bot_username = bot.get_me().username
            
            post_text, post_markup = UIFactory.generate_giveaway_post(giveaway_name, code_count, [example_code], bot_username, post_markup)
            
            if post_image_url:
                try:
                    bot.send_photo(chat_id, post_image_url)
                except Exception as e:
                    bot.send_message(chat_id, f"Could not send image URL: {escape(e)}. Sending text post only.")
            
            bot.send_message(chat_id, post_text, reply_markup=post_markup)
            send_premium_reply("<b>Smart Post Complete!</b> ⬆️\nYour post with extras is ready.")

        elif step == "broadcast_message":
            broadcast_text = message.text 
            send_premium_prompt("<b>Step 2/2: Broadcast Image</b>\n\nMessage text set. Now, please send a direct URL for an image to attach.\n\nOr send <code>skip</code> to send text-only.")
            admin_task_queue[chat_id] = "broadcast_image"
            admin_task_queue[f"{chat_id}_broadcast_text"] = broadcast_text

        elif step == "broadcast_image":
            broadcast_text = admin_task_queue.pop(f"{chat_id}_broadcast_text", "Error: Message not found.")
            image_url = text_input
            
            bot.send_message(chat_id, f"{UIFactory.EMOJIS['broadcast']} Broadcasting... this may take a while.")
            data = load_data()
            user_ids = list(data["users"].keys())
            banned_users = data["settings"].get("banned_users", [])
            sent, failed, skipped = 0, 0, 0
            
            use_image = image_url.upper() != 'SKIP' and image_url.upper() != 'NONE'
            if use_image and not re.match(URL_REGEX, image_url):
                send_premium_error("Invalid Image URL. Broadcast cancelled.")
                return

            start_time = time.time()
            for user_id_str in user_ids:
                user_id_int = int(user_id_str)
                if is_admin(user_id_int) or user_id_int in banned_users:
                    skipped += 1
                    continue
                try:
                    if use_image:
                        bot.send_photo(user_id_int, image_url, caption=broadcast_text)
                    else:
                        bot.send_message(user_id_int, broadcast_text)
                    sent += 1
                except Exception as e:
                    failed += 1
                    print(f"Broadcast failed for {user_id_int}: {e}")
                
                if sent % 20 == 0:
                    time.sleep(1)
            
            end_time = time.time()
            total_time = round(end_time - start_time, 2)
            
            bot.send_message(chat_id, f"<b>Broadcast Complete!</b> (Took {total_time}s)\n{UIFactory.EMOJIS['success']} Sent to {sent} users.\n{UIFactory.EMOJIS['error']} Failed for {failed} users.\n{UIFactory.EMOJIS['warn']} Skipped {skipped} (Admins/Banned).")
        
        # v22.0: Admin Search
        elif step == "admin_do_search":
            search_term = text_input.lower()
            if not search_term:
                send_premium_error("Search term cannot be empty. Action cancelled.")
                return

            data = load_data()
            results = []
            sorted_giveaways = sorted(data.get('giveaways', {}).items(), key=lambda item: item[1]['name'])
            
            for gid, gdata in sorted_giveaways:
                gname = gdata['name']
                for code, prize in gdata.get('prizes', {}).items():
                    if not prize.get('redeemed', False):
                        if search_term in prize['prize_text'].lower() or search_term in code.lower():
                            results.append({'gname': gname, 'code': code, 'prize': prize['prize_text']})

            search_text, search_markup = UIFactory.search_results_message(text_input, results)
            bot.send_message(chat_id, search_text, reply_markup=search_markup)

    except Exception as e:
        if chat_id in admin_task_queue:
             admin_task_queue.pop(chat_id)
        admin_task_queue.pop(f"{chat_id}_pro_prize_text", None)
        send_premium_error(f"An unknown error occurred: <pre>{escape(e)}</pre>")
        print(f"Admin Input Handler Error: {e}")

# -----------------------------------------------------------------------------------
# 👤 --- USER: TASK HANDLER (v22.0 - Threaded) --- 👤
# -----------------------------------------------------------------------------------
@bot.message_handler(
    func=lambda message: user_task_queue.get(message.chat.id) is not None,
    content_types=['text']
)
def user_input_handler(message):
    process_threaded(handle_user_input, message)

def handle_user_input(message):
    chat_id = message.chat.id
    step = user_task_queue.get(chat_id)
    text_input = message.text

    if text_input and text_input == "/cancel":
        user_task_queue.pop(chat_id, None)
        bot.send_message(chat_id, UIFactory.cancelled_message())
        return

    try:
        step = user_task_queue.pop(chat_id)
        
        if step == "user_redeem_code":
            user = message.from_user
            redeem_code = text_input.strip().upper()
            
            # Run the redeem logic
            status, message_text = process_redeem_attempt(user, redeem_code)
            
            if status == 1: # Success
                send_branded_message(chat_id, message_text)
            else: # Error
                bot.reply_to(message, message_text)

    except Exception as e:
        if chat_id in user_task_queue:
             user_task_queue.pop(chat_id)
        bot.send_message(chat_id, UIFactory.error_message(f"An unknown error occurred: <pre>{escape(e)}</pre>"))
        print(f"User Input Handler Error: {e}")

# -----------------------------------------------------------------------------------
# 🚀 --- BOT LAUNCH (v22.0 - 'Quantum-Flux' Build) --- 🚀
# -----------------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"👑 {UIFactory.EMOJIS['crown']} 𝗚𝗔𝗗𝗚𝗘𝗧 𝗚𝗜𝗩𝗘𝗔𝗪𝗔𝗬 𝗕𝗢𝗧 𝗛𝗨𝗕 (v22.0 - 'Quantum-Flux' Build) is starting...")
    
    try:
        print("Setting bot commands...")
        bot.set_my_commands([
            BotCommand("start", "🚀 Start the Bot / Admin Panel"),
            BotCommand("redeem", "🎟️ Redeem a Gift Code"),
            BotCommand("mywinnings", "🎁 Show My Winnings"),
            BotCommand("userinfo", "🧑‍💻 (Admin) Get info for a user")
        ])
    except Exception as e:
        print(f"Warning: Could not set bot commands: {e}")

    while True:
        try:
            print("Attempting to connect to Telegram API...")
            print("Connection successful. Bot is now online and polling...")
            
            poll_thread = threading.Thread(target=bot.polling, kwargs={'non_stop': True, 'interval': 1, 'timeout': 30})
            poll_thread.start()
            
            poll_thread.join()

        except requests.exceptions.ConnectionError as e:
            print(f"!!! NETWORK ERROR: {e} !!!")
            print("Network is unreachable. Retrying in 15 seconds...")
            bot.stop_polling()
            time.sleep(15)
        except Exception as e:
            print(f"!!! BOT CRASHED: {e} !!!")
            print("An unexpected error occurred. Restarting in 15 seconds...")
            try:
                bot.stop_polling()
            except:
                pass
            time.sleep(15)
