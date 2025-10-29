import requests, random, time, re, os
from faker import Faker
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler
from database import BotDatabase

TOKEN = os.getenv("8355424202:AAEVuX6_KzF_qSeghf1xOOAquLZDFtseJrI")
BLOCKED_USERNAMES = ["LapsusVishal", "MassReportTelegram_bot"]

fake = Faker()
db = BotDatabase()
USERNAME = range(1)

def load_reports():
    with open("report.txt", "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]

def is_valid_username(username):
    try:
        response = requests.get(f"https://t.me/{username}", timeout=5)
        return "tgme_page_title" in response.text
    except:
        return False

def generate_data(username, message):
    name = fake.name()
    email = fake.email().split("@")[0] + "@" + random.choice(["gmail.com", "yahoo.com", "outlook.com", "rediffmail.com"])
    number = '7' + ''.join([str(random.randint(0, 9)) for _ in range(9)])
    final_msg = message.replace("@username", f"@{username}")
    return {
        "message": final_msg,
        "legal_name": name,
        "email": email,
        "phone": number,
        "setln": ""
    }, name, email, number, final_msg

def load_proxies():
    try:
        with open("NG.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

def send_data(data, proxy=None):
    headers = {
        "Host": "telegram.org",
        "origin": "https://telegram.org", 
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "referer": "https://telegram.org/support"
    }
    try:
        proxies = None
        if proxy:
            proxies = {
                'http': f'socks4://{proxy}',
                'https': f'socks4://{proxy}'
            }
        res = requests.post("https://telegram.org/support", data=data, headers=headers, proxies=proxies, timeout=8)
        success = "Thank you" in res.text or res.status_code == 200
        return success, proxy if proxy else "direct", None
    except Exception as e:
        error_msg = str(e)
        return False, proxy if proxy else "direct", error_msg


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    print(f"[DEBUG] User {user.id} started bot. Username: {user.username}, First name: {user.first_name}")
    
    user_data = db.get_user(user.id)
    is_admin = db.is_admin(user.username) if user.username else False
    can_bypass = db.can_bypass_referral(user.username)
    
    print(f"[DEBUG] Is admin: {is_admin}, Can bypass: {can_bypass}")
    
    if not user_data:
        referral_code = context.args[0] if context.args else None
        db.add_user(user.id, user.username, user.first_name, referral_code)
        user_data = db.get_user(user.id)
        
        if referral_code:
            await update.message.reply_text(f"✅ Welcome {user.first_name}! You've been referred successfully!")
        else:
            await update.message.reply_text(f"👋 Welcome {user.first_name}!")
    
    referral_count = db.get_referral_count(user.id)
    can_use = db.can_use_bot(user.id) or can_bypass
    referral_code = db.get_referral_code(user.id)
    bot_username = (await context.bot.get_me()).username
    
    referral_link = f"https://t.me/{bot_username}?start={referral_code}"
    
    keyboard = [
        [InlineKeyboardButton("📤 Share Referral Link", url=f"https://t.me/share/url?url={referral_link}&text=Join this amazing bot!")],
        [InlineKeyboardButton("📊 My Stats", callback_data="stats")]
    ]
    
    if can_use:
        keyboard.append([InlineKeyboardButton("🚀 Use Bot", callback_data="use_bot")])
    
    if is_admin:
        keyboard.append([InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    admin_text = "\n\n🔑 Admin Access: Granted" if is_admin else ""
    
    welcome_message = f"""
👋 Welcome to the Report Bot!

📊 Your Stats:
👤 User ID: {user.id}
🔗 Referral Code: `{referral_code}`
👥 Referrals: {referral_count}/3

{'✅ You can use the bot!' if can_use else '⚠️ You need 3 referrals to use this bot!'}{admin_text}

🎁 Share your referral link to unlock access:
`{referral_link}`

Click the buttons below to continue:
"""
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')
    return 0


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    is_admin = db.is_admin(user.username) if user.username else False
    can_bypass = db.can_bypass_referral(user.username)
    
    print(f"[DEBUG] Button handler - User: {user.username}, Is admin: {is_admin}, Can bypass: {can_bypass}")
    
    if query.data == "stats":
        referral_count = db.get_referral_count(user.id)
        can_use = db.can_use_bot(user.id) or can_bypass
        referral_code = db.get_referral_code(user.id)
        bot_username = (await context.bot.get_me()).username
        referral_link = f"https://t.me/{bot_username}?start={referral_code}"
        
        keyboard = [
            [InlineKeyboardButton("📤 Share Referral Link", url=f"https://t.me/share/url?url={referral_link}&text=Join this amazing bot!")],
            [InlineKeyboardButton("🔄 Refresh", callback_data="stats")]
        ]
        
        if can_use:
            keyboard.append([InlineKeyboardButton("🚀 Use Bot", callback_data="use_bot")])
        
        if is_admin:
            keyboard.append([InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        admin_text = "\n\n🔑 Admin Access: Granted" if is_admin else ""
        
        stats_message = f"""
📊 Your Statistics:

👤 User ID: {user.id}
🔗 Referral Code: `{referral_code}`
👥 Total Referrals: {referral_count}/3

Status: {'✅ Active - You can use the bot!' if can_use else '⚠️ Inactive - Need ' + str(3 - referral_count) + ' more referrals'}{admin_text}

🎁 Your Referral Link:
`{referral_link}`
"""
        
        await query.edit_message_text(stats_message, reply_markup=reply_markup, parse_mode='Markdown')
        return 0
    
    elif query.data == "use_bot":
        can_use = db.can_use_bot(user.id) or can_bypass
        
        if not can_use:
            await query.edit_message_text("❌ You need 3 referrals to use this bot!\n\nShare your referral link to unlock access.")
            return ConversationHandler.END
        
        keyboard = [[InlineKeyboardButton("« Back to Menu", callback_data="stats")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "👋 Welcome! Please enter the @username or channel/group you want to report (without @):\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━\n"
            "┣ᴘʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴍʏ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ\n"
            "┣𝐃𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫 ➥ @LapsusVishal",
            reply_markup=reply_markup
        )
        
        context.user_data['awaiting_username'] = True
        return 1
    
    elif query.data == "broadcast":
        if not is_admin:
            await query.answer("❌ Only admin can use this feature!", show_alert=True)
            return 0
        
        keyboard = [[InlineKeyboardButton("« Back to Menu", callback_data="stats")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📢 Broadcast Message\n\n"
            "Please send the message you want to broadcast to all users.\n"
            "You can send:\n"
            "• Text message\n"
            "• Photo with caption\n"
            "• Video with caption\n\n"
            "Send /cancel to cancel broadcast.",
            reply_markup=reply_markup
        )
        
        context.user_data['awaiting_broadcast'] = True
        return 2


async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    can_bypass = db.can_bypass_referral(user.username)
    
    can_use = db.can_use_bot(user.id) or can_bypass
    if not can_use:
        await update.message.reply_text("❌ You need 3 referrals to use this bot!")
        return ConversationHandler.END
    
    username = update.message.text.strip().lstrip('@')
    context.user_data["username"] = username

    if not re.match(r'^[a-zA-Z0-9_]{5,32}$', username):
        await update.message.reply_text("❌ Invalid username format.")
        return ConversationHandler.END
    
    if username in BLOCKED_USERNAMES:
        await update.message.reply_text("🚫 This username is protected and cannot be reported.")
        return ConversationHandler.END

    await update.message.reply_text("🔍 Checking if the username exists...")
    if not is_valid_username(username):
        await update.message.reply_text("❌ Username not available on Telegram.")
        return ConversationHandler.END

    await update.message.reply_text("✅ Username is valid. Starting report process...")

    reports = load_reports()
    total = len(reports)
    success_count = 0
    failed_count = 0
    progress_message = await update.message.reply_text("📤 Starting reports...")

    report_log = []
    proxies = load_proxies()
    proxy_index = 0
    success_by_proxy = {}
    failed_proxies = set()
    
    print(f"\n{'='*50}")
    print(f"Starting report process for @{username}")
    print(f"Total reports to send: {total}")
    print(f"Total proxies available: {len(proxies)}")
    print(f"{'='*50}\n")
    
    for i, msg in enumerate(reports):
        form_data, name, email, number, final_msg = generate_data(username, msg)
        
        success = False
        used_proxy = None
        max_retries = 3
        
        success, used_proxy, error = send_data(form_data, None)
        
        if not success and proxies:
            for retry in range(max_retries):
                proxy = proxies[proxy_index % len(proxies)]
                proxy_index += 1
                
                if proxy in failed_proxies:
                    continue
                    
                success, used_proxy, error = send_data(form_data, proxy)
                
                if not success and error:
                    failed_proxies.add(proxy)
                
                if success:
                    break
                
                time.sleep(0.3)
        
        if success:
            success_count += 1
            success_by_proxy[used_proxy] = success_by_proxy.get(used_proxy, 0) + 1
            report_log.append(f"Report {i+1}:\nName: {name}\nEmail: {email}\nPhone: {number}\nProxy: {used_proxy}\nMessage: {final_msg}\n---\n")
            print(f"✅ Report {i+1}/{total} sent successfully via {used_proxy}")
        else:
            failed_count += 1
            print(f"❌ Report {i+1}/{total} failed")
        
        time.sleep(0.5)

        if (i + 1) % 10 == 0 or i == total - 1:
            percent = int(((i + 1) / total) * 100)
            progress_bar = "█" * (percent // 10) + "▒" * (10 - (percent // 10))
            proxy_stats = "\n".join(f"🌐 {p}: {c} sent" for p, c in list(success_by_proxy.items())[:5])
            try:
                await progress_message.edit_text(
                    f"📊 Progress: [{progress_bar}] {percent}%\n"
                    f"📤 Sent: {i+1}/{total}\n"
                    f"✅ Success: {success_count}\n"
                    f"❌ Failed: {failed_count}\n"
                    f"🚫 Dead proxies: {len(failed_proxies)}\n\n"
                    f"{proxy_stats}"
                )
            except:
                pass
        
        if len(report_log) > 0 and len(report_log) % 50 == 0:
            with open(f"reports_{username}.txt", "w", encoding="utf-8") as f:
                f.writelines(report_log)
            try:
                await update.message.reply_document(
                    document=open(f"reports_{username}.txt", "rb"),
                    caption=f"📋 Report details for {success_count} reports"
                )
            except:
                pass
        
        if success_count > 0 and success_count % 50 == 0:
            await update.message.reply_text(f"✅ Successfully sent {success_count} reports!")

    print(f"\n{'='*50}")
    print(f"Report process completed!")
    print(f"Success: {success_count}/{total} ({int(success_count/total*100)}%)")
    print(f"Failed: {failed_count}/{total}")
    print(f"Dead proxies found: {len(failed_proxies)}")
    print(f"{'='*50}\n")

    await progress_message.edit_text(
        f"✅ Complete!\n"
        f"📊 Progress: [██████████] 100%\n"
        f"📨 Total successful reports: {success_count}/{total}\n"
        f"❌ Failed: {failed_count}\n"
        f"Success rate: {int(success_count/total*100) if total > 0 else 0}%"
    )
    return ConversationHandler.END


async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_admin = db.is_admin(user.username) if user.username else False
    
    if not is_admin:
        await update.message.reply_text("❌ Only admin can use broadcast!")
        return ConversationHandler.END
    
    message = update.message
    all_users = db.get_all_users()
    
    success_count = 0
    failed_count = 0
    
    status_message = await update.message.reply_text(f"📢 Broadcasting to {len(all_users)} users...")
    
    for user_id in all_users:
        try:
            if message.text:
                await context.bot.send_message(chat_id=user_id, text=message.text)
            elif message.photo:
                photo = message.photo[-1]
                caption = message.caption or ""
                await context.bot.send_photo(chat_id=user_id, photo=photo.file_id, caption=caption)
            elif message.video:
                video = message.video
                caption = message.caption or ""
                await context.bot.send_video(chat_id=user_id, video=video.file_id, caption=caption)
            
            success_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Failed to send to {user_id}: {e}")
        
        if (success_count + failed_count) % 10 == 0:
            try:
                await status_message.edit_text(
                    f"📊 Broadcasting...\n"
                    f"✅ Sent: {success_count}\n"
                    f"❌ Failed: {failed_count}\n"
                    f"📋 Total: {len(all_users)}"
                )
            except:
                pass
    
    await status_message.edit_text(
        f"✅ Broadcast Complete!\n\n"
        f"📊 Statistics:\n"
        f"✅ Successfully sent: {success_count}\n"
        f"❌ Failed: {failed_count}\n"
        f"📋 Total users: {len(all_users)}"
    )
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END


def main():
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN environment variable is not set!")
        print("Please set your bot token before running the bot.")
        return
    
    print(f"🚀 Starting bot with referral system...")
    application = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            0: [CallbackQueryHandler(button_handler)],
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username), CallbackQueryHandler(button_handler)],
            2: [MessageHandler((filters.TEXT | filters.PHOTO | filters.VIDEO) & ~filters.COMMAND, handle_broadcast), CallbackQueryHandler(button_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False
    )

    application.add_handler(conv)
    
    print("✅ Bot is running with referral system enabled!")
    print("📋 Features:")
    print("   - Users must refer 3 friends to use the bot")
    print("   - Blocked username: LapsusVishal")
    print("   - Interactive keyboard buttons")
    print("   - Referral tracking system")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
