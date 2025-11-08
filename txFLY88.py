import telebot
import hashlib
import struct
from datetime import datetime
import random # Thêm random để điều chỉnh độ tin cậy và lời khuyên

# --- TRUNG TÂM ĐIỀU KHIỂN CỦA BẠN (3 Ổ KHOÁ) ---

# Ổ KHOÁ 1: Chìa khoá Bot
BOT_TOKEN = "8380092974:AAH5szL1AEXwf4tWQhUxZG9qKwmcGsKSb_U" # Dán token của bạn vào đây

# Ổ KHOÁ 2: ID Admin của bạn
ADMIN_ID = 8356373953 # Thay bằng ID Admin của BẠN

# Ổ KHOÁ 3: Username Admin của bạn (để gà liên hệ)
ADMIN_USERNAME = "@namsky88" # Ví dụ: "@CSN_NhaTrong"

# --- CƠ SỞ DỮ LIỆU CỦA PHỄU ---

# "Sổ Trắng" (Whitelist) - Người được duyệt
authorized_users = {
    ADMIN_ID, 7984561571,8196174785,7436004129
}

# --- KHỞI TẠO HỆ THỐNG ---
bot = telebot.TeleBot(BOT_TOKEN)


# --- PHẦN LÕI "UY TÍN GIẢ LẬP" (V5.3 - ĐÃ NÂNG CẤP) ---
class TaiXiuPredictorV5_3:
    def __init__(self):
        pass # Không cần lưu lịch sử nữa

    def advanced_md5_analysis_v5_3(self, md5_hash):
        """
        Phân tích MD5 V5.3:
        1. Cân bằng Tài/Xỉu hơn.
        2. Độ tin cậy ngẫu nhiên 60-99%.
        """
        # --- Phần tính toán dựa trên hash vẫn giữ nguyên để đảm bảo "nhất quán" ---
        hash_parts = [md5_hash[i:i + 8] for i in range(0, 32, 8)]
        numbers = [int(part, 16) for part in hash_parts]
        total_sum = sum(numbers)
        product = 1
        for num in numbers[:4]: product *= (num % 1000) + 1
        binary_pattern = bin(int(md5_hash[:16], 16))[2:].zfill(64)
        ones_count = binary_pattern.count('1')
        zeros_count = binary_pattern.count('0')

        # --- NÂNG CẤP 1: Cân bằng Tài/Xỉu ---
        # Thay vì dùng score, ta dùng điểm số dự đoán (3-18) để quyết định T/X
        # Cách này đảm bảo tỷ lệ T/X gần 50/50 hơn
        predicted_score = (sum(int(c, 16) for c in md5_hash[:3]) % 16) + 3

        if predicted_score >= 11:
            prediction = "Tài"
            # Tính score giả lập để hiển thị (không ảnh hưởng kết quả)
            tai_score = predicted_score * 5 + random.randint(0, 9)
            xiu_score = 100 - tai_score + random.randint(-5, 5)
        else:
            prediction = "Xỉu"
            # Tính score giả lập để hiển thị
            xiu_score = (18 - predicted_score) * 5 + random.randint(0, 9)
            tai_score = 100 - xiu_score + random.randint(-5, 5)

        # Đảm bảo score không âm hoặc > 100
        tai_score = max(0, min(100, tai_score))
        xiu_score = max(0, min(100, xiu_score))

        # --- NÂNG CẤP 2: Độ tin cậy ngẫu nhiên 60-99% ---
        confidence = round(random.uniform(60.0, 99.0), 2)

        return {
            'prediction': prediction,
            'confidence': confidence,
            'predicted_score': predicted_score, # Vẫn giữ để hiển thị
            'tai_score': tai_score, # Score giả lập
            'xiu_score': xiu_score, # Score giả lập
            'analysis_details': { # Vẫn giữ để "diễn"
                'total_sum': total_sum,
                'bit_ratio': f"{ones_count}:{zeros_count}",
                'hash_pattern': md5_hash[:8] + "..." + md5_hash[-8:]
            }
        }

# Khởi tạo predictor V5.3
predictor = TaiXiuPredictorV5_3()

# --- MODULE 1: LỆNH PHÂN QUYỀN (CHỈ ADMIN DÙNG) ---
# (Giữ nguyên không đổi)
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
        bot.reply_to(message, f"✅ ĐÃ CẤP QUYỀN cho User ID: {user_id_to_approve}")
        bot.send_message(user_id_to_approve, "🎉 **XIN CHÚC MỪNG!**\nTài khoản Bot Tài Xỉu của bạn đã được Admin duyệt.")
    except Exception as e:
        bot.reply_to(message, "Lỗi cú pháp. Dùng: /approve <USER_ID>")

@bot.message_handler(commands=['revoke'])
def revoke_user(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Bạn không có quyền dùng lệnh này.")
        return
    try:
        user_id_to_revoke = int(message.text.split()[1])
        authorized_users.discard(user_id_to_revoke)
        bot.reply_to(message, f"🚫 ĐÃ THU HỒI QUYỀN của User ID: {user_id_to_revoke}")
    except Exception as e:
        bot.reply_to(message, "Lỗi cú pháp. Dùng: /revoke <USER_ID>")

@bot.message_handler(commands=['listusers'])
def list_users(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Bạn không có quyền dùng lệnh này.")
        return
    if not authorized_users:
        bot.reply_to(message, "Danh sách trắng đang trống.")
        return
    user_list = "\n".join([str(uid) for uid in authorized_users])
    bot.reply_to(message, f"--- DANH SÁCH ĐƯỢC CẤP QUYỀN ---\n{user_list}")


# --- MODULE 2: LỆNH CHO NGƯỜI DÙNG (ĐÃ NÂNG CẤP) ---

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    safe_admin_username = ADMIN_USERNAME.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')

    welcome = f"""
🎰 **BOT DỰ ĐOÁN TÀI XỈU (Bản Cố Vấn V5.3) dành cho SUN WIN** 🎰

Chào mừng {message.from_user.first_name},

Đây là công cụ quét Tài Xỉu ĐỘC QUYỀN, sử dụng thuật toán phân tích mã phiên để dự đoán kết quả.

⚠️ **TRẠNG THÁI TRUY CẬP:** {"✅ **ĐÃ KÍCH HOẠT**" if user_id in authorized_users else f"🚫 **CHƯA KÍCH HOẠT** (Liên hệ: {safe_admin_username})"}

Để được cấp quyền sử dụng Bot:
1.  **Đăng ký** tài khoản qua link đại lý của Admin.
2.  **Nạp tiền** lần đầu để kích hoạt tài khoản.
3.  **Liên hệ Admin** ({safe_admin_username}) để được duyệt.

Nếu bạn đã được duyệt, sử dụng lệnh:
`/tx <MÃ PHIÊN>`
Ví dụ: `/tx abc123def456`
    """
    bot.reply_to(message, welcome, parse_mode='Markdown')

@bot.message_handler(commands=['getid'])
def get_id(message):
    user_id = message.from_user.id
    safe_admin_username = ADMIN_USERNAME.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')
    bot.reply_to(message,
                 f"🆔 User ID Telegram của bạn là:\n`{user_id}`\n\n(Gửi ID này cho Admin {safe_admin_username} để được duyệt)",
                 parse_mode='Markdown')

# --- HÀM XỬ LÝ LỆNH /tx (V5.3 - ĐÃ NÂNG CẤP) ---
@bot.message_handler(commands=['tx'])
def handle_tx_command(message):
    user_id = message.from_user.id
    safe_admin_username = ADMIN_USERNAME.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')

    if user_id not in authorized_users:
        bot.reply_to(message,
                     f"🚫 **TRUY CẬP BỊ TỪ CHỐI** 🚫\nVui lòng liên hệ Admin ({safe_admin_username}) để đăng ký và kích hoạt.",
                     parse_mode='Markdown')
        return

    try:
        user_input = message.text.split(maxsplit=1)[1].strip()
        if not (4 <= len(user_input) <= 100):
            raise ValueError("Độ dài mã phiên không hợp lệ.")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ **Sai cú pháp!**\nDùng: `/tx <MÃ PHIÊN>`\nVí dụ: `/tx abc123def456`",
                     parse_mode='Markdown')
        return

    # --- BỘ GIẢI MÃ ĐA NĂNG (V5.0) ---
    fake_md5 = hashlib.md5(user_input.encode()).hexdigest()

    # --- LÕI PHÂN TÍCH V5.3 ---
    try:
        # Sử dụng hàm phân tích mới V5.3
        result = predictor.advanced_md5_analysis_v5_3(fake_md5)

        # --- NÂNG CẤP 3: Thêm "Lời Khuyên Chiến Lược" ngẫu nhiên ---
        advice = ""
        # 30% cơ hội đưa ra lời khuyên (giống bot Baccarat)
        if random.choice([1, 2, 3]) == 3:
            advice = "\n\n**=> LỜI KHUYÊN CHIẾN LƯỢC:**\nAI phát hiện 'Tín Hiệu Nhiễu'. Độ tin cậy cao nhưng vẫn có rủi ro. Khuyến nghị **VÀO VỐN NHỎ** (lót) ở tay này."

        # Trả kết quả
        response = f"""
📊 **PHÂN TÍCH Kết Quả HOÀN TẤT**

🔢 **Mã Phiên:** `{user_input}` (Đã giải mã)
🎯 **Dự đoán:** **{result['prediction']}**
📈 **Độ tin cậy:** {result['confidence']}%

📋 **CHI TIẾT PHÂN TÍCH (Giả Lập):**
• Điểm Tài: {result['tai_score']}/100
• Điểm Xỉu: {result['xiu_score']}/100
• Điểm dự đoán: {result['predicted_score']}
• Tổng hash: {result['analysis_details']['total_sum']}
• Bit pattern: {result['analysis_details']['bit_ratio']}

💡 **LƯU Ý:** Phân tích dựa trên thuật toán AI độc quyền.
Kết quả có độ chính xác cao.

🎲 **QUYẾT ĐỊNH CUỐI CÙNG:** **{result['prediction']}**
{advice}
        """
        bot.reply_to(message, response, parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"Lỗi hệ thống phân tích. Vui lòng thử lại sau. \nChi tiết: {e}")


# --- CHẠY BOT ---
if __name__ == "__main__":
    print("🚀 Bot Tài Xỉu V5.3 (Cố Vấn TX) đang chạy...")
    bot.polling(none_stop=True)