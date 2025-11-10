import telebot
import hashlib
import time
import random
import json
import os
import threading 
from datetime import datetime, timedelta
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

# --- TRUNG TÂM ĐIỀU KHIỂN CỦA CẬU (5 Ổ KHOÁ - V6.15) ---
# Ổ KHOÁ 1: Chìa khoá Bot (Của cậu)
BOT_TOKEN = "8278136953:AAF1RD6S874aE_n_KOb1hSAr3NLsElAYG6U" 

# Ổ KHOÁ 2: ID ADMIN (LẤY TỪ @userinfobot)
ADMIN_ID = 8196174785 # <--- BẮT BUỘC THAY BẰNG SỐ ID CỦA CẬU

# Ổ KHOÁ 3: Username Admin (Của cậu)
ADMIN_USERNAME = "@NAMSKY88" 

# Ổ KHOÁ 4: ID Nhóm CHÍNH (Của cậu)
GROUP_CHAT_ID = "@casinonoidiaaa" 

# Ổ KHOÁ 5: Link Đại Lý "Lối 2"
AGENT_LINK = "https://m.fly88j.com/?id=733040027"

# --- CÁC CÀI ĐẶT CỦA PHỄU (V6.8) ---
MIN_WITHDRAW_INVITE = 500000 
MIN_WITHDRAW_TASK = 888888 
INVITE_REWARD = 5000
DAILY_REWARD = 5000
DB_FILE = "users_database.json" 

# --- CÀI ĐẶT FAKE SỐ LIỆU (V6.4) ---
FAKE_BASE_USERS = 15126 
FAKE_BASE_MONEY = 30817000 
BOT_BIRTHDAY = datetime(2025, 10, 25) 
HOURLY_USER_GROWTH = 10 
HOURLY_MONEY_GROWTH = 50000 
MONEY_PER_REAL_USER = 10000 

# --- TÊN NÚT BẤM (Kiến trúc V6.3 - Chống lỗi Emoji) ---
BTN_TAIKHOAN = "📊 Tài khoản"
BTN_MOIBAN = "👥 Mời bạn"
BTN_THONGKE = "📈 Thống kê"
BTN_RUTTIEN = "🏧 Rút tiền"
BTN_DIEMDANH = "📅 Điểm danh"
BTN_LINKGAME = "🔥 Link game (Nhận đến 888k)"


# --- KHỞI TẠO HỆ THỐNG ---
bot = telebot.TeleBot(BOT_TOKEN)

# --- MODULE DATABASE (Dùng file JSON) ---
def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_users(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- HÀM "LÕI" (V6.8) ---
def get_user(users, user_id): 
    """Lấy data từ 1 database đã tải, nếu chưa có thì tạo mới"""
    user_id_str = str(user_id)
    if user_id_str not in users:
        users[user_id_str] = {
            "username": "", 
            "invite_balance": 0,
            "task_balance": 0,
            "invited_by": None,
            "invited_count": 0,
            "last_check_in": None, 
            "is_new_user": True 
        }
    return users, users[user_id_str] 

# --- MODULE KIẾN TRÚC MENU (V6.6) ---
def create_main_menu():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_taikhoan = KeyboardButton(BTN_TAIKHOAN)
    btn_moiban = KeyboardButton(BTN_MOIBAN)
    btn_thongke = KeyboardButton(BTN_THONGKE)
    btn_ruttien = KeyboardButton(BTN_RUTTIEN)
    btn_diemdanh = KeyboardButton(BTN_DIEMDANH)
    btn_linkgame = KeyboardButton(BTN_LINKGAME)
    markup.add(btn_taikhoan, btn_moiban, btn_thongke, btn_ruttien, btn_diemdanh, btn_linkgame)
    return markup

# --- MODULE KIỂM TRA "CÁNH CỔNG" (V6.5 - Đã vá lỗi) ---
def check_if_joined(user_id, message):
    safe_admin_username = ADMIN_USERNAME.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')
    try:
        status = bot.get_chat_member(GROUP_CHAT_ID, user_id).status
        if status in ['member', 'administrator', 'creator']:
            return True
        else:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("➡️ THAM GIA LÒ RÈN TẠI ĐÂY ⬅️", url=f"https://t.me/{GROUP_CHAT_ID[1:]}"))
            bot.reply_to(message,
                         f"⚠️ **LỖI XÁC THỰC!**\n\nHệ thống phát hiện bạn chưa tham gia 'Lò Rèn' **{GROUP_CHAT_ID}**.\n\n"
                         f"Vui lòng **tham gia nhóm** để mở khóa Bot, sau đó quay lại đây và gõ /start.",
                         reply_markup=markup, parse_mode='Markdown')
            return False
    except Exception as e:
        print(f"Lỗi check join: {e}")
        bot.reply_to(message, f"🚫 **Lỗi Hệ Thống (ADMIN)!** 🚫\nBot không thể quét danh sách thành viên.\n"
                             f"Vui lòng liên hệ Admin ({safe_admin_username}) và báo: 'Bot Tặng Code chưa được thêm vào nhóm {GROUP_CHAT_ID}'.", parse_mode='Markdown')
        return False

# --- MODULE 1: XỬ LÝ LỆNH /start (V6.8 - ĐÃ SỬA TÊN HÀM) ---
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    safe_admin_username = ADMIN_USERNAME.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')
    
    is_new_invite = False 
    
    users = load_users() 
    
    # 1. XỬ LÝ MỜI BẠN
    referral_code = message.text.split()
    if len(referral_code) > 1:
        referrer_id = referral_code[1]
        
        users, new_user_data = get_user(users, user_id) 
        
        if new_user_data["is_new_user"] and str(referrer_id) != str(user_id):
            new_user_data["is_new_user"] = False 
            new_user_data["invited_by"] = referrer_id
            
            users, referrer_data = get_user(users, referrer_id) 
            referrer_data["invite_balance"] += INVITE_REWARD
            referrer_data["invited_count"] += 1
            
            save_users(users) 
            is_new_invite = True
            
            try:
                bot.send_message(referrer_id, f"🎉 Chúc mừng! {user_name} đã tham gia qua link của cậu. Cậu nhận được +{INVITE_REWARD:,} VNĐ vào số dư [Mời Bạn].")
            except Exception as e:
                print(f"Không gửi được tin cho thằng mời: {e}")
                
            bot.reply_to(message, f"Bạn đã tham gia qua lời mời của User ID: {referrer_id}.")
            
    # 2. KIỂM TRA "CÁNH CỔNG"
    if not check_if_joined(user_id, message): 
        return 

    # 3. KÍCH HOẠT PHỄU (NẾU ĐÃ JOIN)
    if not is_new_invite:
        users, user_data = get_user(load_users(), user_id) 
    else:
        users, user_data = get_user(load_users(), user_id) 
        
    user_data["username"] = user_name 
    save_users(users) 
    
    bot.send_message(user_id,
                     f"✅ **Xác thực thành công!** Chào mừng {user_name} đến với hệ thống Tặng Code FLY88.",
                     reply_markup=create_main_menu())
    
    if user_data.get("first_start", True) or is_new_invite:
        bot.send_message(user_id,
                         "Hệ thống ghi nhận 2 cách để cậu nhận 'Code' (quy đổi thành VNĐ):\n\n"
                         "1. 💸 **CON ĐƯỜNG MỜI BẠN BÈ**\n"
                         f"   (Tích lũy {INVITE_REWARD:,} VNĐ / 1 lượt mời. Min rút **{MIN_WITHDRAW_INVITE:,} VNĐ**)\n\n"
                         "2. 🔥 **CON ĐƯỜNG TÂN THỦ FLY88**\n"
                         f"   (Cách DỄ NHẤT: Hoàn thành 1 nhiệm vụ chơi để nhận **Lên đến {MIN_WITHDRAW_TASK:,} VNĐ** và RÚT NGAY!)\n\n"
                         "Vui lòng chọn 1 trong 2 con đường bằng cách sử dụng Menu bên dưới 👇",
                         parse_mode='Markdown')
        user_data["first_start"] = False
        save_users(users) 

# --- MODULE 3: XỬ LÝ CÁC NÚT BẤM MENU (V6.8 - SỬA TÊN HÀM) ---

# 1. Xử lý nút [Tài khoản]
@bot.message_handler(func=lambda message: message.text == BTN_TAIKHOAN)
def handle_taikhoan(message):
    user_id = message.from_user.id
    if not check_if_joined(user_id, message): return 
    
    users, user_data = get_user(load_users(), user_id) 
    response = (
        f"👤 **Tên:** {user_data.get('username', message.from_user.first_name)}\n"
        f"🆔 **ID:** `{user_id}` (Dùng ID này để Admin duyệt Rút tiền)\n"
        f"💰 **Số dư [Mời Bạn]:** {user_data.get('invite_balance', 0):,} VNĐ\n"
        f"💰 **Số dư [Nhiệm Vụ FLY88]:** {user_data.get('task_balance', 0):,} VNĐ\n"
        f"👥 **Số người đã mời:** {user_data.get('invited_count', 0)} người"
    )
    bot.reply_to(message, response, parse_mode='Markdown')

# 2. Xử lý nút [Mời bạn]
@bot.message_handler(func=lambda message: message.text == BTN_MOIBAN)
def handle_moiban(message):
    user_id = message.from_user.id
    if not check_if_joined(user_id, message): return 
    
    bot_username = bot.get_me().username
    users, user_data = get_user(load_users(), user_id) 
    
    response = (
        f"🎉 Mời bạn bè tham gia nhóm **{GROUP_CHAT_ID}** VÀ sử dụng Bot này để nhận **{INVITE_REWARD:,} VNĐ** / 1 lượt mời!\n"
        f"(Lưu ý: Bạn bè phải là người dùng thật & có tương tác)\n\n"
        f"🔗 **Link mời CÁ NHÂN của cậu:**\n"
        f"`https://t.me/{bot_username}?start={user_id}`\n"
        f"---"
        f"👥 Số người đã mời: {user_data.get('invited_count', 0)}\n"
        f"💰 Thưởng tạm tính: {user_data.get('invite_balance', 0):,} VNĐ (Min rút: {MIN_WITHDRAW_INVITE:,} VNĐ)"
    )
    bot.reply_to(message, response, parse_mode='Markdown')

# 3. Xử lý nút [Điểm danh]
@bot.message_handler(func=lambda message: message.text == BTN_DIEMDANH)
def handle_diemdanh(message):
    user_id = message.from_user.id
    if not check_if_joined(user_id, message): return 

    users, user_data = get_user(load_users(), user_id) 
    last_check_in_str = user_data.get('last_check_in')
    current_time = datetime.now()
    
    if last_check_in_str:
        last_check_in_time = datetime.fromisoformat(last_check_in_str)
        if current_time - last_check_in_time < timedelta(hours=24):
            time_left = timedelta(hours=24) - (current_time - last_check_in_time)
            hours_left = time_left.seconds // 3600
            minutes_left = (time_left.seconds % 3600) // 60
            bot.reply_to(message, f"🚫 Bạn đã điểm danh rồi. Vui lòng quay lại sau **{hours_left} giờ {minutes_left} phút** nữa.", parse_mode='Markdown')
            return

    user_data['invite_balance'] += DAILY_REWARD
    user_data['last_check_in'] = current_time.isoformat()
    save_users(users)
    
    bot.reply_to(message,
                 f"✅ **Điểm danh thành công!**\n"
                 f"+{DAILY_REWARD:,} VNĐ đã được cộng vào 'Số dư [Mời Bạn]'.\n\n"
                 f"Số dư [Mời Bạn] hiện tại: {user_data['invite_balance']:,} VNĐ (Min rút: {MIN_WITHDRAW_INVITE:,} VNĐ)", parse_mode='Markdown')

# 4. Xử lý nút [Thống kê] (V6.4 - NÂNG CẤP)
@bot.message_handler(func=lambda message: message.text == BTN_THONGKE)
def handle_thongke(message):
    if not check_if_joined(message.from_user.id, message): return 

    users = load_users()
    real_user_count = len(users)
    
    now = datetime.now()
    hours_running = (now - BOT_BIRTHDAY).total_seconds() / 3600
    
    time_based_users = int(hours_running * HOURLY_USER_GROWTH)
    time_based_money = int(hours_running * HOURLY_MONEY_GROWTH)
    
    displayed_users = FAKE_BASE_USERS + time_based_users + real_user_count
    displayed_money = FAKE_BASE_MONEY + time_based_money + (real_user_count * MONEY_PER_REAL_USER)
    
    response = (
        f"📊 **THỐNG KÊ HỆ THỐNG BOT:**\n"
        f"👥 Tổng người dùng: **{displayed_users:,}** người\n"
        f"💰 Tổng số tiền đã rút: **{displayed_money:,}** VNĐ"
    )
    bot.reply_to(message, response, parse_mode='Markdown')

# 5. Xử lý nút [Rút tiền] (V6.7 - ĐÃ VÁ LỖI)
@bot.message_handler(func=lambda message: message.text == BTN_RUTTIEN)
def handle_ruttien_info(message):
    user_id = message.from_user.id
    if not check_if_joined(user_id, message): return 
    
    users, user_data = get_user(load_users(), user_id) 
    safe_admin_username = ADMIN_USERNAME.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')

    response = (
        f"🏧 **HỆ THỐNG RÚT TIỀN:**\n\n"
        f"1. **Số dư [Mời Bạn]:** {user_data.get('invite_balance', 0):,} VNĐ\n"
        f"   (Min rút: **{MIN_WITHDRAW_INVITE:,} VNĐ**. Chỉ rút khi đủ Min.)\n\n"
        f"2. **Số dư [Nhiệm Vụ FLY88]:** {user_data.get('task_balance', 0):,} VNĐ\n"
        f"   (Min rút: **Lên đến {MIN_WITHDRAW_TASK:,} VNĐ**. Rút ngay khi hoàn thành nhiệm vụ.)\n" 
        f"---\n"
        f"Để rút tiền, vui lòng liên hệ Admin ({safe_admin_username}) để xác minh và làm lệnh."
    )
    bot.reply_to(message, response, parse_mode='Markdown')

# 6. Xử lý nút [Link game] (V6.7 - ĐÃ VÁ LỖI)
@bot.message_handler(func=lambda message: message.text == BTN_LINKGAME)
def handle_linkgame(message):
    if not check_if_joined(message.from_user.id, message): return 
    
    safe_admin_username = ADMIN_USERNAME.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')
    
    response = f"""
🔥 **CON ĐƯỜNG TÂN THỦ (CÁCH DỄ NHẤT ĐỂ RÚT {MIN_WITHDRAW_TASK:,}K)** 🔥

Đây là nhiệm vụ DUY NHẤT để nhận **Lên đến {MIN_WITHDRAW_TASK:,} VNĐ** tiền mặt (Rút ngay không cần mời bạn bè):

1.  **[➡️ BẤM VÀO ĐÂY ĐỂ ĐĂNG KÝ FLY88 ⬅️]({AGENT_LINK})**
    (Đăng ký tài khoản bằng link này)

2.  **Tổng Nạp** trong Tháng đạt **1.000.000 VNĐ**. 

3.  **Chụp ảnh LỊCH SỬ NẠP** và gửi ngay cho Admin ({safe_admin_username}).

Admin sẽ duyệt và cộng CODE FLY88 vào 'Số dư [Nhiệm Vụ FLY88]' để cậu rút ngay lập tức!
    """
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("➡️ BẤM VÀO ĐÂY ĐỂ ĐĂNG KÝ FLY88 ⬅️", url=AGENT_LINK))
    
    bot.reply_to(message, response, parse_mode='Markdown', reply_markup=markup)

# --- MODULE 4: KIẾN TRÚC "LOA PHƯỜNG" (V6.15 MỚI - GIỮ ID CHẶN) ---
@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    # 1. KIỂM TRA "Ổ KHOÁ 2"
    if str(message.from_user.id) != str(ADMIN_ID):
        bot.reply_to(message, "🚫 Mày không phải 'Chủ'. Cút.")
        return

    # 2. XÁC ĐỊNH CHẾ ĐỘ PHÁT SÓNG
    is_media = False
    media_file_id = None
    media_type = None
    caption = None
    
    # Kịch bản 1: Cậu TRẢ LỜI vào một bức ảnh/video/document
    if message.reply_to_message:
        replied_msg = message.reply_to_message
        
        if replied_msg.photo:
            is_media = True
            media_type = 'photo'
            media_file_id = replied_msg.photo[-1].file_id 
            caption = replied_msg.caption if replied_msg.caption else ""
        elif replied_msg.video:
            is_media = True
            media_type = 'video'
            media_file_id = replied_msg.video.file_id
            caption = replied_msg.caption if replied_msg.caption else ""
        elif replied_msg.document:
            is_media = True
            media_type = 'document'
            media_file_id = replied_msg.document.file_id
            caption = replied_msg.caption if replied_msg.caption else ""
        
    # Lấy nội dung TEXT (của lệnh /broadcast)
    try:
        text_content = message.text.split(maxsplit=1)[1] 
        if is_media:
            caption = text_content
        else:
            caption = text_content
            
    except IndexError:
        if not is_media:
            bot.reply_to(message, "🚫 Lỗi cú pháp! Gõ:\n`/broadcast [Nội dung tin nhắn]`\nHoặc:\n**TRẢ LỜI** vào ảnh/video và gõ `/broadcast [Caption]`")
            return
    
    # 3. THI CÔNG "PHÁT LOA"
    users = load_users()
    user_ids_to_send = list(users.keys()) # Lấy danh sách ID
    
    if is_media:
        bot.reply_to(message, f"📣 Bắt đầu 'Phát Ảnh/Video' cho {len(user_ids_to_send)} 'gà'. Chờ...")
    else:
        bot.reply_to(message, f"📣 Bắt đầu 'Phát Loa Text' cho {len(user_ids_to_send)} 'gà'. Chờ...")

    sent_count = 0
    blocked_count = 0

    for user_id_str in user_ids_to_send:
        user_id = int(user_id_str)
        try:
            if is_media:
                # Gửi MEDIA
                if media_type == 'photo':
                    bot.send_photo(user_id, media_file_id, caption=caption, parse_mode='Markdown')
                elif media_type == 'video':
                    bot.send_video(user_id, media_file_id, caption=caption, parse_mode='Markdown')
                elif media_type == 'document':
                    bot.send_document(user_id, media_file_id, caption=caption, parse_mode='Markdown')
            else:
                # Gửi TEXT thuần
                bot.send_message(user_id, caption, parse_mode='Markdown')
            
            # --- ĐẾM THÀNH CÔNG (FIXED V6.13) ---
            sent_count += 1
            
        except telebot.apihelper.ApiTelegramException as e:
            # --- ĐẾM LỖI (V6.15: KHÔNG XÓA ID) ---
            if e.result_json.get('error_code') in [403, 400]:
                blocked_count += 1
            
        except Exception as e:
            # Bắt các lỗi khác
            blocked_count += 1
            
        time.sleep(0.1) 

    # 4. KHÔNG XÓA ID (V6.15) - Chỉ lưu lại dữ liệu (đã được làm ở các module khác)

    # 5. BÁO CÁO CHO "CHỦ"
    bot.reply_to(message, f"✅ **'LOA PHƯỜNG' HOÀN TẤT!**\n\n"
                          f"📬 Đã gửi thành công: **{sent_count}** 'gà'\n"
                          f"🛡️ Đã chặn bot/lỗi: **{blocked_count}** 'gà' (Tổng số ID trong DB: **{len(users)}**)", parse_mode='Markdown')

# --- MODULE 5: KIẾN TRÚC "BÁO CÁO" (V6.10) ---

# Lệnh "Hút" DB thủ công
@bot.message_handler(commands=['getdb'])
def handle_get_db(message):
    # 1. KIỂM TRA "Ổ KHOÁ 2"
    if str(message.from_user.id) != str(ADMIN_ID):
        bot.reply_to(message, "🚫 Mày không phải 'Chủ'. Cút.")
        return
        
    # 2. "HÚT" FILE
    try:
        if not os.path.exists(DB_FILE):
            bot.reply_to(message, "🚫 Lỗi: Không tìm thấy file `users_database.json`.")
            return
            
        with open(DB_FILE, 'rb') as f:
            bot.send_document(ADMIN_ID, f, caption="File backup 'gà' (Hút thủ công)")
            
    except Exception as e:
        bot.reply_to(message, f"🚫 Lỗi khi 'hút' file: {e}")

# "Cỗ Máy Thời Gian" Tự Động Backup
def send_daily_backup():
    if ADMIN_ID == 123456789: # Kiểm tra xem "Chủ" đã thay ID chưa
        print("!!! CẢNH BÁO: ADMIN_ID chưa được thay đổi. 'Lò' Tự Động Backup sẽ KHÔNG chạy.")
        return # Dừng "Lò" này lại

    while True:
        # 1. Chờ 24 giờ
        print(f"[V6.15 Backup] Đã ngủ. Sẽ backup sau 24 giờ...")
        time.sleep(24 * 60 * 60) # 86400 giây
        
        # 2. "Hút" File
        try:
            if not os.path.exists(DB_FILE):
                bot.send_message(ADMIN_ID, f"🚫 Lỗi Backup Tự Động: Không tìm thấy file `{DB_FILE}`.")
            else:
                with open(DB_FILE, 'rb') as f:
                    bot.send_document(ADMIN_ID, f, caption=f"💾 Backup 'Gà' Tự Động\nNgày: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"[V6.15 Backup] Đã gửi backup tự động cho 'Chủ'.")
            
        except Exception as e:
            print(f"!!! Lỗi nghiêm trọng 'Lò' Tự Động Backup: {e}")
            try:
                bot.send_message(ADMIN_ID, f"🚫 Lỗi nghiêm trọng 'Lò' Tự Động Backup: {e}")
            except:
                pass 

# --- CHẠY BOT (V6.15 - "TỐI ƯU HÓA") ---
if __name__ == "__main__":
    print("🚀 Bắt đầu khởi chạy 'cỗ máy' V6.15 (FIX BÁO CÁO & GIỮ TẤT CẢ ID)...")
    
    # 1. Khởi chạy "Lò" Tự Động Backup (luồng riêng)
    backup_thread = threading.Thread(target=send_daily_backup, daemon=True)
    backup_thread.start()
    print("... 'Lò' Tự Động Backup đã bật.")

    # 2. Khởi chạy "Lò" Chính (luồng chính)
    print("... 'Lò' Chính (Polling) đang chạy 24/7.")
    bot.polling(none_stop=True)
