import os
import json
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# قراءة التوكن من متغير البيئة (أو ضع التوكن مباشرة هنا)
TOKEN = os.getenv("TOKEN", "YOUR_TOKEN_HERE")

# ملف النقاط
POINTS_FILE = "points.json"

# تحميل النقاط من الملف
def load_points():
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# حفظ النقاط في الملف
def save_points(points):
    with open(POINTS_FILE, "w", encoding="utf-8") as f:
        json.dump(points, f, ensure_ascii=False, indent=2)

# إضافة نقاط
def add_points(user_id, points_to_add):
    points = load_points()
    points[str(user_id)] = points.get(str(user_id), 0) + points_to_add
    save_points(points)

# أمر /الألعاب
async def games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game_choice = random.choice(["🎲 رقم عشوائي", "🎯 تخمين الرقم"])
    await update.message.reply_text(f"اخترنا لك لعبة: {game_choice}")

# أمر /الترتيب
async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    points = load_points()
    sorted_points = sorted(points.items(), key=lambda x: x[1], reverse=True)
    if not sorted_points:
        await update.message.reply_text("لا يوجد أي نقاط حتى الآن.")
        return
    msg = "🏆 ترتيب اللاعبين:\n"
    for i, (user_id, pts) in enumerate(sorted_points[:10], start=1):
        msg += f"{i}. {user_id} — {pts} نقطة\n"
    await update.message.reply_text(msg)

# أمر /حظر
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("يجب الرد على رسالة الشخص المراد حظره.")
        return
    user_id = update.message.reply_to_message.from_user.id
    try:
        await update.effective_chat.ban_member(user_id)
        await update.message.reply_text("🚫 تم حظر العضو بنجاح.")
    except:
        await update.message.reply_text("❌ لا أستطيع حظر هذا العضو.")

# أمر /رفع_الحظر
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("يجب الرد على رسالة الشخص المراد رفع الحظر عنه.")
        return
    user_id = update.message.reply_to_message.from_user.id
    try:
        await update.effective_chat.unban_member(user_id)
        await update.message.reply_text("✅ تم رفع الحظر عن العضو.")
    except:
        await update.message.reply_text("❌ لا أستطيع رفع الحظر عن هذا العضو.")

# أمر /ترقية
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("يجب الرد على رسالة الشخص المراد ترقيته.")
        return
    user_id = update.message.reply_to_message.from_user.id
    try:
        await update.effective_chat.promote_member(user_id, can_manage_chat=True)
        await update.message.reply_text("⬆️ تم ترقية العضو إلى مشرف.")
    except:
        await update.message.reply_text("❌ لا أستطيع ترقية هذا العضو.")

# أمر /تنزيل_الرتبة
async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("يجب الرد على رسالة الشخص المراد تنزيل رتبته.")
        return
    user_id = update.message.reply_to_message.from_user.id
    try:
        await update.effective_chat.promote_member(
            user_id,
            can_manage_chat=False,
            can_delete_messages=False,
            can_manage_video_chats=False,
            can_promote_members=False
        )
        await update.message.reply_text("⬇️ تم تنزيل رتبة العضو.")
    except:
        await update.message.reply_text("❌ لا أستطيع تنزيل رتبة هذا العضو.")

# أمر /همسة
async def whisper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("الاستخدام: /همسة @username الرسالة")
        return
    username = context.args[0]
    message = " ".join(context.args[1:])
    try:
        await context.bot.send_message(chat_id=username, text=f"💌 همسة لك: {message}")
        await update.message.reply_text("✅ تم إرسال الهمسة.")
    except:
        await update.message.reply_text("❌ لم أتمكن من إرسال الهمسة. ربما العضو لم يبدأ محادثة خاصة مع البوت.")

# تشغيل البوت
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("الألعاب", games))
app.add_handler(CommandHandler("الترتيب", ranking))
app.add_handler(CommandHandler("حظر", ban))
app.add_handler(CommandHandler("رفع_الحظر", unban))
app.add_handler(CommandHandler("ترقية", promote))
app.add_handler(CommandHandler("تنزيل_الرتبة", demote))
app.add_handler(CommandHandler("همسة", whisper))

if __name__ == "__main__":
    print("🚀 البوت يعمل الآن...")
    app.run_polling()
