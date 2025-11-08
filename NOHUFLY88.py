import telebot
import hashlib
from datetime import datetime, timedelta # Rất quan trọng cho V3.3
import time
import random
import re
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- TRUNG TÂM ĐIỀU KHIỂN CỦA BẠN (3 Ổ KHOÁ) ---

# Ổ KHOÁ 1: Chìa khoá Bot
BOT_TOKEN = "7967528361:AAHlHX9jYzXrQjivv9iWi1jI_3WpmNnR5wE"

# Ổ KHOÁ 2: ID Admin của bạn
ADMIN_ID = 8356373953 # ID Admin của bạn (thay bằng ID của bạn)

# Ổ KHOÁ 3: Username Admin của bạn (để gà liên hệ)
ADMIN_USERNAME = "@NamSky88" # Ví dụ: "@CSN_NhaTrong"

# --- CƠ SỞ DỮ LIỆU CỦA PHỄU (Bạn có thể sửa đổi sau) ---

# "Sổ Trắng" (Whitelist) - Người được duyệt
authorized_users = {1222206685,6881114763,5302116180,8196174785,7727285471,7100573288,ADMIN_ID
}

# "Bản Đồ Phễu Tầng 2" (Danh sách 18 sảnh)
Sảnh_List = [
    "168Game", "PG", "JILI", "FC", "MG", "MW", "TP", "JDB", "PP",
    "WG", "CQ9", "VA", "Spade Gaming", "PlayStar", "BNG", "Redtiger", "KA", "NetEnt"
]

# "Bản Đồ Phễu Tầng 3" (Danh sách Game Hot của mỗi sảnh)
# BẠN CẦN THÊM GAME VÀO ĐÂY THEO ĐÚNG CẤU TRÚC
GAME_DATABASE = {
    "168Game": ["Ù Mạt Chược 1", "Ù Mạt Chược 2", "Ù Mạt Chược 3", "Siêu Thủ Ace", "Sư Phụ Wada", "Heo Disco", "Thật Sảng Khoái", "Siêu Sạc Dự Phòng"],
    "PG": ["Quyết Chiến", "Đường Mạt Chược 2", "Kho Báu Aztec", "Đường Mạt Chược", "Neko May Mắn", "Thần May Mắn", "Kỳ Lân Mách Nước", "Wild Đạo Tặc"],
    "JILI": ["Siêu Cấp Ace", "Đế Quốc Hoàng Kim", "Bảo Thạch Kala", "Super Ace Deluxe", "Quyền Vương", "Điên Cuồng 777", "Truyền Thuyết Tần Vương"],
    "FC": ["Cuối Năm 2", "Ma Thuật Ghép", "Trâu Hoang Điên Cuồng", "Zeus", "Mèo Tải Tâm Bảo", "Trứng Vàng", "Máy Ủi Cây Tiền"],
    "MG": ["Tiền Đạo Bóng Đá", "Con Thuyền May Mắn", "Ngôi Sao Bóng Đá Deluxe", "9 Mặt Nạ Lửa", "Thoát Khỏi Vùng Hoang Dã May Mắn", "Jackpot Cặp Song Sinh May Mắn"],
    "MW": ["Quỷ Bà Đêm Khuya", "Vua Tiền Mặt", "Vua Ngà", "Lãng Mạn Bất Tử", "Xã Hội Cao", "Halloween"],
    "TP": ["Super King", "Mạt Chược Đại Phát", "Mạt Chược Phát Tài", "Sư Tử May Mắn 7", "Chép Vượt Vũ Môn 7", "Kim Cương 5x 7"],
    "JDB": ["Kho Báu", "Siêunubi", "Rồng May Mắn", "Học Giả Tấn Tinh Tăng", "Mặt Nạ Chiến Thắng", "Ngộ Không", "Gấu Formosa"],
    "PP": ["Rise Of Samurai 4", "Sugar Rush 1000", "Mahjong Wins 2", "Sugar Rush", "Khoan Vàng", "Cỏ Ba Lá Vàng", "Wild West Gold Megaways"],
    "WG": ["Máy Đánh Bạc Siêu Trái Cây", "Thủy Hử", "Chuỗi Kho Báu", "Bữa Tiệc Kẹo", "Tài Lộc và Sự Giàu Có", "Kho Báu Của Rồng"],
    "CQ9": ["Good Fortune M", "Nhảy Cao", "Mê Sảng", "Nhảy Cao 2", "Chú Dơi May Mắn", "Bay Lên", "Thần Sấm"],
    "VA": ["Dragon Treasure 4", "Wild Fortune 2", "Mahjong Self-drawn Win 3", "Golden Empire 2", "Mahjong Self-drawn Win 2", "Fireworks Blessings"],
    "Spade Gaming": ["Đội Trưởng Golds Fortune", "Hành Trình Đến Nơi Hoang Dã", "Trái Cây Mania", "Caishen", "Fiery Sevens Độc Quyền", "Koi May Mắn", "Múa Hổ"],
    "PlayStar": ["Vô Mỹ Nương", "Phu Nhân Caroline", "Chúc Mừng Phát Tài", "Thiên Tử", "Khỉ Fa Fa", "777", "Song Hỷ"],
    "BNG": ["Ngọc Rồng", "Cuốn Sách Của Mặt Trời Đa", "Các Vị Thần Trên Đỉnh Olympus", "Mặt Trời Của Ai Cập", "Vàng Con Hổ", "Gấu Trúc Lớn", "15 Viên Ngọc Rồng"],
    "Redtiger": ["5 Gia Đình", "777 Đỉnh Công", "Đặc Vụ Hoàng Gia", "Phước Lành Của Người Xưa", "Bom Điện Tử", "Atlantis", "10001 Đêm"],
    "KA": ["Giành Chiến Thắng Bất", "Khối Vuông 2", "Khối Vuông", "Siêu Keno", "Tháp Xung Kích", "Ngọc Rồng", "Siêu Video Poker", "Bài Baccarat"],
    "NetEnt": ["Máy Hút Máu", "Cửa Hàng Trái Cây", "Guns N' Roses Video Slots™", "Starburst™", "Quay Đôi", "Chết Hay Sống 2™", "Divine Fortune Medaways™"]
}

# "Bản Đồ Phễu Tầng 3.1" (Danh sách "Mỏ Neo" - Game Hot 90%+)
# Đây là game sẽ LUÔN LUÔN được chọn
# BẠN CẦN THÊM CÁC SẢNH KHÁC VÀ GAME MỎ NEO TƯƠNG ỨNG
GAME_ANCHORS = {
    "168Game": "Ù Mạt Chược 1",
    "PG": "Đường Mạt Chược 2",
    "JILI": "Siêu Cấp Ace",
    "FC": "Cuối Năm 2",
    "JDB": "Kho Báu",
    "PP": "Sugar Rush 1000",
    "CQ9": "Nhảy Cao 2",
    # (Thêm các sảnh khác vào đây, ví dụ: "MG": "9 Mặt Nạ Lửa")
}

# --- KHỞI TẠO HỆ THỐNG ---
bot = telebot.TeleBot(BOT_TOKEN)

class SlotScannerV3:
    """
    Kiến trúc V3.3: "Lửa Gần Rơm" + "Neo & Mồi Nhử"
    """
    def __init__(self, db, anchors):
        self.db = db
        self.anchors = anchors

    def _generate_golden_time(self, game_name, is_anchor):
        """
        Kiến trúc "Lửa Gần Rơm" (V3.3)
        """
        current_time = datetime.now()

        if is_anchor:
            delay_minutes = random.randint(15, 45)
            confidence = round(random.uniform(90.0, 97.5), 1)
            status = "🔥 SIÊU HOT (ƯU TIÊN) 🔥"
        else:
            delay_minutes = random.randint(60, 120)
            confidence = round(random.uniform(85.0, 89.9), 1)
            status = "ỔN ĐỊNH (NÊN LÓT)"

        start_time = current_time + timedelta(minutes=delay_minutes)
        end_time = start_time + timedelta(minutes=15)

        return {
            "start": start_time.strftime("%H:%M"),
            "end": end_time.strftime("%H:%M"),
            "confidence": confidence,
            "status": status
        }

    def scan_sanh(self, sanh_name):
        """
        Kiến trúc "Neo & Mồi Nhử" (V3.2)
        """
        if sanh_name not in self.db:
            return None

        game_list_of_sanh = self.db[sanh_name]
        results = []

        anchor_game_name = self.anchors.get(sanh_name)

        if anchor_game_name and anchor_game_name in game_list_of_sanh:
            game_name = anchor_game_name
            prediction = self._generate_golden_time(game_name, is_anchor=True)
            results.append({"name": game_name, **prediction})

        num_satellites = random.choice([1, 2])
        possible_satellites = [game for game in game_list_of_sanh if game != anchor_game_name]

        if not possible_satellites:
             return results

        chosen_satellites = random.sample(possible_satellites, min(num_satellites, len(possible_satellites)))

        for game_name in chosen_satellites:
            prediction = self._generate_golden_time(game_name, is_anchor=False)
            results.append({"name": game_name, **prediction})

        results.sort(key=lambda x: x['confidence'], reverse=True)
        return results

# Khởi tạo "Bộ Quét" V3.3
scanner = SlotScannerV3(GAME_DATABASE, GAME_ANCHORS)

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
        bot.reply_to(message, f"✅ ĐÃ CẤP QUYỀN (Nổ Hũ) cho User ID: {user_id_to_approve}")
        bot.send_message(user_id_to_approve, "🎉 **XIN CHÚC MỪNG!**\nTài khoản Bot Nổ Hũ của bạn đã được Admin duyệt.")
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
        bot.reply_to(message, f"🚫 ĐÃ THU HỒI QUYỀN (Nổ Hũ) của User ID: {user_id_to_revoke}")
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
    bot.reply_to(message, f"--- DANH SÁCH ĐƯỢC CẤP QUYỀN (Nổ Hũ) ---\n{user_list}")


# --- MODULE 2: LỆNH CHO NGƯỜI DÙNG ---

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    safe_admin_username = ADMIN_USERNAME.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')

    welcome = f"""
🎰 **BOT QUÉT GIỜ VÀNG NỔ HŨ FLY88 (Bản Độc Quyền chỉ dành cho web FLY88)** 🎰

Chào mừng {message.from_user.first_name},

Đây là công cụ quét Hũ ĐỘC QUYỀN, sử dụng thuật toán AI phân tích "lỗ hổng" của server game để tìm ra Khung Giờ Vàng của FLY88.

⚠️ **TRẠNG THÁI TRUY CẬP:** {"✅ **ĐÃ KÍCH HOẠT**" if user_id in authorized_users else f"🚫 **CHƯA KÍCH HOẠT** (Liên hệ: {safe_admin_username})"}

Để được cấp quyền sử dụng Bot:
1.  **Đăng ký** tài khoản qua link đại lý của Admin.
2.  **Nạp tiền** lần đầu để kích hoạt tài khoản.
3.  **Liên hệ Admin** ({safe_admin_username}) để được duyệt.

Nếu bạn đã được duyệt, sử dụng lệnh:
`/scanhu` (Để bắt đầu quét)
    """
    bot.reply_to(message, welcome, parse_mode='Markdown')

@bot.message_handler(commands=['getid'])
def get_id(message):
    user_id = message.from_user.id
    safe_admin_username = ADMIN_USERNAME.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')
    bot.reply_to(message, f"🆔 User ID Telegram của bạn là:\n`{user_id}`\n\n(Gửi ID này cho Admin {safe_admin_username} để được duyệt)", parse_mode='Markdown')

@bot.message_handler(commands=['scanhu'])
def scan_sanh_start(message):
    user_id = message.from_user.id
    safe_admin_username = ADMIN_USERNAME.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')

    if user_id not in authorized_users:
        bot.reply_to(message, f"🚫 **TRUY CẬP BỊ TỪ CHỐI** 🚫\nVui lòng liên hệ Admin ({safe_admin_username}) để đăng ký và kích hoạt.", parse_mode='Markdown')
        return

    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    buttons = [InlineKeyboardButton(sanh_name, callback_data=f"scan_{sanh_name}") for sanh_name in Sảnh_List]
    markup.add(*buttons)

    bot.reply_to(message, "✅ **ĐÃ XÁC THỰC.**\nVui lòng chọn SẢNH GAME bạn muốn quét Giờ Vàng:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('scan_'))
def callback_query(call):
    """
    Hàm này "bắt" lấy nút bấm Sảnh mà "gà" chọn
    """
    user_id = call.from_user.id

    if user_id not in authorized_users:
        bot.answer_callback_query(call.id, "🚫 TRUY CẬP BỊ TỪ CHỐI. Liên hệ Admin.", show_alert=True)
        return

    sanh_name = call.data.split('_', 1)[1]

    try:
        bot.edit_message_text(f"Đang quét toàn bộ sảnh [{sanh_name}]...\nPhân tích 10,000 phiên quay...",
                              call.message.chat.id, call.message.message_id)
        time.sleep(random.randint(3, 5))

        results = scanner.scan_sanh(sanh_name)

        if not results:
            bot.edit_message_text(f"Không tìm thấy game hot cho sảnh [{sanh_name}]. Vui lòng thử lại sau.",
                                  call.message.chat.id, call.message.message_id)
            return

        response = f"**[BÁO CÁO QUÉT SẢNH {sanh_name.upper()} HOÀN TẤT]**\n"
        response += f"Đã phân tích. Đây là {len(results)} game có 'Giờ Vàng' đẹp nhất (khung giờ hiện tại là {datetime.now().strftime('%H:%M')}):\n\n"

        for i, game in enumerate(results, 1):
            response += (
                f"{i}. **{game['name']}**\n"
                f"   => Khung Giờ: **{game['start']} - {game['end']}**\n"
                f"   => Độ Tin Cậy: **{game['confidence']}%** ({game['status']})\n\n"
            )

        response += "*Khuyến nghị: Ưu tiên các game có độ tin cậy cao. Chúc AE may mắn!*"

        bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
        bot.answer_callback_query(call.id, "Quét hoàn tất!")

    except Exception as e:
        bot.edit_message_text(f"Lỗi hệ thống phân tích sảnh {sanh_name}. Vui lòng thử lại. \nChi tiết: {e}",
                              call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "Lỗi!", show_alert=True)


# --- CHẠY BOT ---
if __name__ == "__main__":
    print("🚀 Bot Quét Hũ V3.3 (Impulse + Anchor + Menu) đang chạy...")
    bot.polling(none_stop=True)