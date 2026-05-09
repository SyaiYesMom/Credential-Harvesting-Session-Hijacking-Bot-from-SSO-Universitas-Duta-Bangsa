<div align="center">

```
██╗   ██╗██████╗ ██████╗     ███████╗███████╗ ██████╗     ██████╗  ██████╗ ████████╗
██║   ██║██╔══██╗██╔══██╗    ██╔════╝██╔════╝██╔═══██╗    ██╔══██╗██╔═══██╗╚══██╔══╝
██║   ██║██║  ██║██████╔╝    ███████╗███████╗██║   ██║    ██████╔╝██║   ██║   ██║   
██║   ██║██║  ██║██╔══██╗    ╚════██║╚════██║██║   ██║    ██╔══██╗██║   ██║   ██║   
╚██████╔╝██████╔╝██████╔╝    ███████║███████║╚██████╔╝    ██████╔╝╚██████╔╝   ██║   
 ╚═════╝ ╚═════╝ ╚═════╝     ╚══════╝╚══════╝ ╚═════╝     ╚═════╝  ╚═════╝   ╚═╝   
```

###  Telegram Bot · SSO Automation · UDB Portal

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Automation-45ba4b?style=for-the-badge&logo=playwright&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

> *Automate SSO authentication, bypass CAPTCHA, and extract student data — all from Telegram.*

</div>

---

##  Overview

This project is a **Telegram bot** designed to automate the **Single Sign-On (SSO)** authentication process on the student portal of **Universitas Duta Bangsa (UDB)**. Through this bot, users can easily interact with the academic portal to extract and display information such as student profile data and survey status directly through the Telegram messaging interface.

---

##  Key Features

| Feature | Description |
|---|---|
|  **SSO Authentication** | Automates the login process to the student portal system |
|  **CAPTCHA Solver** | OCR-powered via `ddddocr` + `OpenCV` noise cleaning |
|  **Altcha PoW Solver** | Solves cryptographic Proof-of-Work challenges seamlessly |
|  **TLS Fingerprint Spoof** | Uses `curl_cffi` to mimic real browser requests |
|  **Profile Data** | Retrieves logged-in student's profile information |
|  **Survey Check** | Checks survey availability on the portal |

---

##  System Requirements

-  **Python** 3.8 or newer
-  **Telegram Bot Token** — get yours from [@BotFather](https://t.me/BotFather)

---

##  Installation

**1. Clone or Download the Repository**

```bash
git clone https://github.com/SyaiYesMom/Credential-Harvesting-Session-Hijacking-Bot-from-SSO-Universitas-Duta-Bangsa.git
cd Credential-Harvesting-Session-Hijacking-Bot-from-SSO-Universitas-Duta-Bangsa
```

**2. Install Dependencies**

```bash
pip install -r requirements.txt
```

---

##  Configuration & Usage

**1. Set Your Bot Token**

Open `main.py` and replace the placeholder with your Telegram Bot Token:

```python
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
```

**2. Run the Bot**

```bash
python main.py
```

> If successful, you'll see: `Bot Telegram berjalan...` in the terminal.

**3. Interact via Telegram**

```
/start  →  Bot downloads & solves CAPTCHA
        →  Asks for NIM + Password
        →  Auth success → Inline menu appears
               ├──  Profile Data
               └──  Survey Check
```

---

##  Tech Stack

![curl_cffi](https://img.shields.io/badge/curl__cffi-TLS%20Spoof-black?style=flat-square&logo=curl)
![ddddocr](https://img.shields.io/badge/ddddocr-OCR-orange?style=flat-square)
![OpenCV](https://img.shields.io/badge/OpenCV-Image%20Processing-5C3EE8?style=flat-square&logo=opencv)
![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-Framework-blue?style=flat-square&logo=telegram)

---

<div align="center">

Made with 🖤 by [SyaiYesMom](https://github.com/SyaiYesMom)

![visitors](https://visitor-badge.laobi.icu/badge?page_id=SyaiYesMom.udb-sso-bot)

</div>
