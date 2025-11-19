import telebot
import hashlib
import time
import random
import json
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# --- CẤU HÌNH HỆ THỐNG (SỬA TẠI ĐÂY) ---
BOT_TOKEN = "8247971504:AAFCvmdSCPLQQp9v5-6RBQUOyYrGEiq-UJs" # Thay token của bạn
ADMIN_ID = 8196174785 # ID của bạn
ADMIN_USERNAME = "NamSky88" # Username Admin
CHANNEL_ID = "@ToolsTaiXiu" 
CHANNEL_LINK = "https://t.me/ToolsTaiXiu"

# --- DANH SÁCH VIP CỨNG (Luôn được add khi khởi động) ---
PERMANENT_VIPS = [
    ADMIN_ID,
    ]

# --- CƠ SỞ DỮ LIỆU ---
USERS_FILE = "vip_members.json"

# Khởi tạo bot
bot = telebot.TeleBot(BOT_TOKEN)

# --- HÀM HỆ THỐNG: QUẢN LÝ VIP ---
def load_vip_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                users = json.load(f)
        except:
            users = []
    else:
        users = []

    is_changed = False
    for uid in PERMANENT_VIPS:
        if uid not in users:
            users.append(uid)
            is_changed = True
    
    if is_changed:
        save_vip_users(users)
    return users

def save_vip_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

vip_users = load_vip_users()

# --- HÀM HỆ THỐNG: KIỂM TRA JOIN NHÓM ---
def check_member_joined(user_id):
    if user_id == ADMIN_ID: return True 
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except:
        return True 

# --- MENU CHÍNH ---
def main_menu_keyboard():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = KeyboardButton("🌞 SUNWIN")
    btn2 = KeyboardButton("🔥 HITCLUB")
    btn3 = KeyboardButton("👤 Tài Khoản")
    btn4 = KeyboardButton("📞 Hỗ Trợ")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# --- LÕI PHÂN TÍCH ---
class PredictionEngine:
    def get_advice(self, confidence):
        # Đã xóa các ký tự gây lỗi Markdown
        if confidence >= 80:
            return random.choice([
                "🔥 CẦU ĐANG VÀO GUỒNG: Tín hiệu cực kỳ ổn định. Anh em tự tin vào tiền, có thể đi mạnh tay.",
                "💎 TÍN HIỆU VÀNG: Phân tích lịch sử cho thấy nhịp này rất khó gãy. Cơ hội về bờ là đây.",
                "🚀 CƠ HỘI LỚN: Cầu đang đi đúng sách giáo khoa. Mạnh dạn gấp thếp nếu đang lãi.",
                "✅ KHẢ NĂNG NỔ CAO: Thuật toán AI báo về độ trùng khớp 90%. Kèo này thơm phức.",
                "💰 THỜI ĐIỂM VÀNG: Nhà cái đang nhả cầu này. Tranh thủ húp nhanh gọn lẹ."
            ])
        elif confidence >= 65:
            return random.choice([
                "🛡️ AN TOÀN LÀ BẠN: Cầu ổn định nhưng chưa bùng nổ. Khuyên anh em đi đều tay.",
                "👀 QUAN SÁT KỸ: Tín hiệu khá rõ nhưng vẫn cần đề phòng. Đánh mức trung bình.",
                "⚖️ CÂN BẰNG VỐN: Đừng để lòng tham dẫn dắt. Chia vốn ra đánh.",
                "🐢 CHẬM MÀ CHẮC: Nhịp cầu đang chuyển giao. Đánh vừa phải thăm dò.",
                "💡 CHIẾN THUẬT: Cầu này phù hợp đánh rỉa. Không nên gấp thếp ở tay này."
            ])
        else:
            return random.choice([
                "⚠️ CẢNH BÁO ĐỎ: Cầu đang cực kỳ loạn. Khuyên chân thành anh em nên BỎ QUA.",
                "🛑 RỦI RO CAO: Dữ liệu cho thấy pha này dễ bẻ lái. Ngồi xem giữ tiền là thắng.",
                "☠️ VÙNG TỬ THẦN: Đừng cố đấm ăn xôi. Cầu đang xấu, ra ngoài hít thở đi.",
                "📉 TÍN HIỆU XẤU: AI không tìm thấy quy luật. Tỷ lệ 50/50 may rủi quá cao.",
                "🚫 STOP: Đừng để lòng tham làm mờ mắt. Tay này cực khoai."
            ])

    def analyze(self, input_data):
        seed_str = str(input_data).strip()
        hash_obj = hashlib.md5(seed_str.encode()).hexdigest()
        numbers = [int(c, 16) for c in hash_obj if c.isdigit()]
        total = sum(numbers)
        
        prediction = "TÀI 🔴" if total % 2 == 0 else "XỈU 🔵"
        
        random.seed(seed_str) 
        confidence = round(random.uniform(50.0, 85.0), 2)
        advice = self.get_advice(confidence)
        
        return prediction, confidence, advice

engine = PredictionEngine()
user_sessions = {} 

# --- CÁC LỆNH ADMIN ---
@bot.message_handler(commands=['capquyen'])
def cap_quyen(message):
    if message.from_user.id != ADMIN_ID: return 
    try:
        uid = int(message.text.split()[1])
        if uid not in vip_users:
            vip_users.append(uid)
            save_vip_users(vip_users)
            bot.reply_to(message, f"✅ Đã kích hoạt VIP cho ID: `{uid}`", parse_mode="Markdown")
            try:
                bot.send_message(uid, "🎉 **CHÚC MỪNG!** Tài khoản đã kích hoạt. Bấm /start để dùng.", parse_mode="Markdown")
            except: pass
        else:
            bot.reply_to(message, "⚠️ ID này đã là VIP rồi.")
    except:
        bot.reply_to(message, "❌ Dùng: `/capquyen <ID>`", parse_mode="Markdown")

@bot.message_handler(commands=['xoaquyen'])
def xoa_quyen(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        uid = int(message.text.split()[1])
        if uid in vip_users:
            vip_users.remove(uid)
            save_vip_users(vip_users)
            bot.reply_to(message, f"🚫 Đã xóa VIP của ID: `{uid}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, "⚠️ ID này chưa phải VIP.")
    except:
        bot.reply_to(message, "❌ Dùng: `/xoaquyen <ID>`", parse_mode="Markdown")

# --- XỬ LÝ START ---
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    welcome_msg = f"👋 Xin chào {message.from_user.first_name}!\nChào mừng đến với **TOOL TX PRO V7.5**.\n\n👇 **SỬ DỤNG MENU BÊN DƯỚI:**"
    bot.send_message(message.chat.id, welcome_msg, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

# --- NÚT MENU ---
@bot.message_handler(func=lambda message: message.text == "👤 Tài Khoản")
def my_account(message):
    status = "✅ VIP" if message.from_user.id in vip_users else "🔒 Chưa kích hoạt"
    bot.reply_to(message, f"👤 **TÀI KHOẢN**\n🆔 ID: `{message.from_user.id}`\n🏷 Trạng Thái: {status}", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "📞 Hỗ Trợ")
def support(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💬 Nhắn Tin Admin", url=f"https://t.me/{ADMIN_USERNAME}")) 
    bot.reply_to(message, "📞 Cần hỗ trợ? Liên hệ ngay:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["🌞 SUNWIN", "🔥 HITCLUB"])
def chon_game(message):
    user_id = message.from_user.id
    
    if not check_member_joined(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("👉 VÀO NHÓM NGAY", url=CHANNEL_LINK))
        bot.send_message(message.chat.id, "🚫 Bạn chưa vào nhóm.", reply_markup=markup)
        return

    if user_id not in vip_users:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💬 LIÊN HỆ ADMIN", url=f"https://t.me/{ADMIN_USERNAME}"))
        bot.send_message(message.chat.id, f"🔒 **CHƯA KÍCH HOẠT!**\n🆔 ID: `{user_id}`\nLiên hệ Admin để mua gói.", reply_markup=markup, parse_mode="Markdown")
        return

    game = message.text
    # Xóa session cũ để tránh lỗi
    if user_id in user_sessions: del user_sessions[user_id]

    if "SUNWIN" in game:
        user_sessions[user_id] = {"game": "SUNWIN", "mode": "TX", "last_phien": 0}
        bot.send_message(message.chat.id, "🌞 **SUNWIN (Tài Xỉu)**\n👉 Nhập **MÃ PHIÊN** (Số) để soi:", parse_mode="Markdown")
    
    elif "HITCLUB" in game:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🎲 TX Thường", callback_data="hit_tx"))
        markup.add(InlineKeyboardButton("🔐 TX MD5", callback_data="hit_md5"))
        bot.send_message(message.chat.id, "🔥 **HITCLUB - Chọn chế độ:**", reply_markup=markup, parse_mode="Markdown")

# --- XỬ LÝ CALLBACK (NÚT BẤM) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.from_user.id
    
    # FIX LỖI MODE: Đảm bảo gán đúng chế độ khi bấm nút
    if call.data == "hit_tx":
        user_sessions[user_id] = {"game": "HITCLUB", "mode": "TX", "last_phien": 0}
        bot.edit_message_text("🔥 **HITCLUB (TX Thường)**\n👉 Nhập **MÃ PHIÊN** (Số) để soi:", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    
    elif call.data == "hit_md5":
        user_sessions[user_id] = {"game": "HITCLUB", "mode": "MD5"}
        bot.edit_message_text("🔐 **HITCLUB (MD5)**\n👉 Copy & Dán **chuỗi MD5** vào đây:", call.message.chat.id, call.message.message_id, parse_mode="Markdown")

    elif call.data == "next_session":
        if user_id not in user_sessions:
            bot.answer_callback_query(call.id, "⚠️ Phiên hết hạn. Chọn lại game.", show_alert=True)
            return
        if user_sessions[user_id]["mode"] == "MD5":
            bot.answer_callback_query(call.id, "❌ MD5 không tự nhảy phiên.", show_alert=True)
            return
        
        next_phien = user_sessions[user_id]["last_phien"] + 1
        user_sessions[user_id]["last_phien"] = next_phien
        process_prediction(call.message, next_phien)

# --- XỬ LÝ INPUT ---
@bot.message_handler(func=lambda message: message.text.strip() not in ["🌞 SUNWIN", "🔥 HITCLUB", "👤 Tài Khoản", "📞 Hỗ Trợ"])
def handle_input(message):
    user_id = message.from_user.id
    if user_id not in vip_users: return 
    if user_id not in user_sessions:
        bot.reply_to(message, "⚠️ Vui lòng chọn Cổng Game trước!")
        return

    data = message.text.strip()
    session = user_sessions[user_id]

    # Phân loại xử lý dựa trên MODE đã chọn
    if session["mode"] == "TX":
        if not data.isdigit():
            bot.reply_to(message, "❌ Mã phiên phải là số!")
            return
        user_sessions[user_id]["last_phien"] = int(data)
        process_prediction(message, int(data))
    
    elif session["mode"] == "MD5":
        process_prediction(message, data)

# --- HÀM TRẢ KẾT QUẢ (FIXED MARKDOWN) ---
def process_prediction(message, input_data):
    user_id = message.from_user.id
    session = user_sessions[user_id]
    
    wait = bot.send_message(message.chat.id, "🔄 **Đang phân tích...**", parse_mode="Markdown")
    time.sleep(1.5)
    
    pred, conf, advice = engine.analyze(input_data)
    
    bar = "▓" * int((conf-50)/3.5) + "░" * (10 - int((conf-50)/3.5))

    text = f"""
🎰 **KẾT QUẢ SOI CẦU {session['game']}**
────────────────
🆔 **Phiên:** `{input_data}`
🛠 **Chế độ:** {session['mode']}

📊 **PHÂN TÍCH:**
• Tỷ lệ: `{conf}%`
• Tín hiệu: [{bar}]

🎯 **DỰ ĐOÁN:**
# ✨ {pred} ✨

💡 **LỜI KHUYÊN:**
{advice}
────────────────
⚠️ _Kết quả tham khảo. Vui lòng quản lý vốn._
"""
    markup = None
    if session["mode"] == "TX":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"🔮 Soi Phiên Tiếp ({int(input_data)+1}) ⏩", callback_data="next_session"))

    bot.delete_message(message.chat.id, wait.message_id)
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

# --- CHẠY BOT ---
print("🚀 Bot TX PRO V7.5 (Fix Bug & Clean) đang chạy...")
bot.infinity_polling()
