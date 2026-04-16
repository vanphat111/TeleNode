import telebot
from telebot import types
import platform

def start_tele_bot(token, admin_id, sys_core):
    bot = telebot.TeleBot(token)
    waiting_sudo = {} 

    def check_auth(message):
        if str(message.from_user.id) != str(admin_id):
            bot.reply_to(message, "❌ Mày không phải chủ tao, đừng có nghịch!")
            return False
        return True

    @bot.message_handler(commands=['start', 'menu'])
    def send_welcome(message):
        if not check_auth(message): return
        
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add('📊 Trạng thái', '🔌 Nguồn')
        
        welcome_msg = (
            f"🚀 **UniControl Agent Online**\n"
            f"OS: `{platform.system()}` | Host: `{platform.node()}`\n\n"
            "Dùng menu bên dưới hoặc gõ lệnh trực tiếp:\n"
            "👉 `/shell <lệnh>` để chạy terminal\n"
            "👉 `/pass <mật_khẩu>` khi lệnh yêu cầu sudo"
        )
        bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=markup)

    @bot.message_handler(func=lambda m: m.text == '📊 Trạng thái' or m.text == '/status')
    def status_handler(message):
        if not check_auth(message): return
        
        info = sys_core.get_basic_info()
        msg = (
            f"📊 **THÔNG SỐ HỆ THỐNG**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"CPU: `{info['cpu']}`\n"
            f"RAM: `{info['ram']}`\n"
            f"Disk: `{info['disk']}`\n"
            f"Boot: `{info['boot']}`"
        )
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

    @bot.message_handler(commands=['shell'])
    def shell_command(message):
        if not check_auth(message): return
        
        command = message.text.replace("/shell ", "").strip()
        if not command:
            bot.reply_to(message, "Gõ lệnh sau /shell. VD: `/shell ip a`")
            return

        if "sudo" in command:
            waiting_sudo[message.chat.id] = command
            bot.reply_to(message, "🔑 Lệnh này cần quyền **sudo**.\nHãy gõ: `/pass <mật_khẩu>` để thực thi.", parse_mode="Markdown")
        else:
            result = sys_core.execute_shell(command)
            if len(result) > 4000: result = result[:4000] + "\n..."
            bot.send_message(message.chat.id, f"💻 **Kết quả:**\n```\n{result}\n```", parse_mode="Markdown")

    @bot.message_handler(commands=['pass'])
    def pass_handler(message):
        if not check_auth(message): return
        
        password = message.text.replace("/pass ", "").strip()
        chat_id = message.chat.id

        if chat_id in waiting_sudo:
            cmd = waiting_sudo[chat_id]
            bot.send_message(chat_id, f"⏳ Đang thực thi sudo: `{cmd}`...")
            
            res = sys_core.execute_interactive_shell(cmd, password)
            
            bot.send_message(chat_id, f"💻 **Kết quả:**\n")

    @bot.message_handler(func=lambda m: m.text == '🔌 Nguồn')
    def power_menu(message):
        if not check_auth(message): return
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 Reboot", callback_data="p_reboot"),
                   types.InlineKeyboardButton("🛑 Shutdown", callback_data="p_shutdown"))
        bot.send_message(message.chat.id, "⚠️ Xác nhận tác động nguồn?", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("p_"))
    def power_callback(call):
        action = call.data.split("_")[1]
        cmd = sys_core.power_control(action)
        waiting_sudo[call.message.chat.id] = cmd
        bot.edit_message_text(f"🔑 Cần pass để {action.upper()}. Gõ `/pass <mật_khẩu>`", 
                              call.message.chat.id, call.message.message_id)

    bot.infinity_polling()