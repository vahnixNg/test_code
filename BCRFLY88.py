import telebot
import hashlib
import struct
from datetime import datetime
import time
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- TRUNG TÂM ĐIỀU KHIỂN CỦA BẠN (3 Ổ KHOÁ) ---

# Ổ KHOÁ 1: Chìa khoá Bot
BOT_TOKEN = "8344681329:AAF32xV_xpd5X-EU_k4RW_fXyM4pBsSjy0o"

# Ổ KHOÁ 2: ID Admin của bạn
ADMIN_ID = 8356373953

# Ổ KHOÁ 3: Username Admin của bạn (để gà liên hệ)
ADMIN_USERNAME = "@NamSky88"

# --- CƠ SỞ DỮ LIỆU CỦA PHỄU (BẠN CÓ THỂ SỬA/THÊM SAU) ---

# "Sổ Trắng" (Whitelist) - Người được duyệt
authorized_users = {8196174785,6178840800,7436004129,
    ADMIN_ID
}

# "Bản Đồ Phễu" - Sảnh và Bàn
BACCARAT_DATABASE = {
    "AE SEXY": ['C05', 'C06', 'C07', 'C15', 'C01', 'C02', 'C03', 'C04', 'C08', 'C09', 'C10', 'C16', '1', '2', '3', '4',
                '5', '6', '7', '8', '10', 'C11', 'C12', 'C13', 'C14'],
    "DG": ['D01', 'D02', 'D03', 'D05', 'D06', 'D07', 'D08', 'A01', 'A02', 'A03', 'A05']
    # Thêm các sảnh khác vào đây
}

# "Bộ Nhớ Tạm" - Lưu trữ quá trình "gà" nhập cầu
BACCARAT_SESSIONS = {}

# --- KHỞI TẠO HỆ THỐNG ---
bot = telebot.TeleBot(BOT_TOKEN)


# --- PHẦN LÕI "UY TÍN GIẢ LẬP" (V4.6) ---
class BaccaratPredictor:
    def advanced_baccarat_analysis(self, cau_string):
        """Phân tích cầu nâng cao - KHÔNG RANDOM"""
        md5_hash = hashlib.md5(cau_string.encode()).hexdigest()
        hash_parts = [md5_hash[i:i + 8] for i in range(0, 32, 8)]
        numbers = [int(part, 16) for part in hash_parts]
        total_sum = sum(numbers)
        product = 1
        for num in numbers[:4]: product *= (num % 1000) + 1
        binary_pattern = bin(int(md5_hash[:16], 16))[2:].zfill(64)
        ones_count = binary_pattern.count('1')
        zeros_count = binary_pattern.count('0')

        banker_score = 0
        player_score = 0

        if total_sum % 2 == 0:
            banker_score += 35
        else:
            player_score += 35
        if ones_count > zeros_count:
            banker_score += 25
        else:
            player_score += 25
        if product % 2 == 0:
            banker_score += 20
        else:
            player_score += 20
        if numbers[0] % 2 == 0:
            banker_score += 10
        else:
            player_score += 10
        if int(md5_hash[-1], 16) >= 8:
            banker_score += 10
        else:
            player_score += 10

        if banker_score > player_score:
            prediction = "BANKER (CÁI)"
            confidence = (banker_score / (banker_score + player_score)) * 100
        else:
            prediction = "PLAYER (CON)"
            confidence = (player_score / (player_score + player_score)) * 100

        return {
            'prediction': prediction,
            'confidence': round(confidence, 2)
        }


predictor = BaccaratPredictor()


# --- MODULE 1: LỆNH PHÂN QUYỀN (CHỈ ADMIN DÙNG) ---
def is_admin(user_id):
    return user_id == ADMIN_ID


@bot.message_handler(commands=['approve'])
def approve_user(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Bạn không có quyền dùng lệnh này.")
        return
    try:
        user_id_to_approve = int(message.text.split()[1])
        authorized_users.add(user_id_to_approve)
        bot.reply_to(message, f"✅ ĐÃ CẤP QUYỀN (Baccarat) cho User ID: {user_id_to_approve}")
        bot.send_message(user_id_to_approve,
                         "🎉 **XIN CHÚC MỪNG!**\nTài khoản Bot Baccarat của bạn đã được Admin duyệt.")
    except Exception as e:
        bot.reply_to(message, "Lỗi cú pháp. Dùng: /approve <USER_ID>")


# (Thêm /revoke, /listusers nếu bạn muốn, tôi ẩn đi cho code gọn)

# --- MODULE 2: LỆNH CHO NGƯỜI DÙNG (Phễu V4.8) ---

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    # "Bảo vệ" username admin khỏi lỗi Markdown
    safe_admin_username = ADMIN_USERNAME.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')

    welcome = f"""
🎰 **BOT PHÂN TÍCH CẦU BACCARAT FLY88 (Bản chỉ dành cho web FLY88)** 🎰

Chào mừng {message.from_user.first_name},

Đây là công cụ AI ĐỘC QUYỀN, phân tích dữ liệu cầu bạn nhập vào để đưa ra dự đoán có độ tin cậy cao.

⚠️ **TRẠNG THÁI TRUY CẬP:** {"✅ **ĐÃ KÍCH HOẠT**" if user_id in authorized_users else f"🚫 **CHƯA KÍCH HOẠT** (Liên hệ: {safe_admin_username})"}

Để được cấp quyền sử dụng Bot:
1.  **Đăng ký** tài khoản qua link đại lý của Admin.
2.  **Nạp tiền** lần đầu để kích hoạt tài khoản.
3.  **Liên hệ Admin** ({safe_admin_username}) để được duyệt.

Nếu bạn đã được duyệt, sử dụng lệnh:
`/scanbcr` (Để bắt đầu quét)
    """
    bot.reply_to(message, welcome, parse_mode='Markdown')


@bot.message_handler(commands=['getid'])
def get_id(message):
    user_id = message.from_user.id
    safe_admin_username = ADMIN_USERNAME.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')
    bot.reply_to(message,
                 f"🆔 User ID Telegram của bạn là:\n`{user_id}`\n\n(Gửi ID này cho Admin {safe_admin_username} để được duyệt)",
                 parse_mode='Markdown')


@bot.message_handler(commands=['scanbcr'])
def scan_bcr_start(message):
    user_id = message.from_user.id
    safe_admin_username = ADMIN_USERNAME.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')

    if user_id not in authorized_users:
        bot.reply_to(message,
                     f"🚫 **TRUY CẬP BỊ TỪ CHỐI** 🚫\nVui lòng liên hệ Admin ({safe_admin_username}) để đăng ký và kích hoạt.",
                     parse_mode='Markdown')
        return

    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    buttons = [InlineKeyboardButton(sanh_name, callback_data=f"sanh_{sanh_name}") for sanh_name in
               BACCARAT_DATABASE.keys()]
    markup.add(*buttons)
    bot.reply_to(message, "✅ **ĐÃ XÁC THỰC.**\nVui lòng chọn SẢNH BACCARAT bạn đang chơi:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('sanh_'))
def handle_sanh_choice(call):
    user_id = call.from_user.id
    if user_id not in authorized_users:
        bot.answer_callback_query(call.id, "🚫 TRUY CẬP BỊ TỪ CHỐI.", show_alert=True)
        return

    sanh_name = call.data.split('_', 1)[1]
    BACCARAT_SESSIONS[user_id] = {"sanh": sanh_name, "ban": None, "cau": ""}

    markup = InlineKeyboardMarkup()
    markup.row_width = 5
    buttons = []
    if sanh_name in BACCARAT_DATABASE:
        for ban_name in BACCARAT_DATABASE[sanh_name]:
            buttons.append(InlineKeyboardButton(ban_name, callback_data=f"ban_{ban_name}"))

    markup.add(*buttons)
    bot.edit_message_text(f"Đã chọn sảnh [{sanh_name}].\nVui lòng chọn BÀN CƯỢC bạn đang chơi:",
                          call.message.chat.id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('ban_'))
def handle_ban_choice(call):
    user_id = call.from_user.id
    if user_id not in authorized_users or user_id not in BACCARAT_SESSIONS:
        bot.answer_callback_query(call.id, "🚫 Lỗi phiên làm việc. Gõ /scanbcr để bắt đầu lại.", show_alert=True)
        return

    ban_name = call.data.split('_', 1)[1]
    BACCARAT_SESSIONS[user_id]["ban"] = ban_name
    BACCARAT_SESSIONS[user_id]["cau"] = ""  # Reset cầu

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔴 BANKER (Cái)", callback_data="cau_B"),
               InlineKeyboardButton("🔵 PLAYER (Con)", callback_data="cau_P"))

    bot.edit_message_text(f"Đã khoá mục tiêu: Sảnh [{BACCARAT_SESSIONS[user_id]['sanh']}] - Bàn [{ban_name}]\n\n"
                          f"**LỊCH SỬ CẦU:** (Chưa có)\n"
                          f"**VÁN 1:** Vui lòng chọn (từ CŨ nhất đến MỚI nhất):",
                          call.message.chat.id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('cau_'))
def handle_cau_input(call):
    user_id = call.from_user.id
    if user_id not in authorized_users or user_id not in BACCARAT_SESSIONS:
        bot.answer_callback_query(call.id, "🚫 Lỗi phiên làm việc. Gõ /scanbcr để bắt đầu lại.", show_alert=True)
        return

    choice = call.data.split('_', 1)[1]  # 'B' hoặc 'P'
    session = BACCARAT_SESSIONS[user_id]
    session["cau"] += choice

    current_cau_string = " - ".join(session["cau"])

    if len(session["cau"]) < 5:
        # --- TIẾP TỤC NHẬP CẦU ---
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔴 BANKER (Cái)", callback_data="cau_B"),
                   InlineKeyboardButton("🔵 PLAYER (Con)", callback_data="cau_P"))

        bot.edit_message_text(f"Đã khoá mục tiêu: Sảnh [{session['sanh']}] - Bàn [{session['ban']}]\n\n"
                              f"**LỊCH SỬ CẦU:** `{current_cau_string}`\n"
                              f"**VÁN {len(session['cau']) + 1}:** Vui lòng chọn:",
                              call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')
    else:
        # --- ĐỦ 5 CẦU -> CHẠY BLACK BOX (Lần đầu) ---
        run_black_box_prediction(call, session)


def run_black_box_prediction(call, session):
    """
    Đây là "Lõi Bất Tử" V4.8 - "Cố Vấn Liên Tục"
    """
    try:
        # 1. "Màn Kịch"
        bot.edit_message_text(f"**LỊCH SỬ CẦU:** `{" - ".join(session['cau'])}`\n"
                              f"Đang phân tích chuỗi cầu...\n"
                              f"Chạy **Giải Thuật Phân Tích Cầu AI 7.0**...",
                              call.message.chat.id, call.message.message_id, parse_mode='Markdown')
        time.sleep(random.randint(3, 5))

        # 2. "Lõi" Phân Tích (V4.6)
        result = predictor.advanced_baccarat_analysis(session["cau"])

        # 3. "Cú Chốt Hạ" (V4.7 - Ngẫu nhiên 2 kịch bản)
        choice = random.choice([1, 2, 3])  # 33% cơ hội ra lời khuyên
        response = ""

        if choice <= 2:  # 66% Phán Quyết Cứng
            response = f"""
**[PHÂN TÍCH AI - BÀN {session['ban']} HOÀN TẤT]**
---------------------------------
**CẦU ĐÃ NHẬP:** `{" - ".join(session['cau'])}`
**THUẬT TOÁN:** Giải Thuật Phân Tích Cầu AI 7.0

**=> DỰ ĐOÁN VÁN TIẾP THEO (Tay thứ {len(session['cau']) + 1}):**
🔥 **{result['prediction']}** 🔥

**ĐỘ TIN CẬY (TÍNH TOÁN):** **{result['confidence']}%**

*Kỷ luật! Theo 1 tay, gãy bỏ qua!*
            """
        else:  # 33% Phán Quyết Kèm Lời Khuyên
            response = f"""
**[PHÂN TÍCH AI - BÀN {session['ban']} HOÀN TẤT]**
---------------------------------
**CẦU ĐÃ NHẬP:** `{" - ".join(session['cau'])}`
**THUẬT TOÁN:** Giải Thuật Phân Tích Cầu AI 7.0

**=> DỰ ĐOÁN VÁN TIẾP THEO (Tay thứ {len(session['cau']) + 1}):**
🔥 **{result['prediction']}** 🔥

**ĐỘ TIN CẬY (TÍNH TOÁN):** **{result['confidence']}%**

**=> LỜI KHUYÊN CHIẾN LƯỢC:**
AI phát hiện "Thế Cầu Gãy". Độ tin cậy {result['confidence']}% là cao, nhưng vẫn có rủi ro. Khuyến nghị **VÀO VỐN NHỎ** (lót) ở tay này.
            """

        # --- ĐÂY LÀ NÂNG CẤP V4.8 ---
        # Thêm 2 nút bấm mới
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(
            InlineKeyboardButton("1. ✅ Nhập Kết Quả Ván Vừa Rồi", callback_data="next_hand_input"),
            InlineKeyboardButton("2. 🔄 Reset (Đổi Bàn/Bắt Đầu Lại)", callback_data="reset_session")
        )

        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode='Markdown',
                              reply_markup=markup)

    except Exception as e:
        bot.edit_message_text(f"Lỗi hệ thống phân tích. Vui lòng thử lại sau. \nChi tiết: {e}",
                              call.message.chat.id, call.message.message_id)
        # Không xoá session, để user thử lại


@bot.callback_query_handler(func=lambda call: call.data == 'reset_session')
def handle_reset_session(call):
    """
    Xử lý khi "gà" bấm nút "2. Reset"
    """
    user_id = call.from_user.id
    if user_id in BACCARAT_SESSIONS:
        del BACCARAT_SESSIONS[user_id]

    bot.edit_message_text("✅ Đã reset phiên làm việc.\n\nGõ /scanbcr để bắt đầu lại một phiên quét mới.",
                          call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "Đã reset!")


@bot.callback_query_handler(func=lambda call: call.data == 'next_hand_input')
def handle_next_hand_input(call):
    """
    Xử lý khi "gà" bấm nút "1. Nhập Kết Quả"
    """
    user_id = call.from_user.id
    if user_id not in BACCARAT_SESSIONS:
        bot.answer_callback_query(call.id, "🚫 Lỗi phiên làm việc. Gõ /scanbcr để bắt đầu lại.", show_alert=True)
        return

    # Bot sẽ hỏi "gà" ván vừa rồi ra gì
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔴 BANKER (Cái)", callback_data="update_cau_B"),
               InlineKeyboardButton("🔵 PLAYER (Con)", callback_data="update_cau_P"))

    session = BACCARAT_SESSIONS[user_id]
    bot.edit_message_text(f"**LỊCH SỬ CẦU CŨ:** `{" - ".join(session['cau'])}`\n\n"
                          f"Vui lòng nhập **KẾT QUẢ** của ván vừa rồi (Tay thứ {len(session['cau']) + 1}):",
                          call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data.startswith('update_cau_'))
def handle_update_cau(call):
    """
    Bắt lấy kết quả (B hoặc P), cập nhật lại cầu, và PHÁN TIẾP
    """
    user_id = call.from_user.id
    if user_id not in BACCARAT_SESSIONS:
        bot.answer_callback_query(call.id, "🚫 Lỗi phiên làm việc. Gõ /scanbcr để bắt đầu lại.", show_alert=True)
        return

    choice = call.data.split('_', 2)[2]  # 'B' hoặc 'P'
    session = BACCARAT_SESSIONS[user_id]

    # --- Logic "Bất Tử" (Cập nhật cầu 5 tay) ---
    new_cau_string = session["cau"]

    if len(new_cau_string) < 5:
        new_cau_string += choice
    else:
        # "Quên" tay đầu tiên và "thêm" tay mới
        # Ví dụ: "BBPBP" + "B" -> "BPBPB"
        new_cau_string = new_cau_string[1:] + choice

    session["cau"] = new_cau_string  # Cập nhật session

    # --- Gọi lại hàm "Black Box" để phán tiếp ---
    # "Gà" sẽ bị kẹt trong vòng lặp này mãi mãi
    run_black_box_prediction(call, session)


# --- CHẠY BOT ---
if __name__ == "__main__":
    print("🚀 Bot Baccarat V4.8 (Cố Vấn Liên Tục) đang chạy...")
    bot.polling(none_stop=True)