# -----------------------------------------------------------------------------------
# 👑 𝗚𝗔𝗗𝗚𝗘𝗧 𝗚𝗜𝗩𝗘𝗔𝗪𝗔𝗬 𝗕𝗢𝗧 𝗛𝗨𝗕 (v18.0 - The 'Bug-Smasher' Build) 👑
# 𝗗𝗘𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡: v17.0 এর উপর ভিত্তি করে তৈরি। এই ভার্সনে v17 এর সেই
#              বিরক্তিকর "View/Edit Prizes" বাগটি ১০০% সমাধান করা হয়েছে।
#              এবং অ্যাডমিনদের জন্য নতুন "আল্ট্রা-প্রিমিয়াম" ফিচার যোগ করা হয়েছে।
#
# 𝗙𝗘𝗔𝗧𝗨𝗥𝗘𝗦 (v18.0):
#   1. [CRITICAL BUG FIX] 🐞 View/Edit Prizes Crash: ১০০% সমাধান করা হয়েছে।
#      `admin_prize_list_` এর callback parser টি ঠিক করা হয়েছে।
#      আগে এটা ছিল parts[2] ও parts[3], এখন parts[3] ও parts[4] করা হয়েছে।
#
#   2. [NEW - PREMIUM] 🔥 Dynamic Code System: "Add Prize" করার সময় বট এখন
#      প্রথমে Prize Text চাইবে, তারপর Redeem Code চাইবে। অ্যাডমিন চাইলে
#      নিজের কাস্টম কোড (e.g., "MY-CODE-123") দিতে পারবে অথবা "auto"
#      লিখে অটো-জেনারেট করতে পারবে।
#
#   3. [NEW - ADMIN QOL] 📊 Global Stock Report: অ্যাডমিন প্যানেলে নতুন বাটন।
#      বটের সমস্ত গিভওয়ের যতগুলো প্রাইজ এখনো রিডিম হয়নি, তার একটি
#      সম্পূর্ণ তালিকা একবারে দেখাবে।
#
#   4. [UI POLISH] ✨ Prettier Admin Panels: গিভওয়ে ম্যানেজমেন্ট প্যানেল
#      এবং প্রাইজ লিস্ট আরও সুন্দর ও তথ্যবহুল করা হয়েছে।
#
#   5. [KEPT] All v17.0 features (Leaderboard, Username Search, etc.)
#
# 𝗔𝗨𝗧𝗛𝗢𝗥: Shuvo Hassan (Concept & Vision)
# 𝗗𝗘𝗩𝗘𝗟𝗢𝗣𝗘𝗗 𝗕𝗬: Your AI Assistant (The 'Bug-Smasher' Build v18.0)
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
import threading
import uuid  # For unique codes
from datetime import datetime
import re  # For URL validation and Dynamic Codes
import pytz  # For "Live Time" (Timezone)
import io  # For exporting codes and batch uploading
import math # For pagination
import html # For HTML escaping

# -----------------------------------------------------------------------------------
# ⚙️ --- MAIN CONFIGURATION --- ⚙️
# -----------------------------------------------------------------------------------

# --- v5.0: The Bot Owner (YOU) ---
OWNER_ID = 6074463370  # ⚠️ This is YOUR ID.

# --- Bot Token ---
BOT_TOKEN = "7984240580:AAEth0NgopkraueMYdTwHq5JDGYfICqxge0"  # ⚠️ Put your bot's token here

# --- Database file name ---
DATA_FILE = "ultimate_giveaway_db_v18.json"  # v18.0 Database

# --- v3.0 Timezone Configuration ---
BOT_TIMEZONE = pytz.timezone("Asia/Dhaka")

# --- Global Bot Variables ---
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')
data_lock = threading.Lock()
admin_next_step = {}

# --- v12.0: Constants ---
PRIZES_PER_PAGE = 5 # Number of prizes to show in the 'View/Edit Prizes' list
WELCOME_GIFT_GID = "SYS_WELCOME_GIFT" # v16.0: Special GID for Welcome Gift
LEADERBOARD_COUNT = 5 # v17.0: How many top users to show

# --- URL Regex for validation ---
URL_REGEX = re.compile(
    r'^(?:http|ftp)s?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    r'(?::\d+)?'
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
# -----------------------------------------------------------------------------------
# 🛠️ --- v14.0: CORE HELPER FUNCTIONS --- 🛠️
# -----------------------------------------------------------------------------------

def escape(text):
    """
    v14.0: Escapes HTML special characters for safe rendering in messages.
    """
    if text is None:
        return ""
    return html.escape(str(text))

def get_live_time():
    """
    v14.0: Returns the current time formatted for the bot's timezone.
    """
    return datetime.now(BOT_TIMEZONE).strftime("%d-%b-%Y %I:%M %p (%Z)")


# -----------------------------------------------------------------------------------
# 🎨 --- PREMIUM UI FACTORY (v18.0) --- 🎨
# -----------------------------------------------------------------------------------
class UIFactory:
    # v17.0: Added Leaderboard emoji
    EMOJIS = {
        'crown': '👑', 'gift': '🎁', 'ticket': '🎟️', 'success': '✅', 'error': '🚫',
        'warn': '⚠️', 'admin': '🛡️', 'user': '👤', 'db': '💾', 'stats': '📊',
        'broadcast': '📡', 'settings': '⚙️', 'link': '🔗', 'check': '🔍',
        'pic': '🖼️', 'export': '📤', 'owner': '💎', 'group': '👥', 'post': '📢',
        'upload': '📤', 'star': '✨', 'rocket': '🚀', 'party': '🎉', 'back': '«',
        'plus': '➕', 'trash': '🗑️', 'list': '🗃️', 'download': '📥', 'alert': '🔔',
        'ban': '🚫', 'unban': '✅', 'edit': '✏️', 'users': '👥', 'clone': '🧬',
        'welcome': '👋', 'clock': '🕑', 'confirm': '❓', 'rename': '📝',
        'lock': '🔒', 'unlock': '🔓', 'new': '🌟', 'search': '🔍' # v17.0 Emojis
    }

    @staticmethod
    def design_box(title, body, footer):
        """
        v6.0 Original sleek box format.
        """
        return (f"<code>┌ {title}</code>\n"
                f"<code>│</code>\n{body}\n"
                f"<code>│</code>\n"
                f"└─➤ {footer}")

    # --- User Messages ---
    @staticmethod
    def welcome_message(user, welcome_gift_name=None):
        """
        v17.0: Shows welcome gift if provided and adds Top Winners button.
        """
        user_name = escape(user.first_name.encode('utf-8').decode('utf-8'))
        user_id = user.id
        user_link = f'<a href="tg://user?id={user_id}">{user_name}</a>'

        title = f"{UIFactory.EMOJIS['crown']} 𝗚𝗔𝗗𝗚𝗘𝗧 𝗚𝗜𝗩𝗘𝗔𝗪𝗔𝗬 𝗕𝗢𝗧 𝗛𝗨𝗕 {UIFactory.EMOJIS['crown']}"
        body = (f"<code>│</code> Hello <b>{user_link}</b>, Welcome to Our Bot.\n")
        
        if welcome_gift_name:
            body += (f"<code>│</code>\n"
                     f"<code>│</code> {UIFactory.EMOJIS['new']} As a special welcome gift, you have received:\n"
                     f"<code>│</code> <b>{escape(welcome_gift_name)}</b>\n"
                     f"<code>│</code> Use /mywinnings to see it!")
        
        body += (f"<code>│</code>\n"
                 f"<code>│</code> Stay tuned for daily new giveaways!!\n"
                 f"<code>│</code>\n"
                 f"<code>│</code> ℹ️  Use the buttons below to get started or\n"
                 f"<code>│</code>    send <code>/redeem CODE-XXXX-XXXX</code>")
        footer = f"{UIFactory.EMOJIS['clock']} {get_live_time()}"

        markup = InlineKeyboardMarkup(row_width=3)
        markup.add(
            InlineKeyboardButton(f"{UIFactory.EMOJIS['ticket']} Redeem Code", callback_data="user_redeem_prompt"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['gift']} My Winnings", callback_data="user_my_winnings"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['stats']} Live Stats", callback_data="user_public_stats")
        )
        # v17.0: Add Top Winners button
        markup.add(
            InlineKeyboardButton(f"{UIFactory.EMOJIS['crown']} Top Winners", callback_data="user_top_winners")
        )

        return UIFactory.design_box(title, body, footer), markup

    @staticmethod
    def redeem_success_message(user_name, prize_name, prize_text, admin_username, redeem_code):
        # v17.0: Polished UI
        title = f"{UIFactory.EMOJIS['party']} 𝗖𝗢𝗡𝗚𝗥𝗔𝗧𝗨𝗟𝗔𝗧𝗜𝗢𝗡𝗦, {escape(user_name)}!"
        body = (f"<code>│</code> You have successfully redeemed:\n"
                f"<code>│</code> <b>{escape(prize_name)}</b>\n"
                f"<code>│</code> (Code: <code>{escape(redeem_code)}</code>)\n"
                f"<code>│</code>\n"
                f"<code>│</code> <b>{UIFactory.EMOJIS['gift']} Here is your prize:</b>\n"
                f"<code>│</code> <pre>{escape(prize_text)}</pre>\n"
                f"<code>│</code>\n"
                f"<code>│</code> <b>{UIFactory.EMOJIS['alert']} PLEASE PROVIDE PROOF {UIFactory.EMOJIS['alert']}</b>\n"
                f"<code>│</code> Please login and send a screenshot to\n"
                f"<code>│</code> <b>{escape(admin_username)}</b> as proof!\n"
                f"<code>│</code>\n"
                f"<code>│</code> <b>{UIFactory.EMOJIS['warn']} Warning:</b> Providing proof is mandatory.\n"
                f"<code>│</code> Failure to send a review may result in\n"
                f"<code>│</code> a ban from future giveaways."
                )
        footer = "Thank you for participating!"
        return UIFactory.design_box(title, body, footer)

    @staticmethod
    def my_winnings_message(user_name, winnings):
        title = f"{UIFactory.EMOJIS['gift']} {escape(user_name)}'s 𝗪𝗜𝗡𝗡𝗜𝗡𝗚𝗦"
        if not winnings:
            body = f"<code>│</code> {UIFactory.EMOJIS['error']} You haven't won any prizes yet."
        else:
            body = "<code>│</code> <b>Here is a list of all the prizes you have redeemed:</b>\n"
            for i, win in enumerate(winnings, 1):
                body += f"<code>│</code>\n"
                body += f"<code>│</code> <b>{i}. {escape(win['giveaway_name'])}</b>\n"
                if win['giveaway_name'] == "Welcome Gift": # v16.0
                     body += f"<code>│</code>    <pre>{escape(win['prize_text'])}</pre>\n"
                else:
                    body += f"<code>│</code>    <pre>{escape(win['prize_text'])}</pre>\n"
                    body += f"<code>│</code>    <pre>Code: {escape(win['code'])}</pre>\n"
                body += f"<code>│</code>    <pre>Redeemed on: {escape(win['date'])}</pre>"
        footer = "Your personal prize vault."
        return UIFactory.design_box(title, body, footer)

    @staticmethod
    def public_stats_message(total_users, total_redeemed, active_giveaways):
        title = f"{UIFactory.EMOJIS['stats']} 𝗟𝗜𝗩𝗘 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦"
        body = (f"<code>│</code> <b>Building trust with our community!</b>\n"
                f"<code>│</code>\n"
                f"<code>│</code> {UIFactory.EMOJIS['users']} <b>Total Bot Users:</b> {total_users}\n"
                f"<code>│</code> {UIFactory.EMOJIS['party']} <b>Total Prizes Redeemed:</b> {total_redeemed}\n"
                f"<code>│</code> {UIFactory.EMOJIS['rocket']} <b>Active Giveaways:</b> {active_giveaways}\n"
                f"<code>│</code>\n"
                f"<code>│</code> Stay active to be the next winner!")
        footer = f"{UIFactory.EMOJIS['clock']} {get_live_time()}"
        return UIFactory.design_box(title, body, footer)

    # v17.0: New Message for Leaderboard
    @staticmethod
    def top_winners_message(top_users):
        title = f"{UIFactory.EMOJIS['crown']} 𝗧𝗢𝗣 {len(top_users)} 𝗪𝗜𝗡𝗡𝗘𝗥𝗦 𝗟𝗘𝗔𝗗𝗘𝗥𝗕𝗢𝗔𝗥𝗗"
        if not top_users:
            body = f"<code>│</code> {UIFactory.EMOJIS['error']} No winners found yet."
        else:
            body = "<code>│</code> <b>Here are our most dedicated winners:</b>\n"
            medals = [f"{UIFactory.EMOJIS['crown']}", '🥈', '🥉', '4.', '5.']
            
            for i, user_data in enumerate(top_users):
                name = escape(user_data.get('first_name', 'User'))
                username = f"(@{escape(user_data.get('username', 'N/A'))})" if user_data.get('username') else ""
                wins = len(user_data.get('winnings', []))
                
                medal = medals[i] if i < len(medals) else f"{i+1}."
                
                body += f"<code>│</code>\n"
                body += f"<code>│</code> <b>{medal} {name}</b> {username}\n"
                body += f"<code>│</code>    <b>Wins:</b> {wins}"
                
        footer = "Keep participating to get on the list!"
        return UIFactory.design_box(title, body, footer)

    @staticmethod
    def force_join_message(channel_username, group_username):
        title = f"{UIFactory.EMOJIS['warn']} 𝗠𝗘𝗠𝗕𝗘𝗥𝗦𝗛𝗜𝗣 𝗥𝗘𝗤𝗨𝗜𝗥𝗘𝗗"
        body = (f"<code>│</code> To use this bot, you must be a member of our\n"
                f"<code>│</code> channel <b>and</b> group.\n"
                f"<code>│</code>\n"
                f"<code>│</code> Please join both, then press 'Start' again.")
        footer = "Thank you for your support!"
        markup = InlineKeyboardMarkup(row_width=1)
        if channel_username:
            markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['link']} Join Our Channel", url=f"https://t.me/{channel_username.replace('@', '')}"))
        if group_username:
            markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['link']} Join Our Group", url=f"https://t.me/{group_username.replace('@', '')}"))
        return UIFactory.design_box(title, body, footer), markup

    @staticmethod
    def error_message(details):
        title = f"{UIFactory.EMOJIS['error']} 𝗔𝗡 𝗘𝗥𝗥𝗢𝗥 𝗢𝗖𝗖𝗨𝗥𝗥𝗘𝗗"
        body = f"<code>│</code> {UIFactory.EMOJIS['error']} <b>Details:</b> <code>{details}</code>"
        footer = "Please try again or contact the admin."
        return UIFactory.design_box(title, body, footer)
        
    @staticmethod
    def success_message(details):
        title = f"{UIFactory.EMOJIS['success']} 𝗦𝗨𝗖𝗖𝗘𝗦𝗦"
        body = f"<code>│</code> {UIFactory.EMOJIS['star']} {details}"
        footer = "Action completed."
        return UIFactory.design_box(title, body, footer)

    @staticmethod
    def prompt_message(details):
        title = f"{UIFactory.EMOJIS['warn']} 𝗔𝗖𝗧𝗜𝗢𝗡 𝗥𝗘𝗤𝗨𝗜𝗥𝗘𝗗"
        body = f"<code>│</code> 💬 {details}"
        footer = "Please reply to this message."
        return UIFactory.design_box(title, body, footer)
        
    @staticmethod
    def cancelled_message():
        title = f"{UIFactory.EMOJIS['error']} 𝗔𝗖𝗧𝗜𝗢𝗡 𝗖𝗔𝗡𝗖𝗘𝗟𝗟𝗘𝗗"
        body = f"<code>│</code> {UIFactory.EMOJIS['back']} The previous action has been cancelled."
        footer = "No changes were made."
        return UIFactory.design_box(title, body, footer)
        
    @staticmethod
    def confirmation_message(action_name, callback_yes, callback_no):
        title = f"{UIFactory.EMOJIS['confirm']} 𝗖𝗢𝗡𝗙𝗜𝗥𝗠 𝗔𝗖𝗧𝗜𝗢𝗡"
        body = (f"<code>│</code> Are you sure you want to <b>{escape(action_name)}</b>?\n"
                f"<code>│</code>\n"
                f"<code>│</code> <b>This action cannot be undone.</b>")
        footer = "Please confirm your choice."
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(f"{UIFactory.EMOJIS['success']} Yes, Confirm", callback_data=callback_yes),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['error']} No, Cancel", callback_data=callback_no)
        )
        return UIFactory.design_box(title, body, footer), markup

    # v16.0: Admin Panel Lock
    @staticmethod
    def locked_panel_message():
        title = f"{UIFactory.EMOJIS['lock']} 𝗣𝗔𝗡𝗘𝗟 𝗟𝗢𝗖𝗞𝗘D"
        body = (f"<code>│</code> The admin panel is currently locked for security.\n"
                f"<code>│</code>\n"
                f"<code>│</code> Click the button below to unlock.")
        footer = f"{UIFactory.EMOJIS['clock']} {get_live_time()}"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['unlock']} Unlock Panel", callback_data="admin_unlock_panel"))
        return UIFactory.design_box(title, body, footer), markup


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
            f"  2. Send this command: <code>/redeem {example_code}</code>\n\n"
            f"👇 <b>REDEEM BOT:</b>\n"
            f"@{bot_username}\n"
            f"@{bot_username}\n\n"
            f"🔺 <b>FIRST {code_count} USERS WILL WIN!</b> 🔺\n"
            f"Hurry Up! {UIFactory.EMOJIS['party']}\n\n"
            f"Bot Powered by @shuvohassan00"
        )
        return post, markup

    # --- Admin Panel Messages (v18.0) ---
    @staticmethod
    def admin_panel_message(is_owner):
        title = f"{UIFactory.EMOJIS['admin']} 𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 𝗖𝗘𝗡𝗧𝗘𝗥"
        body = "<code>│</code> Welcome, Admin. Please choose an action\n<code>│</code> from the buttons below."
        footer = f"{UIFactory.EMOJIS['clock']} {get_live_time()}"
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(f"{UIFactory.EMOJIS['gift']} Create Giveaway", callback_data="admin_create_giveaway"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['list']} Manage Giveaways", callback_data="admin_manage_giveaways"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['broadcast']} Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['stats']} Statistics", callback_data="admin_stats"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['users']} User Management", callback_data="admin_user_manage"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['settings']} Bot Settings", callback_data="admin_settings")
        )
        # v18.0: New Global Stock Report
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['db']} Global Stock Report", callback_data="admin_global_stock"))
        if is_owner:
            markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['crown']} Manage Admins", callback_data="admin_manage_admins"))
        
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['lock']} Lock Panel", callback_data="admin_lock_panel"))
        return UIFactory.design_box(title, body, footer), markup

    @staticmethod
    def settings_panel_message(settings):
        title = f"{UIFactory.EMOJIS['settings']} 𝗕𝗢𝗧 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦"
        channel = escape(settings.get('force_channel') or "Not Set")
        group = escape(settings.get('force_group') or "Not Set")
        fjoin_status = f"{UIFactory.EMOJIS['success']} ON" if settings.get('force_join_enabled', False) else f"{UIFactory.EMOJIS['error']} OFF"
        admin_user = escape(settings.get('admin_username') or "Not Set")
        brand_img = escape(settings.get('welcome_image_url') or "Not Set")
        welcome_img = escape(settings.get('user_welcome_image_url') or "Not Set")
        # v16.0: Welcome Gift
        wg_status = f"{UIFactory.EMOJIS['success']} ON" if settings.get('welcome_gift_enabled', False) else f"{UIFactory.EMOJIS['error']} OFF"
        wg_name = escape(settings.get('welcome_gift_name') or "Not Set")
        wg_prize = escape(settings.get('welcome_gift_prize') or "Not Set")


        body = (f"<code>│</code> <b>Force Join:</b> <code>{fjoin_status}</code> (Ch: <code>{channel}</code> | Gr: <code>{group}</code>)\n"
                f"<code>│</code> <b>Admin User:</b> <code>{admin_user}</code>\n"
                f"<code>│</code> <b>Branding Img:</b> <code>{brand_img if len(brand_img) < 25 else brand_img[:25] + '...'}</code>\n"
                f"<code>│</code> <b>Welcome Img:</b> <code>{welcome_img if len(welcome_img) < 25 else welcome_img[:25] + '...'}</code>\n"
                f"<code>│</code>\n"
                f"<code>│</code> <b>{UIFactory.EMOJIS['new']} Welcome Gift:</b> <code>{wg_status}</code>\n"
                f"<code>│</code> <b>Gift Name:</b> <code>{wg_name}</code>\n"
                f"<code>│</code> <b>Gift Prize:</b> <code>{wg_prize if len(wg_prize) < 25 else wg_prize[:25] + '...'}</code>")
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
            InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Panel", callback_data="admin_main_panel"),
            # v16.0: Welcome Gift Buttons
            InlineKeyboardButton(f"{UIFactory.EMOJIS['new']} Toggle Welcome Gift", callback_data="admin_toggle_welcome_gift"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['rename']} Set Gift Name", callback_data="admin_set_welcome_gift_name"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['edit']} Set Gift Prize", callback_data="admin_set_welcome_gift_prize")
        )
        return UIFactory.design_box(title, body, footer), markup

    @staticmethod
    def manage_admins_panel(admin_ids):
        title = f"{UIFactory.EMOJIS['crown']} 𝗠𝗔𝗡𝗔𝗚𝗘 𝗔𝗗𝗠𝗜𝗡𝗦"
        body = (f"<code>│</code> Here you can add or remove other admins.\n"
                f"<code>│</code> <b>To Add:</b> Reply to a user's message with <code>/promote</code>\n"
                f"<code>│</code> <b>To Remove:</b> Reply to an admin's message with <code>/demote</code>\n"
                f"<code>│</code> You can also add manually below.")
        footer = "Owner-Only Access"
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['user']} Add Admin by ID", callback_data="admin_add_admin"))
        if admin_ids:
            body += "\n<code>│</code>\n<code>│</code> <b>Current Admins:</b>"
            for admin_id in admin_ids:
                markup.add(InlineKeyboardButton(f"🚫 Remove {admin_id}", callback_data=f"admin_confirm_remove_admin_{admin_id}"))
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Panel", callback_data="admin_main_panel"))
        return UIFactory.design_box(title, body, footer), markup

    @staticmethod
    def manage_giveaways_panel(giveaways_data):
        title = f"{UIFactory.EMOJIS['list']} 𝗠𝗔𝗡𝗔𝗚𝗘 𝗚𝗜𝗩𝗘𝗔𝗪𝗔𝗬𝗦"
        footer = "Select a giveaway to manage"
        markup = InlineKeyboardMarkup(row_width=1)
        if not giveaways_data or all(gid == WELCOME_GIFT_GID for gid in giveaways_data):
            body = f"<code>│</code> {UIFactory.EMOJIS['error']} No giveaways created yet. Use 'Create Giveaway' to start."
        else:
            body = "<code>│</code> Select a giveaway to add prizes or manage it:\n"
            # v16.0: Filter out system giveaways
            for gid, data in giveaways_data.items():
                if gid == WELCOME_GIFT_GID:
                    continue
                total = len(data['prizes'])
                redeemed = sum(1 for p in data['prizes'].values() if p['redeemed'])
                remaining = total - redeemed
                markup.add(InlineKeyboardButton(f"{escape(data['name'])} ({remaining} left | {redeemed} redeemed)", callback_data=f"admin_view_giveaway_{gid}"))
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Panel", callback_data="admin_main_panel"))
        return UIFactory.design_box(title, body, footer), markup

    @staticmethod
    def giveaway_details_panel(gid, gdata):
        # v18.0: Polished UI
        title = f"{UIFactory.EMOJIS['gift']} 𝗠𝗔𝗡𝗔𝗚𝗘: {escape(gdata['name'])}"
        total = len(gdata['prizes'])
        redeemed = sum(1 for p in gdata['prizes'].values() if p['redeemed'])
        remaining = total - redeemed
        body = (f"<code>│</code> <b>Giveaway ID:</b> <code>{gid}</code>\n"
                f"<code>│</code>\n"
                f"<code>│</code> {UIFactory.EMOJIS['rocket']} <b>Remaining Stock:</b> {remaining}\n"
                f"<code>│</code> {UIFactory.EMOJIS['party']} <b>Total Redeemed:</b> {redeemed}\n"
                f"<code>│</code> {UIFactory.EMOJIS['db']} <b>Total Prizes:</b> {total}\n"
                f"<code>│</code>\n"
                f"<code>│</code> Use the buttons below to manage this giveaway.")
        footer = "Giveaway Management"
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(f"{UIFactory.EMOJIS['plus']} Add Prize", callback_data=f"admin_add_prize_{gid}"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['upload']} Batch Add Prizes", callback_data=f"admin_batch_add_prize_{gid}"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['edit']} View/Edit Prizes", callback_data=f"admin_prize_list_{gid}_0"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['post']} Generate Post", callback_data=f"admin_generate_post_{gid}"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['rename']} Edit Name", callback_data=f"admin_edit_giveaway_name_{gid}"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['clone']} Clone Giveaway", callback_data=f"admin_clone_giveaway_{gid}"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['download']} Export Codes", callback_data=f"admin_export_codes_{gid}"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['stats']} Full Report", callback_data=f"admin_export_full_report_{gid}"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['trash']} Delete Giveaway", callback_data=f"admin_confirm_delete_giveaway_{gid}"),
            InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to List", callback_data="admin_manage_giveaways")
        )
        return UIFactory.design_box(title, body, footer), markup

    @staticmethod
    def prize_list_panel(gid, gdata, page=0):
        # v18.0: Polished UI
        title = f"{UIFactory.EMOJIS['edit']} 𝗘𝗗𝗜𝗧 𝗣𝗥𝗜𝗭𝗘𝗦: {escape(gdata['name'])}"
        footer = "Manage individual prize stock"
        
        prizes = gdata.get('prizes', {})
        if not prizes:
            body = "<code>│</code> This giveaway has no prizes."
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Giveaway", callback_data=f"admin_view_giveaway_{gid}"))
            return UIFactory.design_box(title, body, footer), markup
            
        sorted_prizes = sorted(prizes.items(), key=lambda item: item[1]['redeemed'])
        
        start_index = page * PRIZES_PER_PAGE
        end_index = start_index + PRIZES_PER_PAGE
        prizes_on_page = sorted_prizes[start_index:end_index]
        total_pages = math.ceil(len(sorted_prizes) / PRIZES_PER_PAGE)

        markup = InlineKeyboardMarkup(row_width=2)
        body = f"<code>│</code> Page {page + 1} of {total_pages}. Showing {len(prizes_on_page)} of {len(sorted_prizes)} prizes.\n"
        
        if not prizes_on_page:
             body = "<code>│</code> No prizes on this page."
        
        for code, prize_data in prizes_on_page:
            prize_text_escaped = escape(prize_data['prize_text'])
            code_escaped = escape(code)
            
            body += "<code>│</code>\n"
            if prize_data['redeemed']:
                username_escaped = escape(prize_data.get('redeemed_by_username', 'N/A'))
                body += f"<code>│</code> <s>{code_escaped}</s>\n"
                body += f"<code>│</code> <i>{UIFactory.EMOJIS['user']} Redeemed by @{username_escaped}</i>\n"
                body += f"<code>│</code> {UIFactory.EMOJIS['gift']} <pre>{prize_text_escaped}</pre>"
            else:
                body += f"<code>│</code> <b>{code_escaped}</b>\n"
                body += f"<code>│</code> {UIFactory.EMOJIS['gift']} Prize: <pre>{prize_text_escaped}</pre>"
                markup.add(
                    InlineKeyboardButton(f"{UIFactory.EMOJIS['edit']} Edit", callback_data=f"admin_edit_prize_text_{gid}_{code}"),
                    InlineKeyboardButton(f"{UIFactory.EMOJIS['trash']} Delete", callback_data=f"admin_confirm_delete_prize_{gid}_{code}_{page}") # v16.0: Pass page
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
        return UIFactory.design_box(title, body, footer), markup

    @staticmethod
    def user_manage_panel(user_id, user_data, is_banned):
        if not user_data:
            title = f"{UIFactory.EMOJIS['error']} 𝗨𝗦𝗘𝗥 𝗡𝗢𝗧 𝗙𝗢𝗨𝗡𝗗"
            body = f"<code>│</code> No user found with ID or Username: <code>{escape(user_id)}</code>\n<code>│</code> They must /start the bot first."
            footer = "User Management"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Panel", callback_data="admin_main_panel"))
            return UIFactory.design_box(title, body, footer), markup

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
        
        user_id_from_data = user_data.get('user_id') # v17.0: Get the actual ID from data
        
        title = f"{UIFactory.EMOJIS['users']} 𝗠𝗔𝗡𝗔𝗚𝗘 𝗨𝗦𝗘𝗥: {name}"
        body = (f"<code>│</code> <b>User ID:</b> <code>{user_id_from_data}</code>\n"
                f"<code>│</code> <b>Username:</b> @{username}\n"
                f"<code>│</code> <b>Total Wins:</b> {wins}\n"
                f"<code>│</code> <b>Joined On:</b> {joined_at_str}\n"
                f"<code>│</code> <b>Status:</b> <b>{status}</b>")
        footer = "User Management"
        
        markup = InlineKeyboardMarkup(row_width=1)
        if is_banned:
            markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['unban']} Unban User", callback_data=f"admin_unban_user_{user_id_from_data}"))
        else:
            markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['ban']} Ban User", callback_data=f"admin_confirm_ban_user_{user_id_from_data}"))
            
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Panel", callback_data="admin_main_panel"))
        return UIFactory.design_box(title, body, footer), markup


    @staticmethod
    def stock_success_message(name, prize_text, new_code):
        # v18.0: Polished
        title = f"{UIFactory.EMOJIS['success']} 𝗣𝗥𝗜𝗭𝗘 𝗦𝗧𝗢𝗖𝗞𝗘D!"
        body = (f"<code>│</code> Successfully added 1 new prize to:\n"
                f"<code>│</code> <b>{escape(name)}</b>\n"
                f"<code>│</code>\n"
                f"<code>│</code> <b>Prize Text:</b>\n"
                f"<code>│</code> <pre>{escape(prize_text)}</pre>\n"
                f"<code>│</code>\n"
                f"<code>│</code> <b>Redeem Code:</b>\n"
                f"<code>│</code> <code>{escape(new_code)}</code>\n"
                f"<code>│</code>\n"
                f"<code>│</code> ⬆️ Copy this code and post it in your channel.")
        footer = "Admin Notification"
        return UIFactory.design_box(title, body, footer)
        
    @staticmethod
    def stock_multi_success_message(name, count):
        title = f"{UIFactory.EMOJIS['success']} 𝗕𝗔𝗧𝗖𝗛 𝗦𝗧𝗢𝗖𝗞 𝗦𝗨𝗖𝗖𝗘𝗦𝗦!"
        body = (f"<code>│</code> Successfully stocked <b>{count}</b> new prizes\n"
                f"<code>│</code> from the .txt file for '<b>{escape(name)}</b>'.\n"
                f"<code>│</code>\n"
                f"<code>│</code> Use 'View/Edit Prizes' or 'Generate Post' to see\n"
                f"<code>│</code> the new codes.")
        footer = "Admin Notification"
        return UIFactory.design_box(title, body, footer)


    @staticmethod
    def stats_message(total_users, total_giveaways, total_prizes, total_redeemed, remaining_prizes):
        title = f"{UIFactory.EMOJIS['stats']} 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦"
        body = (f"<code>│</code> <b>{UIFactory.EMOJIS['users']} Total Bot Users:</b> {total_users}\n"
                f"<code>│</code> <b>{UIFactory.EMOJIS['list']} Total Giveaways Created:</b> {total_giveaways}\n"
                f"<code>│</code>\n"
                f"<code>│</code> <b>{UIFactory.EMOJIS['gift']} Total Prizes Stocked:</b> {total_prizes}\n"
                f"<code>│</code> <b>{UIFactory.EMOJIS['party']} Total Prizes Redeemed:</b> {total_redeemed}\n"
                f"<code>│</code> <b>{UIFactory.EMOJIS['rocket']} Prizes Remaining:</b> {remaining_prizes}")
        footer = f"{UIFactory.EMOJIS['clock']} {get_live_time()}"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Panel", callback_data="admin_main_panel"))
        return UIFactory.design_box(title, body, footer), markup

    # v18.0: New UI for Global Stock
    @staticmethod
    def global_stock_message(global_stock_list):
        title = f"{UIFactory.EMOJIS['db']} 𝗚𝗟𝗢𝗕𝗔𝗟 𝗦𝗧𝗢𝗖𝗞 𝗥𝗘𝗣𝗢𝗥𝗧"
        
        if not global_stock_list:
            body = f"<code>│</code> {UIFactory.EMOJIS['success']} All prizes have been redeemed! Stock is empty."
            footer = "Great job!"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Panel", callback_data="admin_main_panel"))
            return UIFactory.design_box(title, body, footer), markup

        body = f"<code>│</code> Here are all <b>{len(global_stock_list)}</b> unredeemed prizes in the bot:\n"
        
        current_gname = ""
        for item in global_stock_list:
            gname = item['gname']
            if gname != current_gname:
                body += f"<code>│</code>\n"
                body += f"<code>│</code> <b>{UIFactory.EMOJIS['gift']} {escape(gname)}</b>\n"
                current_gname = gname
            
            body += f"<code>│</code>   - <code>{escape(item['code'])}</code>\n"
            body += f"<code>│</code>     <pre>{escape(item['prize'])}</pre>\n"

        footer = "Report generated successfully."
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"{UIFactory.EMOJIS['back']} Back to Panel", callback_data="admin_main_panel"))
        return UIFactory.design_box(title, body, footer), markup

# -----------------------------------------------------------------------------------
# 💾 --- DATABASE MANAGEMENT (v18.0) --- 💾
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
                "welcome_gift_enabled": False, # v16.0
                "welcome_gift_name": "Welcome Gift", # v16.0
                "welcome_gift_prize": "✨ Special Welcome Pack ✨", # v17.0: Changed to a logical default
            },
            "giveaways": {},
            "users": {}
        }
        
        if not os.path.exists(DATA_FILE):
            return defaults
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                
            if "settings" not in data: data["settings"] = defaults["settings"]
            if "giveaways" not in data: data["giveaways"] = defaults["giveaways"]
            if "users" not in data: data["users"] = defaults["users"]
                
            for key, value in defaults["settings"].items():
                if key not in data["settings"]:
                    data["settings"][key] = value
                        
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
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"!!! CRITICAL: Failed to save data to {DATA_FILE}: {e} !!!")


# -----------------------------------------------------------------------------------
# 🛠️ --- HELPER FUNCTIONS (v18.0) --- 🛠️
# -----------------------------------------------------------------------------------

def is_owner(user_id):
    """v5.0: Checks if a user is the Owner."""
    return user_id == OWNER_ID

def is_admin(user_id):
    """vG.0: Checks if a user is Owner OR a secondary admin."""
    data = load_data()
    if user_id == OWNER_ID or user_id in data["settings"].get("admin_ids", []):
        return True
    return False

def is_banned(user_id):
    """Checks if a user is in the banned list."""
    if is_admin(user_id):
        return False
    data = load_data()
    return user_id in data["settings"].get("banned_users", [])

def create_prefix(name):
    """Creates a clean, short prefix from a giveaway name."""
    prefix_raw = name.split(' ')[0]
    prefix_clean = re.sub(r'[^A-Z0-9]', '', prefix_raw.upper())
    prefix_limited = prefix_clean[:8]
    if not prefix_limited:
        return "GIFT"
    return prefix_limited

def generate_code(giveaway_name):
    """
    v10.0: Generates a unique gift code based on the giveaway name.
    """
    prefix = create_prefix(giveaway_name)
    random_part_1 = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=4))
    random_part_2 = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=4))
    return f"{prefix}-{random_part_1}-{random_part_2}"

# v18.0: New helper function to check for unique code
def is_code_unique(code_to_check, data):
    """
    v18.0: Checks if a redeem code is unique across ALL giveaways.
    """
    code_upper = code_to_check.upper()
    for gdata in data['giveaways'].values():
        if code_upper in gdata['prizes']:
            return False
    return True

# v16.0: New Function for Welcome Gift
def give_welcome_gift(user, data, settings):
    """
    Automatically creates and redeems a welcome gift for a new user.
    Modifies the `data` object directly.
    """
    try:
        gift_name = settings.get("welcome_gift_name", "Welcome Gift")
        prize_text = settings.get("welcome_gift_prize", "✨ Special Welcome Pack ✨") # v17.0: Updated default
        
        # 1. Find or create the special welcome gift giveaway
        if WELCOME_GIFT_GID not in data["giveaways"]:
            data["giveaways"][WELCOME_GIFT_GID] = {
                "name": "Welcome Gift (System)",
                "created_at": datetime.now(BOT_TIMEZONE).isoformat(),
                "prizes": {}
            }
        
        # 2. Create a unique code for this user
        user_specific_code = f"WELCOME-{user.id}"
        
        # 3. Add this prize to the giveaway
        redeemed_at_time = datetime.now(BOT_TIMEZONE)
        data["giveaways"][WELCOME_GIFT_GID]["prizes"][user_specific_code] = {
            "prize_text": prize_text,
            "redeemed": True,
            "redeemed_by_user_id": user.id,
            "redeemed_by_username": user.username or user.first_name,
            "redeemed_at": redeemed_at_time.isoformat()
        }
        
        # 4. Add the win record to the user
        win_record = {
            "giveaway_name": gift_name,
            "prize_text": prize_text,
            "code": "WELCOME_GIFT",
            "date": redeemed_at_time.strftime("%d-%b-%Y at %I:%M %p %Z")
        }
        data["users"][str(user.id)]["winnings"].append(win_record)
        
        return gift_name
    except Exception as e:
        print(f"Error giving welcome gift: {e}")
        return None

# v17.0: Modified register_user
def register_user(user):
    """
    v17.0: Registers/updates user. Adds 'joined_at' and 'user_id'.
    Calls 'give_welcome_gift' for new users.
    """
    data = load_data()
    user_id_str = str(user.id)
    welcome_gift_awarded_name = None
    
    user_data = data["users"].get(user_id_str)
    
    if not user_data:
        data["users"][user_id_str] = {
            "user_id": user.id, # v17.0: Store the int ID for safety
            "username": user.username,
            "first_name": user.first_name,
            "winnings": [],
            "joined_at": datetime.now(BOT_TIMEZONE).isoformat()
        }
        
        # v16.0: Give Welcome Gift
        settings = data.get("settings", {})
        if settings.get("welcome_gift_enabled", False):
            welcome_gift_awarded_name = give_welcome_gift(user, data, settings)
        
        save_data(data)
    
    elif (user_data.get("username") != user.username or
          user_data.get("first_name") != user.first_name or
          "user_id" not in user_data): # v17.0: Backfill user_id
        
        user_data["username"] = user.username
        user_data["first_name"] = user.first_name
        user_data["user_id"] = user.id # v17.0
        if "joined_at" not in user_data:
             user_data["joined_at"] = datetime.now(BOT_TIMEZONE).isoformat()
        save_data(data)
        
    return welcome_gift_awarded_name # Return name of gift if awarded

def check_membership(user_id):
    """
    Original v6.0 logic.
    """
    if is_admin(user_id):
        return True
        
    data = load_data()
    settings = data["settings"]
    
    if not settings["force_join_enabled"]:
        return True
        
    channel_ok = False
    group_ok = False

    if not settings["force_channel"]:
        channel_ok = True
    else:
        try:
            member = bot.get_chat_member(chat_id=settings["force_channel"], user_id=user_id)
            if member.status in ['member', 'administrator', 'creator']:
                channel_ok = True
        except Exception as e:
            print(f"Error checking channel {settings['force_channel']}: {e}")
            channel_ok = False

    if not settings["force_group"]:
        group_ok = True
    else:
        try:
            member = bot.get_chat_member(chat_id=settings["force_group"], user_id=user_id)
            if member.status in ['member', 'administrator', 'creator']:
                group_ok = True
        except Exception as e:
            print(f"Error checking group {settings['force_group']}: {e}")
            group_ok = False

    return channel_ok and group_ok

def send_branded_message(chat_id, text, reply_markup=None, is_reply=False, reply_to_id=None, image_url=None):
    """
    v13.0: Branded Image System.
    """
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
            
def get_total_redeemed():
    """v5.0: Helper to get total redeemed prizes for public stats."""
    data = load_data()
    total_redeemed = 0
    # v16.0: Use .get to be safe
    for gid, gdata in data.get('giveaways', {}).items():
        total_redeemed += sum(1 for p in gdata.get('prizes', {}).values() if p.get('redeemed'))
    return total_redeemed

def get_active_giveaway_count():
    """Counts giveaways that still have unredeemed prizes."""
    data = load_data()
    active_count = 0
    # v16.0: Use .get to be safe and filter system
    for gid, gdata in data.get('giveaways', {}).items():
        if gid == WELCOME_GIFT_GID:
            continue
        total = len(gdata.get('prizes', {}))
        redeemed = sum(1 for p in gdata.get('prizes', {}).values() if p.get('redeemed'))
        if total > redeemed:
            active_count += 1
    return active_count

# -----------------------------------------------------------------------------------
# 🤖 --- USER COMMAND HANDLERS (v17.0) --- 🤖
# -----------------------------------------------------------------------------------

@bot.message_handler(commands=['start'])
def start_command(message):
    user = message.from_user
    
    if is_banned(user.id):
        bot.reply_to(message, f"🚫 You have been banned from using this bot.")
        return
    
    # v17.0: Register user and check for welcome gift
    welcome_gift_name = register_user(user)
    
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
        
        # v16.0: Pass welcome gift name to UI
        welcome_text, welcome_markup = UIFactory.welcome_message(message.from_user, welcome_gift_name)
        user_welcome_image = settings.get("user_welcome_image_url")
        
        send_branded_message(message.chat.id, welcome_text, reply_markup=welcome_markup, image_url=user_welcome_image)

@bot.message_handler(commands=['redeem'])
def redeem_command(message):
    user = message.from_user

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

    data = load_data()
    
    found_code = False
    for giveaway_id, giveaway_data in data.get('giveaways', {}).items():
        if redeem_code in giveaway_data.get('prizes', {}):
            found_code = True
            prize_data = giveaway_data["prizes"][redeem_code]
            
            if prize_data.get("redeemed", False):
                error_text = UIFactory.error_message(f"This gift code has already been redeemed by @{escape(prize_data.get('redeemed_by_username', 'N/A'))}!")
                bot.reply_to(message, error_text)
                return

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
            data["users"][str(user.id)]["winnings"].append(win_record)
            
            save_data(data)
            
            admin_username = data["settings"].get("admin_username", "the Admin")
            success_text = UIFactory.redeem_success_message(user.first_name, prize_name, prize_text, admin_username, redeem_code)
            send_branded_message(message.chat.id, success_text)
            
            return
            
    if not found_code:
        error_text = UIFactory.error_message("Invalid or expired gift code. Please check the code and try again.")
        bot.reply_to(message, error_text)

@bot.message_handler(commands=['mywinnings'])
def my_winnings_command(message):
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

# -----------------------------------------------------------------------------------
# 💎 --- OWNER: GODMODE COMMANDS (v16.0) --- 💎
# -----------------------------------------------------------------------------------
@bot.message_handler(commands=['promote'])
def owner_promote_command(message):
    if not is_owner(message.from_user.id):
        return

    if not message.reply_to_message:
        bot.reply_to(message, "<b>Owner Command:</b> Reply to a user's message with <code>/promote</code> to make them an admin.")
        return
        
    try:
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
    if not is_owner(message.from_user.id):
        return

    if not message.reply_to_message:
        bot.reply_to(message, "<b>Owner Command:</b> Reply to an admin's message with <code>/demote</code> to remove them.")
        return
        
    try:
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


# -----------------------------------------------------------------------------------
# ✨ --- v10.0: INLINE SHARING HANDLER --- ✨
# -----------------------------------------------------------------------------------
@bot.inline_handler(lambda query: True)
def inline_query_handler(query):
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
            if gid == WELCOME_GIFT_GID:
                continue
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
# 👤 --- USER: BUTTON HANDLERS (v17.0) --- 👤
# -----------------------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith('user_'))
def user_callback_handler(call):
    user = call.from_user
    action = call.data
    chat_id = call.message.chat.id

    if is_banned(user.id):
        bot.answer_callback_query(call.id, "🚫 You are banned from using this bot.", show_alert=True)
        return
    
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
    
    try:
        if action == "user_redeem_prompt":
            prompt_text = UIFactory.prompt_message("Please send your gift code in the format:\n<code>/redeem CODE-XXXX-XXXX</code>")
            bot.send_message(chat_id, prompt_text)
            bot.answer_callback_query(call.id)
        
        elif action == "user_my_winnings":
            data = load_data()
            winnings = data["users"][str(user.id)]["winnings"]
            winnings_text = UIFactory.my_winnings_message(user.first_name, winnings)
            send_branded_message(chat_id, winnings_text)
            bot.answer_callback_query(call.id)
            
        elif action == "user_public_stats":
            data = load_data()
            total_users = len(data.get('users', {}))
            total_redeemed = get_total_redeemed()
            active_giveaways = get_active_giveaway_count()
            
            stats_text = UIFactory.public_stats_message(total_users, total_redeemed, active_giveaways)
            bot.send_message(chat_id, stats_text)
            bot.answer_callback_query(call.id)
            
        # v17.0: Top Winners Leaderboard
        elif action == "user_top_winners":
            data = load_data()
            all_users = list(data.get('users', {}).values())
            
            # Filter out users with no winnings
            winners = [user for user in all_users if user.get('winnings')]
            
            # Sort by win count, descending
            sorted_users = sorted(winners, key=lambda u: len(u.get('winnings', [])), reverse=True)
            
            top_users = sorted_users[:LEADERBOARD_COUNT]
            
            leaderboard_text = UIFactory.top_winners_message(top_users)
            bot.send_message(chat_id, leaderboard_text)
            bot.answer_callback_query(call.id)
            
    except Exception as e:
        print(f"User Callback Error: {e}")
        bot.answer_callback_query(call.id, "An error occurred.")

# -----------------------------------------------------------------------------------
# 🛡️ --- ADMIN: SMART EDIT HELPER (v6.0) --- 🛡️
# -----------------------------------------------------------------------------------

def edit_admin_message(call, new_text, new_markup):
    """
    Original v6.0 logic.
    """
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    try:
        if call.message.content_type == 'photo':
            bot.edit_message_caption(caption=new_text, chat_id=chat_id, message_id=message_id, reply_markup=new_markup)
        else:
            bot.edit_message_text(text=new_text, chat_id=chat_id, message_id=message_id, reply_markup=new_markup)
        
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        print(f"Error editing admin message: {e}")
        if "message to edit not found" in str(e) or "message can't be edited" in str(e):
             data = load_data()
             send_branded_message(chat_id, new_text, reply_markup=new_markup)
             bot.answer_callback_query(call.id, "Panel refreshed.")
        elif "message is not modified" in str(e):
             bot.answer_callback_query(call.id, "Already on this page.")
        else:
            bot.answer_callback_query(call.id, "An error occurred while editing.")

# -----------------------------------------------------------------------------------
# 🛡️ --- ADMIN: PANEL & BUTTON HANDLERS (v18.0) --- 🛡️
# -----------------------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def admin_callback_handler(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Access Denied.")
        return

    action = call.data
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    def send_premium_prompt(text):
        prompt_text = UIFactory.prompt_message(f"{text}<pre>\n\nOr send /cancel to abort.</pre>")
        bot.send_message(chat_id, prompt_text)
        bot.answer_callback_query(call.id)

    try:
        if action == "admin_noop":
            bot.answer_callback_query(call.id, "Current Page")
            return

        # --- Main Panel & Lock ---
        if action == "admin_main_panel":
            panel_text, panel_markup = UIFactory.admin_panel_message(is_owner(user_id))
            edit_admin_message(call, panel_text, panel_markup)

        elif action == "admin_lock_panel":
            panel_text, panel_markup = UIFactory.locked_panel_message()
            edit_admin_message(call, panel_text, panel_markup)

        elif action == "admin_unlock_panel":
            panel_text, panel_markup = UIFactory.admin_panel_message(is_owner(user_id))
            edit_admin_message(call, panel_text, panel_markup)

        # --- Settings Panel ---
        elif action == "admin_settings":
            data = load_data()
            settings_text, settings_markup = UIFactory.settings_panel_message(data["settings"])
            edit_admin_message(call, settings_text, settings_markup)
        
        elif action == "admin_set_channel":
            send_premium_prompt("Please send the channel username (e.g., @YourChannelName).")
            admin_next_step[chat_id] = "set_channel_name"
            
        elif action == "admin_set_group":
            send_premium_prompt("Please send the group username (e.g., @YourGroupName).")
            admin_next_step[chat_id] = "set_group_name"
            
        elif action == "admin_set_admin_user":
            send_premium_prompt("Please send your admin username (e.g., @shuvohassan00).\nThis will be shown to winners.")
            admin_next_step[chat_id] = "set_admin_user"
            
        elif action == "admin_set_welcome_image":
            send_premium_prompt("Please send a direct URL for the <b>Branding Image</b>.\nThis image will be used on all admin panels and bot replies.\nSend 'NONE' to remove the image.")
            admin_next_step[chat_id] = "set_welcome_image"

        elif action == "admin_set_user_welcome_image":
            send_premium_prompt("Please send a direct URL for the <b>User Welcome Image</b>.\nThis will be shown *only* to users on the /start command.\nSend 'NONE' to remove the image.")
            admin_next_step[chat_id] = "set_user_welcome_image"

        elif action == "admin_toggle_forcejoin":
            data = load_data()
            settings = data["settings"]
            if not settings["force_channel"] or not settings["force_group"]:
                bot.answer_callback_query(call.id, "Error: Please set BOTH channel and group first!", show_alert=True)
                return
            
            settings["force_join_enabled"] = not settings["force_join_enabled"]
            save_data(data)
            
            settings_text, settings_markup = UIFactory.settings_panel_message(settings)
            edit_admin_message(call, settings_text, settings_markup)
            status = "ON" if settings['force_join_enabled'] else "OFF"
            bot.answer_callback_query(call.id, f"Force Join turned {status}.")
            
        # --- v16.0: Welcome Gift Settings ---
        elif action == "admin_toggle_welcome_gift":
            data = load_data()
            settings = data["settings"]
            if not settings["welcome_gift_name"] or not settings["welcome_gift_prize"]:
                 bot.answer_callback_query(call.id, "Error: Please set Gift Name and Gift Prize first!", show_alert=True)
                 return
            
            settings["welcome_gift_enabled"] = not settings.get("welcome_gift_enabled", False)
            save_data(data)
            
            settings_text, settings_markup = UIFactory.settings_panel_message(settings)
            edit_admin_message(call, settings_text, settings_markup)
            status = "ON" if settings['welcome_gift_enabled'] else "OFF"
            bot.answer_callback_query(call.id, f"Welcome Gift turned {status}.")

        elif action == "admin_set_welcome_gift_name":
            send_premium_prompt("Please send the <b>Name</b> for the Welcome Gift (e.g., 'Starter Pack').")
            admin_next_step[chat_id] = "set_welcome_gift_name"
            
        elif action == "admin_set_welcome_gift_prize":
            send_premium_prompt("Please send the <b>Prize Text</b> for the Welcome Gift (e.g., '✨ Special Welcome Pack ✨').")
            admin_next_step[chat_id] = "set_welcome_gift_prize"
        # --- End v16.0 Settings ---

        elif action == "admin_check_setup":
            bot.answer_callback_query(call.id, "Checking setup... please wait.")
            data = load_data()
            settings = data["settings"]
            
            channel = settings.get("force_channel")
            group = settings.get("force_group")
            
            if not channel or not group:
                bot.send_message(chat_id, UIFactory.error_message("Please set both Channel and Group usernames first."))
                return

            report = f"<b>{UIFactory.EMOJIS['check']} Setup Check Report (v18.0)</b>\n\n"
            
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
            
            report += "\n<pre>'Ban Users' permission is REQUIRED for Force Join to work.</pre>\n"
            bot.send_message(chat_id, report)

        # --- Admin Management ---
        elif action == "admin_manage_admins":
            if not is_owner(user_id):
                bot.answer_callback_query(call.id, "🚫 Owner-Only Access.", show_alert=True)
                return
            
            data = load_data()
            admin_ids = data["settings"].get("admin_ids", [])
            admin_text, admin_markup = UIFactory.manage_admins_panel(admin_ids)
            edit_admin_message(call, admin_text, admin_markup)

        elif action == "admin_add_admin":
            if not is_owner(user_id):
                bot.answer_callback_query(call.id, "🚫 Owner-Only Access.", show_alert=True)
                return
            send_premium_prompt("Please send the **User ID** of the person you want to make an admin.\n(Or reply <code>/promote</code> to their message).")
            admin_next_step[chat_id] = "add_admin_id"
            
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
            edit_admin_message(call, confirm_text, confirm_markup)

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
                bot.answer_callback_query(call.id, f"✅ Admin {admin_id_to_remove} has been removed.")
            else:
                bot.answer_callback_query(call.id, "Error: Admin not found.")
                
            admin_text, admin_markup = UIFactory.manage_admins_panel(data["settings"].get("admin_ids", []))
            edit_admin_message(call, admin_text, admin_markup)

        # --- User Management (v17.0) ---
        elif action == "admin_user_manage":
            # v17.0: Updated prompt
            send_premium_prompt(f"{UIFactory.EMOJIS['users']} <b>User Management</b>\n\nPlease send the <b>User ID</b> (e.g., <code>12345678</code>) or <b>Username</b> (e.g., <code>@shuvohassan00</code>) of the person you want to manage.")
            admin_next_step[chat_id] = "user_manage_check"

        elif action.startswith("admin_confirm_ban_user_"):
            user_to_ban_id = int(action.split('_')[-1])
            confirm_text, confirm_markup = UIFactory.confirmation_message(
                f"BAN user {user_to_ban_id}",
                callback_yes=f"admin_do_ban_user_{user_to_ban_id}",
                callback_no=f"admin_user_manage_refresh_{user_to_ban_id}" # Refresh by ID
            )
            edit_admin_message(call, confirm_text, confirm_markup)
            
        elif action.startswith("admin_do_ban_user_"):
            user_to_ban_id = int(action.split('_')[-1])
            
            if user_to_ban_id == OWNER_ID or user_to_ban_id in load_data()["settings"]["admin_ids"]:
                bot.answer_callback_query(call.id, "🚫 You cannot ban an Admin or the Owner.", show_alert=True)
                return
            
            data = load_data()
            if user_to_ban_id not in data["settings"]["banned_users"]:
                data["settings"]["banned_users"].append(user_to_ban_id)
                save_data(data)
                bot.answer_callback_query(call.id, f"✅ User {user_to_ban_id} has been BANNED.")
            
            user_data = data.get("users", {}).get(str(user_to_ban_id))
            panel_text, panel_markup = UIFactory.user_manage_panel(user_to_ban_id, user_data, is_banned=True)
            edit_admin_message(call, panel_text, panel_markup)
            
        elif action.startswith("admin_unban_user_"):
            user_to_unban_id = int(action.split('_')[-1])
            data = load_data()
            if user_to_unban_id in data["settings"]["banned_users"]:
                data["settings"]["banned_users"].remove(user_to_unban_id)
                save_data(data)
                bot.answer_callback_query(call.id, f"✅ User {user_to_unban_id} has been UNBANNED.")
            
            user_data = data.get("users", {}).get(str(user_to_unban_id))
            panel_text, panel_markup = UIFactory.user_manage_panel(user_to_unban_id, user_data, is_banned=False)
            edit_admin_message(call, panel_text, panel_markup)
            
        elif action.startswith("admin_user_manage_refresh_"):
            user_to_refresh_id = int(action.split('_')[-1]) # Always refers to ID
            data = load_data()
            user_data = data.get("users", {}).get(str(user_to_refresh_id))
            is_banned = user_to_refresh_id in data["settings"].get("banned_users", [])
            panel_text, panel_markup = UIFactory.user_manage_panel(user_to_refresh_id, user_data, is_banned)
            edit_admin_message(call, panel_text, panel_markup)


        # --- Giveaway Management ---
        elif action == "admin_create_giveaway":
            send_premium_prompt("Please send the name for the new giveaway (e.g., 'Netflix Premium Account').")
            admin_next_step[chat_id] = "create_giveaway_name"

        elif action == "admin_manage_giveaways":
            data = load_data()
            list_text, list_markup = UIFactory.manage_giveaways_panel(data["giveaways"])
            edit_admin_message(call, list_text, list_markup)

        elif action.startswith("admin_view_giveaway_"):
            gid = action.split('_')[-1]
            data = load_data()
            if gid not in data["giveaways"]:
                bot.answer_callback_query(call.id, "Error: This giveaway was deleted.", show_alert=True)
                list_text, list_markup = UIFactory.manage_giveaways_panel(data["giveaways"])
                edit_admin_message(call, list_text, list_markup)
                return
            gdata = data["giveaways"][gid]
            manage_text, manage_markup = UIFactory.giveaway_details_panel(gid, gdata)
            edit_admin_message(call, manage_text, manage_markup)

        # v18.0: New "Add Prize" Flow
        elif action.startswith("admin_add_prize_"):
            gid = action.split('_')[-1]
            data = load_data()
            giveaway_name = data["giveaways"].get(gid, {}).get("name", "Unknown Giveaway")
            send_premium_prompt(f"<b>Step 1/2: Prize Text</b>\nReady to add a prize to <b>{escape(giveaway_name)}</b>.\n\nPlease send the prize text (e.g., <code>user@pass.com</code>).\n\n<b>Note:</b> The *entire message* will be a single prize, even if it has multiple lines.")
            admin_next_step[chat_id] = f"add_prize_text_{gid}"
            
        elif action.startswith("admin_batch_add_prize_"):
            gid = action.split('_')[-1]
            data = load_data()
            giveaway_name = data["giveaways"].get(gid, {}).get("name", "Unknown Giveaway")
            send_premium_prompt(f"{UIFactory.EMOJIS['upload']} <b>Batch Upload to {escape(giveaway_name)}</b>\n\nPlease upload a <code>.txt</code> file.\nEach line of the file should contain one prize text.")
            admin_next_step[chat_id] = f"batch_add_prize_{gid}"
            
        elif action.startswith("admin_edit_giveaway_name_"):
            gid = action.split('_')[-1]
            data = load_data()
            giveaway_name = data["giveaways"].get(gid, {}).get("name", "Unknown Giveaway")
            send_premium_prompt(f"Ready to edit name for <b>{escape(giveaway_name)}</b>.\n\nPlease send the new name.")
            admin_next_step[chat_id] = f"edit_giveaway_name_{gid}"
            
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
            
            bot.answer_callback_query(call.id, "Cloning... this may take a moment.")
            
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
                # v18.0: Use the new unique checker
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
            edit_admin_message(call, list_text, list_markup)

        # v18.0: CRITICAL BUG FIX
        elif action.startswith("admin_prize_list_"):
            parts = action.split('_')
            # [0: 'admin', 1: 'prize', 2: 'list', 3: 'd6a2a9', 4: '0']
            gid = parts[3]  # <--- FIXED (was parts[2])
            page = int(parts[4]) # <--- FIXED (was int(parts[3]))
            
            data = load_data()
            if gid not in data["giveaways"]:
                bot.answer_callback_query(call.id, "Error: Giveaway not found.", show_alert=True)
                return
            
            gdata = data["giveaways"][gid]
            panel_text, panel_markup = UIFactory.prize_list_panel(gid, gdata, page)
            edit_admin_message(call, panel_text, panel_markup)
            
        # v16.0: BUG FIX (Edit Prize)
        elif action.startswith("admin_edit_prize_text_"):
            parts = action.split('_')
            gid = parts[4]
            code = "_".join(parts[5:]) # Join all remaining parts
            data = load_data()
            prize_text = data["giveaways"][gid]["prizes"][code]["prize_text"]
            send_premium_prompt(f"Ready to edit prize text for code <code>{escape(code)}</code>.\n\nThe current text is:\n<pre>{escape(prize_text)}</pre>\n\nPlease send the new prize text.")
            admin_next_step[chat_id] = f"edit_prize_text_{gid}_{code}"
            
        # v16.0: BUG FIX (Confirm Delete Prize)
        elif action.startswith("admin_confirm_delete_prize_"):
            parts = action.split('_')
            gid = parts[4]
            page = int(parts[-1])
            code = "_".join(parts[5:-1]) # Join all middle parts
            
            confirm_text, confirm_markup = UIFactory.confirmation_message(
                f"delete prize code {escape(code)}",
                callback_yes=f"admin_do_delete_prize_{gid}_{code}_{page}",
                callback_no=f"admin_prize_list_{gid}_{page}"
            )
            edit_admin_message(call, confirm_text, confirm_markup)
            
        # v16.0: BUG FIX (Do Delete Prize)
        elif action.startswith("admin_do_delete_prize_"):
            parts = action.split('_')
            gid = parts[4]
            page = int(parts[-1])
            code = "_".join(parts[5:-1]) # Join all middle parts
            
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
            bot.answer_callback_query(call.id, f"✅ Prize {escape(code)} deleted.")
            
            gdata = data["giveaways"][gid]
            # Recalculate total pages
            total_prizes = len(gdata.get('prizes', {}))
            total_pages = math.ceil(total_prizes / PRIZES_PER_PAGE) if total_prizes > 0 else 1
            if page >= total_pages and page > 0:
                page -= 1 # Go back one page if last item was deleted

            panel_text, panel_markup = UIFactory.prize_list_panel(gid, gdata, page)
            edit_admin_message(call, panel_text, panel_markup)


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
            bot.answer_callback_query(call.id)
            
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
            bot.answer_callback_query(call.id)

        elif action.startswith("admin_generate_post_"):
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

            send_premium_prompt(f"<b>Step 1/3: Post Image</b>\n\nPlease send a direct URL for the post image (e.g., <code>https://i.imgur.com/image.png</code>).\n\nOr send <code>skip</code> if you don't want an image.")
            admin_next_step[chat_id] = f"generate_post_image_{gid}"

        elif action.startswith("admin_confirm_delete_giveaway_"):
            gid = action.split('_')[-1]
            gdata = load_data().get("giveaways", {}).get(gid)
            gname = gdata['name'] if gdata else "DELETED"
            
            confirm_text, confirm_markup = UIFactory.confirmation_message(
                f"DELETE the giveaway '{escape(gname)}' (ID: {gid})",
                callback_yes=f"admin_do_delete_giveaway_{gid}",
                callback_no=f"admin_view_giveaway_{gid}" if gdata else "admin_manage_giveaways"
            )
            edit_admin_message(call, confirm_text, confirm_markup)
            
        elif action.startswith("admin_do_delete_giveaway_"):
            gid = action.split('_')[-1]
            data = load_data()
            if gid in data["giveaways"]:
                deleted_name = data["giveaways"].pop(gid)
                save_data(data)
                bot.answer_callback_query(call.id, f"✅ Giveaway '{escape(deleted_name['name'])}' deleted.")
            else:
                bot.answer_callback_query(call.id, "Error: Giveaway already deleted.")
                
            list_text, list_markup = UIFactory.manage_giveaways_panel(data["giveaways"])
            edit_admin_message(call, list_text, list_markup)

        # --- Broadcast & Stats & Global Stock ---
        elif action == "admin_broadcast":
            send_premium_prompt("<b>Step 1/2: Broadcast Message</b>\n\nPlease send the message you want to broadcast to all users.\n(Supports HTML formatting).")
            admin_next_step[chat_id] = "broadcast_message"

        # v18.0: New Global Stock Report
        elif action == "admin_global_stock":
            bot.answer_callback_query(call.id, "Generating global report...")
            data = load_data()
            global_stock = []
            
            # Sort giveaways by name first
            sorted_giveaways = sorted(data.get('giveaways', {}).items(), key=lambda item: item[1]['name'])
            
            for gid, gdata in sorted_giveaways:
                if gid == WELCOME_GIFT_GID:
                    continue
                gname = gdata['name']
                # Sort prizes by code
                sorted_prizes = sorted(gdata.get('prizes', {}).items())
                
                for code, prize in sorted_prizes:
                    if not prize.get('redeemed', False):
                        global_stock.append({'gname': gname, 'code': code, 'prize': prize['prize_text']})

            stock_text, stock_markup = UIFactory.global_stock_message(global_stock)
            # Send as a new message, don't edit the panel
            bot.send_message(chat_id, stock_text, reply_markup=stock_markup)

        # v16.0: BUG FIX (Statistics)
        elif action == "admin_stats":
            data = load_data()
            total_users = len(data.get('users', {}))
            
            all_giveaways = data.get('giveaways', {})
            # Filter out system giveaways from stats
            user_giveaways = {gid: gdata for gid, gdata in all_giveaways.items() if gid != WELCOME_GIFT_GID}
            
            total_giveaways = len(user_giveaways)
            
            total_prizes, total_redeemed = 0, 0
            for gid, gdata in all_giveaways.items(): # Count all prizes, even system
                try:
                    total_prizes += len(gdata.get('prizes', {}))
                    total_redeemed += sum(1 for p in gdata.get('prizes', {}).values() if p.get('redeemed'))
                except Exception as e:
                    print(f"Error counting stats for GID {gid}: {e}")
            
            remaining_prizes = total_prizes - total_redeemed
            
            stats_text, stats_markup = UIFactory.stats_message(total_users, total_giveaways, total_prizes, total_redeemed, remaining_prizes)
            edit_admin_message(call, stats_text, stats_markup)

    except Exception as e:
        print(f"Callback Error: {e}")
        bot.answer_callback_query(call.id, "An error occurred.")

# -----------------------------------------------------------------------------------
# 🛡️ --- ADMIN: NEXT STEP HANDLERS (v18.0) --- 🛡️
# -----------------------------------------------------------------------------------
@bot.message_handler(
    func=lambda message: admin_next_step.get(message.chat.id) is not None and is_admin(message.from_user.id),
    content_types=['text', 'document']
)
def admin_input_handler(message):
    chat_id = message.chat.id
    step = admin_next_step.get(chat_id) 
    text_input = message.text

    if text_input == "/cancel":
        # v18.0: Clear any pending prize text
        admin_next_step.pop(f"{chat_id}_prize_text", None)
        if step in admin_next_step:
            admin_next_step.pop(chat_id)
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
                admin_next_step.pop(chat_id)
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
                    # v18.0: Use new unique checker
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
             
        step = admin_next_step.pop(chat_id)
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
                data["settings"]["welcome_image_url"] = "NONE" # v17.0: Store "NONE" explicitly
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
                data["settings"]["user_welcome_image_url"] = "NONE" # v17.0: Store "NONE" explicitly
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
                
        # --- v16.0: Welcome Gift ---
        elif step == "set_welcome_gift_name":
            data = load_data()
            data["settings"]["welcome_gift_name"] = text_input
            save_data(data)
            send_premium_reply(f"Welcome Gift Name set to <b>{escape(text_input)}</b>.")
        
        elif step == "set_welcome_gift_prize":
            data = load_data()
            data["settings"]["welcome_gift_prize"] = text_input
            save_data(data)
            send_premium_reply(f"Welcome Gift Prize set to <b>{escape(text_input)}</b>.")
        # --- End v16.0 ---
                
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

        # v17.0: Updated User Management Logic
        elif step == "user_manage_check":
            user_to_check_id = None
            user_data = None
            data = load_data()
            
            if text_input.startswith('@'):
                # Search by Username
                target_username = text_input[1:].lower()
                for uid_str, udata in data.get("users", {}).items():
                    if udata.get('username', '').lower() == target_username:
                        user_to_check_id = int(uid_str) # Get the ID
                        user_data = udata
                        break
            else:
                # Search by ID
                try:
                    user_to_check_id = int(text_input)
                    user_data = data.get("users", {}).get(str(user_to_check_id))
                except ValueError:
                    send_premium_error("Invalid input. Please send a numerical User ID or an @username. Action cancelled.")
                    return
                except Exception as e:
                    send_premium_error(f"An error occurred: {escape(e)}")
                    return
            
            # Now, show the panel
            if user_data and user_to_check_id:
                user_is_banned = user_to_check_id in data.get("settings", {}).get("banned_users", [])
                # Pass the actual ID for the panel
                panel_text, panel_markup = UIFactory.user_manage_panel(user_to_check_id, user_data, user_is_banned)
            else:
                # Pass the original input text to the error message
                panel_text, panel_markup = UIFactory.user_manage_panel(text_input, None, is_banned=False)
                
            send_branded_message(chat_id, panel_text, reply_markup=panel_markup)


        elif step == "create_giveaway_name":
            giveaway_name = text_input
            data = load_data()
            giveaway_id = str(uuid.uuid4())[:6]
            data["giveaways"][giveaway_id] = {"name": giveaway_name, "created_at": datetime.now(BOT_TIMEZONE).isoformat(), "prizes": {}}
            save_data(data)
            send_premium_reply(f"Giveaway '<b>{escape(giveaway_name)}</b>' created with ID: <code>{giveaway_id}</code>\n\nYou can now manage it from the panel.")

        # v18.0: New "Add Prize" 2-step flow
        elif step.startswith("add_prize_text_"):
            gid = step.split('_')[-1]
            prize_text = message.text # Get raw text, not stripped
            
            admin_next_step[f"{chat_id}_prize_text"] = prize_text
            admin_next_step[chat_id] = f"add_prize_code_{gid}"
            send_premium_prompt(f"<b>Step 2/2: Redeem Code</b>\nPrize text set to:\n<pre>{escape(prize_text)}</pre>\n\nPlease send the <b>Redeem Code</b> for this prize (e.g., <code>MY-CUSTOM-CODE-123</code>).\n\nOr send <code>auto</code> to generate one automatically.")

        elif step.startswith("add_prize_code_"):
            gid = step.split('_')[-1]
            prize_text = admin_next_step.pop(f"{chat_id}_prize_text", None)
            redeem_code = text_input.strip().upper()
            
            if not prize_text:
                send_premium_error("An error occurred (prize text was lost). Please start over.")
                return
            
            data = load_data()
            if gid not in data["giveaways"]:
                send_premium_error("Giveaway ID not found. Action cancelled.")
                return
                
            giveaway_name = data["giveaways"][gid]["name"]
            
            if redeem_code == 'AUTO':
                new_code = generate_code(giveaway_name)
                while not is_code_unique(new_code, data):
                    new_code = generate_code(giveaway_name)
            else:
                new_code = redeem_code
                if not is_code_unique(new_code, data):
                    send_premium_error("This code is already in use in another giveaway. Please send a different code.")
                    # Reset the step so they can try again
                    admin_next_step[f"{chat_id}_prize_text"] = prize_text
                    admin_next_step[chat_id] = f"add_prize_code_{gid}"
                    return
            
            data["giveaways"][gid]["prizes"][new_code] = {
                "prize_text": prize_text, "redeemed": False, "redeemed_by_user_id": None,
                "redeemed_by_username": None, "redeemed_at": None
            }
            save_data(data)
            
            bot.reply_to(message, UIFactory.stock_success_message(giveaway_name, prize_text, new_code))
        # --- End v18.0 Flow ---

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

        # v16.0: BUG FIX (Edit Prize)
        elif step.startswith("edit_prize_text_"):
            parts = step.split('_')
            gid = parts[3]
            code = "_".join(parts[4:]) # Join all remaining parts
            new_prize_text = message.text
            
            data = load_data()
            if gid not in data["giveaways"] or code not in data["giveaways"][gid]["prizes"]:
                send_premium_error("Prize or Giveaway not found. Action cancelled.")
                return
            
            data["giveaways"][gid]["prizes"][code]["prize_text"] = new_prize_text
            save_data(data)
            send_premium_reply(f"Prize text for code <code>{escape(code)}</code> has been updated.")

        elif step.startswith("generate_post_image_"):
            gid = step.split('_')[-1]
            image_url = text_input
            
            if image_url.upper() == 'SKIP':
                image_url = 'NONE'
            elif not re.match(URL_REGEX, image_url):
                send_premium_error("Invalid URL. Action cancelled. Please start over.")
                return
            
            data = load_data()
            gdata = data["giveaways"][gid]
            unredeemed_codes = [code for code, prize in gdata["prizes"].items() if not prize["redeemed"]]
            max_codes = len(unredeemed_codes)
            
            if max_codes == 0:
                send_premium_error("This giveaway has no unredeemed codes left. Action cancelled.")
                return

            send_premium_prompt(f"<b>Step 2/3: Code Count</b>\n\nImage set. Now, <b>how many codes</b> do you want to include in this post?\n\n(Send a number, e.g., <code>10</code>)\nYou have <b>{max_codes}</b> unredeemed codes available.")
            admin_next_step[chat_id] = f"generate_post_count_{gid}_{image_url}"

        elif step.startswith("generate_post_count_"):
            parts = step.split('_')
            gid = parts[3]
            image_url = "_".join(parts[4:]) # Re-join URL parts
            
            try:
                code_count_to_post = int(text_input)
                if code_count_to_post <= 0:
                    send_premium_error("Invalid number. Please send a number greater than 0. Action cancelled.")
                    return
            except ValueError:
                send_premium_error("Invalid input. Please send only a number. Action cancelled.")
                return
            
            send_premium_prompt(f"<b>Step 3/3: Custom Button</b>\n\nGreat. Now, do you want to add a custom button to the post?\n\nPlease send the <b>Button Text</b> and <b>URL</b> separated by a <code>|</code> pipe.\n\n<b>Example:</b>\n<code>Join Our Channel | https://t.me/mychannel</code>\n\nOr send <code>skip</code> for no button.")
            admin_next_step[chat_id] = f"generate_post_button_{gid}_{image_url}_{code_count_to_post}"

        elif step.startswith("generate_post_button_"):
            parts = step.split('_')
            gid = parts[3]
            image_url = parts[4]
            count = int(parts[5])
            button_input = text_input
            
            post_markup = None
            if button_input.upper() != 'SKIP':
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

            data = load_data()
            if gid not in data["giveaways"]:
                send_premium_error("Giveaway ID not found. Action cancelled.")
                return
            
            gdata = data["giveaways"][gid]
            unredeemed_codes = [code for code, prize in gdata["prizes"].items() if not prize["redeemed"]]
            
            if not unredeemed_codes:
                send_premium_error("No unredeemed codes left. Action cancelled.")
                return
            
            if count > len(unredeemed_codes):
                bot.send_message(chat_id, f"⚠️ Warning: You asked for {count} codes, but only {len(unredeemed_codes)} are available. Posting all available codes.")
                count = len(unredeemed_codes)
                
            codes_to_post_list = unredeemed_codes[:count]
            
            bot_username = bot.get_me().username
            giveaway_name = gdata["name"]
            
            post_text, post_markup = UIFactory.generate_giveaway_post(giveaway_name, count, codes_to_post_list, bot_username, post_markup)
            
            if image_url != 'NONE':
                try:
                    bot.send_photo(chat_id, image_url)
                except Exception as e:
                    bot.send_message(chat_id, f"Could not send image URL: {escape(e)}. Sending text post only.")
            
            bot.send_message(chat_id, post_text, reply_markup=post_markup)
            send_premium_reply("<b>Post Generated!</b> ⬆️\n(You can copy the message above and paste it in your channel)")

        elif step == "broadcast_message":
            broadcast_text = message.text # Get raw text with HTML
            send_premium_prompt("<b>Step 2/2: Broadcast Image</b>\n\nMessage text set. Now, please send a direct URL for an image to attach.\n\nOr send <code>skip</code> to send text-only.")
            admin_next_step[chat_id] = "broadcast_image"
            admin_next_step[f"{chat_id}_broadcast_text"] = broadcast_text

        elif step == "broadcast_image":
            broadcast_text = admin_next_step.pop(f"{chat_id}_broadcast_text", "Error: Message not found.")
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

            for user_id_str in user_ids:
                user_id = int(user_id_str)
                if is_admin(user_id) or user_id in banned_users:
                    skipped += 1
                    continue
                try:
                    if use_image:
                        bot.send_photo(user_id, image_url, caption=broadcast_text)
                    else:
                        bot.send_message(user_id, broadcast_text)
                    sent += 1
                except Exception as e:
                    failed += 1
                    print(f"Broadcast failed for {user_id}: {e}")
                time.sleep(0.1) # 10 messages per second
                
            bot.send_message(chat_id, f"<b>Broadcast Complete!</b>\n{UIFactory.EMOJIS['success']} Sent to {sent} users.\n{UIFactory.EMOJIS['error']} Failed for {failed} users.\n{UIFactory.EMOJIS['warn']} Skipped {skipped} (Admins/Banned).")

    except Exception as e:
        if chat_id in admin_next_step:
             admin_next_step.pop(chat_id)
        # v18.0: Clear pending prize text on error
        admin_next_step.pop(f"{chat_id}_prize_text", None)
        send_premium_error(f"An unknown error occurred: <pre>{escape(e)}</pre>")
        print(f"Admin Input Handler Error: {e}")


# -----------------------------------------------------------------------------------
# 🚀 --- BOT LAUNCH --- 🚀
# -----------------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"👑 {UIFactory.EMOJIS['crown']} 𝗚𝗔𝗗𝗚𝗘𝗧 𝗚𝗜𝗩𝗘𝗔𝗪𝗔𝗬 𝗕𝗢𝗧 𝗛𝗨𝗕 (v18.0 - 'Bug-Smasher' Build) is now online...")
    bot.set_my_commands([
        BotCommand("start", "🚀 Start the Bot / Admin Panel"),
        BotCommand("redeem", "🎟️ Redeem a Gift Code"),
        BotCommand("mywinnings", "🎁 Show My Winnings")
    ])
    bot.polling(non_stop=True)