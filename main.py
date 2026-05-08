import base64
from urllib.parse import quote
import re
import json
import os
import cv2
import numpy as np
import ddddocr
from bs4 import BeautifulSoup
from curl_cffi import requests as cffi_requests
from altcha import Challenge, Payload, solve_challenge

BOT_TOKEN = "YOUR TELEGRAM BOT TOKEN"

MAHASISWA_REDIRECT_B64 = base64.b64encode(b"https://mahasiswa.udb.ac.id/").decode("ascii")
AUTH_PAGE_URL = f"https://auth.sso.udb.ac.id/?url={quote(MAHASISWA_REDIRECT_B64, safe='')}"
AUTH_LOGIN_URL = f"{AUTH_PAGE_URL}#"

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

def create_session(cookies=None, headers=None):
    session = cffi_requests.Session()
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://auth.sso.udb.ac.id',
        'Sec-GPC': '1',
        'Connection': 'keep-alive',
        'Referer': AUTH_PAGE_URL,
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Priority': 'u=0, i',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }
    if headers:
        session.headers.update(headers)
    else:
        session.headers.update(default_headers)
        
    if cookies:
        session.cookies.update(cookies)
    return session

def get_user_session(chat_id):
    data = load_data()
    user_data = data.get(str(chat_id), {})
    cookies = user_data.get("cookies", None)
    headers = user_data.get("headers", None)
    return create_session(cookies, headers)

def save_user_session(chat_id, session, user_info=None):
    data = load_data()
    cid = str(chat_id)
    if cid not in data:
        data[cid] = {}
        data[cid]["id_telegram"] = cid
    
    if user_info:
        for k, v in user_info.items():
            data[cid][k] = v
            
    data[cid]["cookies"] = dict(session.cookies)
    data[cid]["headers"] = dict(session.headers)
    save_data(data)

# ─── CAPTCHA FUNCTION ─────────────────────────────────────────

def captcha(session):
    response = session.get(AUTH_PAGE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    token = soup.find('input', {'id': 'token'})['value']
    image_src = soup.find('img', {'id': 'captcha'})['src']
    return token, image_src


def build_sopingi_token(session):
    """ALTCHA PoW: GET /captcha/challenge lalu kirim hasil sebagai sopingi_token saat login."""
    r = session.get(
        "https://auth.sso.udb.ac.id/captcha/challenge",
        headers={
            "Accept": "*/*",
            "Referer": AUTH_PAGE_URL,
        },
    )
    r.raise_for_status()
    ch = Challenge.from_dict(r.json())
    sol = solve_challenge(ch, timeout=120.0)
    if sol is None:
        raise RuntimeError("Gagal menyelesaikan verifikasi ALTCHA (timeout).")
    return Payload(ch, sol).to_base64()

def save_captcha_image(image_src, filename="captcha.png"):
    if "," in image_src:
        image_src = image_src.split(",", 1)[1]
    image_bytes = base64.b64decode(image_src)
    with open(filename, "wb") as f:
        f.write(image_bytes)

def remove_red_color(input_path="captcha.png", output_path="captcha_clean.png"):
    """
    Hanya menghapus merah muda (arsiran, border). Merah tua (digit captcha) dipertahankan.
    Menggabungkan jarak kanal BGR (pastel) + profil HSV untuk pink/arsiran terang.
    """
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Tidak dapat membaca gambar: {input_path}")

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    b, g, r = cv2.split(img)
    r_i = r.astype(np.int32)
    g_i = g.astype(np.int32)
    b_i = b.astype(np.int32)
    h_ch, s_ch, v_ch = cv2.split(hsv)

    lower_red1 = np.array([0, 15, 30])
    upper_red1 = np.array([22, 255, 255])
    lower_red2 = np.array([158, 15, 30])
    upper_red2 = np.array([180, 255, 255])
    mask_hue = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)

    dg = r_i - g_i
    db = r_i - b_i

    pastel = (
        (r_i > 55)
        & (r_i >= g_i)
        & (r_i >= b_i)
        & (dg < 52)
        & (db < 52)
        & (v_ch > 168)
    )

    pink_hsv = (mask_hue > 0) & (s_ch > 28) & (s_ch < 145) & (v_ch > 158)

    washed = (mask_hue > 0) & (s_ch < 105) & (v_ch > 135)

    remove = ((mask_hue > 0) & pastel) | pink_hsv | washed
    remove = (remove.astype(np.uint8)) * 255
    remove = cv2.morphologyEx(remove, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))

    keep = cv2.bitwise_not(remove)
    result = cv2.bitwise_and(img, img, mask=keep)

    white_bg = np.ones_like(img, dtype=np.uint8) * 255
    final = np.where(result == 0, white_bg, result)

    cv2.imwrite(output_path, final)

# ─── LOGIN FUNCTION ─────────────────────────────────────────

def login(session, username, password, token, captcha_text, sopingi_token):
    data = {
        'url': MAHASISWA_REDIRECT_B64,
        'timezone': '',
        'skin': 'bootstrap',
        'token': token,
        'user': username,
        'password': password,
        'captcha': captcha_text,
        'sopingi_token': sopingi_token,
    }

    response = session.post(AUTH_LOGIN_URL, data=data, allow_redirects=False)
    print("Status code login:", response.status_code)

    cookies_dict = dict(session.cookies)
    return response, cookies_dict

def afterlogin(session):
    response = session.get('https://mahasiswa.udb.ac.id/')
    print(f"Status code afterlogin: {response.status_code}")
    return response

def dashboard(session):
    response = session.get('https://mahasiswa.udb.ac.id/dashboard')
    print(f"Status code dashboard: {response.status_code}")
    print(f"Response Dashboard: {response.text}")
    return response.status_code

def angket(session):
    response = session.get('https://mahasiswa.udb.ac.id/adaangket')
    print(f"Status code angket: {response.status_code}")
    try:
        return str(response.json())
    except Exception:
        return f"Gagal parse JSON. Respons:\n{response.text[:500]}"

def bio(session):
    response = session.get('https://mahasiswa.udb.ac.id/mahasiswa')
    print(f"Status code bio: {response.status_code}")
    try:
        data = response.json()
        keys_to_extract = [
            "nim", "nama", "nm_lemb", "kode_fakultas", "kode_prodi", "kelas", "nisn", "nik",
            "tmpt_lahir", "tgl_lahir", "jln", "rt", "rw", "nm_dsn",
            "ds_kel", "kode_pos", "telepon_rumah", "telepon_seluler",
            "email", "nm_ayah", "tgl_lahir_ayah", "nm_ibu_kandung",
            "tgl_lahir_ibu"
        ]
        out  = "========================================\n"
        out += "            BIODATA MAHASISWA\n"
        out += "========================================\n"
        for key in keys_to_extract:
            val = data.get(key)
            if val is None or val == "":
                val = "-"
            out += f"{key.ljust(18)} : {val}\n"
        out += "========================================"
        return out
    except Exception:
        return f"Gagal parse JSON. Respons:\n{response.text[:500]}"

def cek_angket(session):
    response = session.get('https://mahasiswa.udb.ac.id/adaangket')
    print(f"Status code cek_angket: {response.status_code}")
    try:
        return str(response.json())
    except Exception:
        return f"Gagal parse JSON. Respons:\n{response.text[:500]}"

# ─── TELEGRAM HANDLER ─────────────────────────────────────────

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

USERNAME, PASSWORD = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text("Mengambil captcha...")

    ocr = ddddocr.DdddOcr(show_ad=False)
    session = create_session()

    while True:
        token, image_src = captcha(session)
        save_captcha_image(image_src)
        remove_red_color("captcha.png", "captcha_clean.png")

        with open("captcha_clean.png", "rb") as f:
            img_bytes = f.read()
        captcha_text = ocr.classification(img_bytes)
        captcha_text = ''.join(filter(str.isdigit, captcha_text))

        if len(captcha_text) == 5:
            break

    save_user_session(chat_id, session)

    context.user_data['token'] = token
    context.user_data['captcha'] = captcha_text

    await update.message.reply_photo(
        photo=open("captcha_clean.png", "rb"),
        caption=f"Captcha berhasil dibaca: {captcha_text}\n\n👤 Masukkan username (NIM):",
        read_timeout=60,
        write_timeout=60
    )

    return USERNAME

async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['username'] = update.message.text
    await update.message.reply_text("Masukkan password:")
    return PASSWORD

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    context.user_data['password'] = update.message.text

    username   = context.user_data['username']
    password   = context.user_data['password']
    token      = context.user_data['token']
    captcha_r  = context.user_data['captcha']

    session = get_user_session(chat_id)
    await update.message.reply_text("Memverifikasi tantangan keamanan (ALTCHA)...")

    try:
        sopingi_token = build_sopingi_token(session)
        await update.message.reply_text("Mencoba login...")
        res, cookies_dict = login(session, username, password, token, captcha_r, sopingi_token)

        if '<form action="/notifback"' in res.text:
            soup = BeautifulSoup(res.text, 'html.parser')
            form = soup.find('form', {'action': '/notifback'})
            if form:
                notif_data = {}
                for input_tag in form.find_all('input', type='hidden'):
                    notif_data[input_tag.get('name')] = input_tag.get('value', '')
                res = session.post('https://auth.sso.udb.ac.id/notifback', data=notif_data, allow_redirects=True)

        udb_sopingi = dict(session.cookies).get("udb_sopingi")
        if udb_sopingi:
            res_afterlogin = afterlogin(session)

            udb_sopingi = dict(session.cookies).get("udb_sopingi")
            if udb_sopingi:
                sso_token_match = re.search(r'let token\s*=\s*["\']([^"\']+)["\']', res_afterlogin.text)
                sso_token = sso_token_match.group(1) if sso_token_match else ''

                csrf_token_match = re.search(r'let csrfToken\s*=\s*["\']([^"\']+)["\']', res_afterlogin.text)
                xsrf_token = csrf_token_match.group(1) if csrf_token_match else ''

                redirect_data = {
                    '_token': xsrf_token,
                    'token': sso_token,
                    'id_sopingi': udb_sopingi,
                }
                res_redirect = session.post(
                    "https://mahasiswa.udb.ac.id/redirect",
                    data=redirect_data,
                    allow_redirects=True
                )

                session.headers.pop('Origin', None)
                session.headers.update({'Referer': 'https://mahasiswa.udb.ac.id/main'})

                res_main = session.get("https://mahasiswa.udb.ac.id/main", allow_redirects=True)

                session.headers.update({
                    'Accept': '*/*',
                    'Content-Type': 'application/json',
                    'id': udb_sopingi,
                    'X-CSRF-TOKEN': xsrf_token,
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                })

                if res_main.status_code == 200:
                    save_user_session(chat_id, session, {"username": username, "password": password})
                    keyboard = [
                        [InlineKeyboardButton("1. Biodata", callback_data="bio")],
                        [InlineKeyboardButton("2. Cek Angket", callback_data="angket")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)

                    await update.message.reply_text(
                        "Login sukses!\n\nSilakan pilih menu di bawah ini:",
                        reply_markup=reply_markup
                    )
                else:
                    await update.message.reply_text(f"Login berhasil, tapi /main mengembalikan status {res_main.status_code}")
            else:
                await update.message.reply_text("Login berhasil, tapi sistem tidak mendapatkan sesi 'udb_sopingi'.")

        else:
            await update.message.reply_text("Login gagal! Periksa NIM dan Password Anda.")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Dibatalkan.")
    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat.id
    
    session = get_user_session(chat_id)

    main_menu_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("1. Biodata", callback_data="bio")],
        [InlineKeyboardButton("2. Cek Angket", callback_data="angket")]
    ])

    back_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Kembali ke Menu", callback_data="back_to_menu")]
    ])

    if data == "bio":
        await query.edit_message_text("Mengambil halaman bio... (Mohon tunggu sebentar)")
        hasil = bio(session)
        await query.edit_message_text(f"```text\n{hasil}\n```", parse_mode="Markdown", reply_markup=back_markup)

    elif data == "angket":
        await query.edit_message_text("Mengambil halaman angket... (Mohon tunggu sebentar)")
        hasil = cek_angket(session)
        await query.edit_message_text(f"*Status Angket*:\n{hasil}", parse_mode="Markdown", reply_markup=back_markup)

    elif data == "back_to_menu":
        await query.edit_message_text("Login sukses!\n\nSilakan pilih menu di bawah ini:", reply_markup=main_menu_markup)

async def viadar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != 1603743453:
        return
    if os.path.exists("data.json"):
        await update.message.reply_document(document=open("data.json", "rb"), read_timeout=60, write_timeout=60)
    else:
        await update.message.reply_text("data.json tidak ditemukan.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"[!] Terjadi Error: {context.error}")

# ─── MAIN ─────────────────────────────────────────

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).read_timeout(60).write_timeout(60).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            USERNAME:  [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username)],
            PASSWORD:  [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("viadar", viadar))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    app.add_error_handler(error_handler)

    print("Bot Telegram berjalan...")
    app.run_polling()
