from kyt import *
import subprocess
import re
import datetime as DT
import shlex
import json
import asyncio

# =================== HELPER FUNCTIONS ===================
async def show_progress(event):
    """Menampilkan animasi progress bar"""
    steps = [
        ("Proses.", 0.5),
        ("Proses..", 0.5),
        ("Proses...", 0.5),
        ("Proses....", 0.5),
        ("Memulai pembuatan akun", 1),
        ("Proses... 0%\n▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒", 1),
        ("Proses... 4%\n█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒", 0.3),
        ("Proses... 8%\n██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒", 0.3),
        ("Proses... 20%\n█████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒", 0.3),
        ("Proses... 36%\n█████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒", 0.5),
        ("Proses... 52%\n█████████████▒▒▒▒▒▒▒▒▒▒▒▒", 0.5),
        ("Proses... 84%\n█████████████████████▒▒▒▒", 0.3),
        ("Proses... 100%\n█████████████████████████", 1),
        ("Menyiapkan hasil...", 1)
    ]
    for msg, delay in steps:
        await event.edit(msg)
        await asyncio.sleep(delay)

async def execute_shell(cmd):
    """Eksekusi command shell dengan error handling"""
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise Exception(f"Gagal Mengeksekusi Perintah: {e.stderr.strip()}")
    except subprocess.TimeoutExpired:
        raise Exception("⏳ Timeout: Proses terlalu lama, silakan coba lagi")

def parse_trojan_links(output):
    """Parsing output untuk mendapatkan link Trojan"""
    try:
        links = re.findall(r"trojan://(.*?)\n", output)
        if len(links) < 2:
            raise ValueError("Format output tidak valid")
        
        return {
            "ws": links[0].strip(),
            "grpc": links[1].strip(),
            "uuid": re.search(r"trojan://(.*?)@", links[0]).group(1),
            "domain": re.search(r"@(.*?):", links[0]).group(1)
        }
    except Exception as e:
        raise ValueError(f"Gagal parsing output: {str(e)}")

# =================== MAIN HANDLERS ===================
@bot.on(events.CallbackQuery(data=b'create-trojan'))
async def create_trojan(event):
    try:
        # Tampilkan progress
        await show_progress(event)

        # Eksekusi command
        cmd = 'echo "user quota ip expiry" | add-tro'
        output = await execute_shell(cmd)

        # Parse output
        details = parse_trojan_links(output)
        expiry_date = DT.date.today() + DT.timedelta(days=30)

        # Format pesan
        msg = f"""
🛡️ **TROJAN ACCOUNT CREATED** 🛡️
▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
▸ **UUID:** `{details['uuid']}`
▸ **Domain:** `{details['domain']}`
▸ **Expired:** `{expiry_date.strftime('%d %b %Y')}`
▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
🔗 **WS Link:**
`{details['ws']}`
▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
🔗 **gRPC Link:**
`{details['grpc']}`
"""
        await event.respond(msg)
    except Exception as e:
        await event.respond(f"🚨 **Creation Failed:**\n{str(e)}")

@bot.on(events.CallbackQuery(data=b'delete-trojan'))
async def delete_trojan(event):
    try:
        username = await event.get_reply_message()
        await show_progress(event)
        
        cmd = f'printf "%s\\n" {username} | del-tro'
        await execute_shell(cmd)
        
        await event.respond(f"✅ **Success Deleted:** `{username}`")
    except Exception as e:
        await event.respond(f"❌ **Deletion Failed:**\n{str(e)}")

@bot.on(events.CallbackQuery(data=b'cek-trojan'))
async def cek_trojan(event):
    try:
        cmd = 'bot-cek-tr'
        output = await execute_shell(cmd)
        
        msg = f"""
📊 **ACTIVE TROJAN USERS** 📊
▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
```{output}```
▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
⚠️ **Update terakhir:** {DT.datetime.now().strftime('%d/%m/%Y %H:%M')}
"""
        await event.respond(msg)
    except Exception as e:
        await event.respond(f"❌ **Check Failed:**\n{str(e)}")

@bot.on(events.CallbackQuery(data=b'trojan'))
async def trojan_menu(event):
    menu = [
        [Button.inline("➕ BUAT TROJAN", "create-trojan"),
         Button.inline("🆓 TRIAL", "trial-trojan")],
        [Button.inline("📋 LIST AKUN", "cek-trojan"),
         Button.inline("🗑️ HAPUS AKUN", "delete-trojan")],
        [Button.inline("🔙 MENU UTAMA", "menu")]
    ]
    
    info = requests.get("http://ip-api.com/json").json()
    msg = f"""
🛠️ **TROJAN MANAGER** 🛠️
▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
▸ **Server:** `{DOMAIN}`
▸ **ISP:** `{info.get('isp', 'Unknown')}`
▸ **Lokasi:** `{info.get('country', 'Unknown')}`
▸ **Protocol:** `TCP/WS + gRPC`
▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
⚠️ **Fitur yang tersedia:**
- Auto Notifikasi Telegram
- Multi Protocol (WS/gRPC)
- Sistem Quota & Limit IP
- Manajemen Akun Lengkap
"""
    await event.edit(msg, buttons=menu)

# =================== RUN BOT ===================
if __name__ == '__main__':
    bot.run_until_disconnected()
