from telegram import ParseMode, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from telegram.error import BadRequest, Unauthorized
import time
import datetime
import pytz
from config import ADMIN_ID, WELCOME_MESSAGE, COMMANDS, GLASS_DESIGN, MESSAGE_TEMPLATES
from admin_panel import AdminPanel, MAIN_MENU, GROUP_SETTINGS, STATS, CUSTOM_COMMANDS, SET_RULES, ADMIN_MANAGEMENT
from currency_api import CurrencyAPI
from account_age import creation_date
import html
class BotHandlers:
    def __init__(self, db, filters):
        self.db = db
        self.filters = filters
        self.admin_panel = AdminPanel(db)
        self.currency_api = CurrencyAPI()
        self.cursor = db.conn.cursor() 
    def register_handlers(self, dispatcher):
        """Register all handlers with the dispatcher"""
        dispatcher.add_handler(CommandHandler("start", self.start_command))
        dispatcher.add_handler(CommandHandler("help", self.help_command))
        dispatcher.add_handler(CommandHandler("rules", self.rules_command))
        dispatcher.add_handler(CommandHandler("ban", self.ban_command))
        dispatcher.add_handler(CommandHandler("unban", self.unban_command))
        dispatcher.add_handler(CommandHandler("mute", self.mute_command))
        dispatcher.add_handler(CommandHandler("unmute", self.unmute_command))
        dispatcher.add_handler(CommandHandler("warn", self.warn_command))
        dispatcher.add_handler(CommandHandler("unwarn", self.unwarn_command))
        dispatcher.add_handler(CommandHandler("lock", self.lock_command))
        dispatcher.add_handler(CommandHandler("unlock", self.unlock_command))
        dispatcher.add_handler(CommandHandler("time", self.time_command))
        dispatcher.add_handler(CommandHandler("pin", self.pin_message))
        dispatcher.add_handler(CommandHandler("unpin", self.unpin_message))
        dispatcher.add_handler(CommandHandler("delete", self.delete_messages))
        dispatcher.add_handler(CommandHandler("voicechat", self.create_voice_call))
        dispatcher.add_handler(CommandHandler("endvoice", self.end_voice_call))
        dispatcher.add_handler(CommandHandler("user", self.user_info_command))
        dispatcher.add_handler(CommandHandler("info", self.user_info_command))
        dispatcher.add_handler(CommandHandler("userinfo", self.user_info_command))
        dispatcher.add_handler(CommandHandler("promote", self.promote_command))
        dispatcher.add_handler(CommandHandler("demote", self.demote_command))
        dispatcher.add_handler(CommandHandler("admins", self.list_admins_command))
        dispatcher.add_handler(CommandHandler("currency", self.currency_command))
        dispatcher.add_handler(CommandHandler("arz", self.currency_command))
        dispatcher.add_handler(CommandHandler("crypto", self.crypto_command))
        dispatcher.add_handler(CommandHandler("gold", self.gold_command))
        dispatcher.add_handler(CommandHandler("top", self.top_command))
        dispatcher.add_handler(CallbackQueryHandler(self.bot_rules_button, pattern="^bot_rules$"))
        dispatcher.add_handler(CallbackQueryHandler(self.show_rules_button, pattern="^show_rules$"))
        dispatcher.add_handler(CallbackQueryHandler(self.help_button, pattern="^help$"))
        dispatcher.add_handler(CallbackQueryHandler(self.back_to_start_button, pattern="^back_to_start$"))
        dispatcher.add_handler(CallbackQueryHandler(self.top_button_handler, pattern="^top_"))
        admin_handler = ConversationHandler(
            entry_points=[
                CommandHandler("admin", self.admin_panel.handle_admin_command),
                CallbackQueryHandler(self.admin_panel.handle_admin_command, pattern="^admin_panel$"),
                MessageHandler(Filters.regex(r'^(ادمین|پنل|مدیریت)'), self.persian_admin_command)
            ],
            states={
                MAIN_MENU: [
                    CallbackQueryHandler(self.admin_panel.handle_callback)
                ],
                GROUP_SETTINGS: [
                    CallbackQueryHandler(self.admin_panel.handle_callback)
                ],
                STATS: [
                    CallbackQueryHandler(self.admin_panel.handle_callback)
                ],
                CUSTOM_COMMANDS: [
                    CallbackQueryHandler(self.admin_panel.handle_callback)
                ],
                SET_RULES: [
                    MessageHandler(Filters.text & ~Filters.command, self.admin_panel.set_rules),
                    CommandHandler("cancel", self.admin_panel.cancel)
                ],
                ADMIN_MANAGEMENT: [
                    CallbackQueryHandler(self.admin_panel.handle_callback)
                ]
            },
            fallbacks=[CommandHandler("cancel", self.admin_panel.cancel)],
            allow_reentry=True
        )
        dispatcher.add_handler(admin_handler)
        dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, self.welcome_new_member))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(سکوت|بی صدا|بیصدا)'), self.persian_mute_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(رفع سکوت|لغو سکوت)'), self.persian_unmute_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(اخراج|بن|حذف)'), self.persian_ban_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(رفع اخراج|آنبن)'), self.persian_unban_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(اخطار|هشدار|وارن)'), self.persian_warn_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(رفع اخطار|آنوارن)'), self.persian_unwarn_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(قوانین|قانون)'), self.rules_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(راهنما|کمک|هلپ)'), self.help_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(قفل|قفل گروه)'), self.persian_lock_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(باز کردن|آنلاک)'), self.persian_unlock_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(زمان|ساعت|تاریخ)'), self.time_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(کاربر|اطلاعات|پروفایل|مشخصات)'), self.persian_user_info_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(پین|سنجاق)'), self.persian_pin_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(آنپین|حذف پین|برداشتن پین)'), self.persian_unpin_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(حذف پیام|پاک کردن)'), self.persian_delete_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(ویس|ویس چت|ویس کال)'), self.persian_voice_call_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(برترین|فعال ترین|کاربران برتر|تاپ)'), self.top_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(ارتقا|ادمین کردن|ارتقاء)'), self.persian_promote_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(تنزل|حذف ادمین|عزل)'), self.persian_demote_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(لیست ادمین|ادمین ها|مدیران)'), self.list_admins_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(ارز|قیمت ارز|نرخ ارز)'), self.currency_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(کریپتو|ارز دیجیتال|رمزارز)'), self.crypto_command))
        dispatcher.add_handler(MessageHandler(Filters.regex(r'^(طلا|قیمت طلا|سکه|قیمت سکه)'), self.gold_command))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))
        dispatcher.add_handler(MessageHandler(Filters.forwarded, self.handle_message))
        dispatcher.add_handler(MessageHandler(Filters.command, self.handle_custom_command))
    def start_command(self, update, context):
        """Handle the /start command"""
        user = update.effective_user
        chat_type = update.effective_chat.type
        is_admin = False
        if chat_type in ["group", "supergroup"]:
            try:
                chat_member = context.bot.get_chat_member(update.effective_chat.id, user.id)
                is_admin = chat_member.status in ["creator", "administrator"]
            except:
                pass
        self.db.add_user(
            user.id,
            user.username,
            user.first_name,
            user.last_name,
            1 if user.id == ADMIN_ID or is_admin else 0
        )
        persian_date, persian_time = self.get_iran_datetime()
        if chat_type == "private":
            keyboard = [
                [
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['add'] + " افزودن به گروه"), 
                        url=f"https://t.me/{context.bot.username}?startgroup=start"
                    )
                ],
                [
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['info'].replace('[TEXT]', GLASS_DESIGN['rules'] + " قوانین ربات"), 
                        callback_data="bot_rules"
                    ),
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['success'].replace('[TEXT]', GLASS_DESIGN['settings'] + " راهنما"), 
                        callback_data="help"
                    )
                ]
            ]
            if user.id == ADMIN_ID:
                keyboard.append([
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['danger'].replace('[TEXT]', GLASS_DESIGN['admin'] + " پنل مدیریت کل"), 
                        callback_data="admin_panel"
                    )
                ])
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["sparkle"]} *خوش آمدید {user.first_name}* {GLASS_DESIGN["welcome"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["fire"]} *ربات مدیریت گروه با طراحی شیشه‌ای*
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} ضد لینک و ضد فوروارد پیشرفته
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} ضد فحش هوشمند فارسی
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} قفل مدت‌دار گروه و مدیریت کامل
{GLASS_DESIGN["side"]} {GLASS_DESIGN["calendar"]} *تاریخ:* {persian_date} | {GLASS_DESIGN["clock"]} *ساعت:* {persian_time}
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            group_id = update.effective_chat.id
            group_title = update.effective_chat.title
            self.db.add_group(group_id, group_title)
            self.update_group_admins(context, group_id)
            keyboard = []
            if is_admin or user.id == ADMIN_ID:
                keyboard.append([
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['admin'] + " پنل مدیریت"), 
                        callback_data="admin_panel"
                    ),
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['info'].replace('[TEXT]', GLASS_DESIGN['rules'] + " قوانین گروه"), 
                        callback_data="show_rules"
                    )
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['info'].replace('[TEXT]', GLASS_DESIGN['rules'] + " قوانین گروه"), 
                        callback_data="show_rules"
                    ),
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['success'].replace('[TEXT]', GLASS_DESIGN['settings'] + " راهنما"), 
                        callback_data="help"
                    )
                ])
            if keyboard:
                reply_markup = InlineKeyboardMarkup(keyboard)
            else:
                reply_markup = None
            update.message.reply_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["sparkle"]} *ربات مدیریت گروه فعال شد* {GLASS_DESIGN["sparkle"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["group"]} *گروه:* {group_title}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["user"]} *کاربر:* {user.first_name}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} برای دیدن دستورات، /help را بفرستید
{GLASS_DESIGN["side"]} {GLASS_DESIGN["calendar"]} *تاریخ:* {persian_date} | {GLASS_DESIGN["clock"]} *ساعت:* {persian_time}
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    def update_group_admins(self, context, chat_id):
        """Update the database with all group admins"""
        try:
            admins = context.bot.get_chat_administrators(chat_id)
            for admin in admins:
                user = admin.user
                self.db.add_user(
                    user.id,
                    user.username,
                    user.first_name,
                    user.last_name,
                    1
                )
        except Exception as e:
            print(f"Error updating group admins: {str(e)}")
    def help_command(self, update, context):
        """Handle the /help command"""
        user_id = update.effective_user.id
        is_admin = self.admin_panel.is_admin(user_id)
        help_text = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["sparkle"]} *راهنمای دستورات ربات* {GLASS_DESIGN["sparkle"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} *دستورات عمومی:*
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /start - شروع کار با ربات
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /help یا "راهنما" - نمایش این راهنما
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /rules یا "قوانین" - نمایش قوانین گروه
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /time یا "زمان" - نمایش ساعت و تاریخ ایران
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /top یا "برترین" - نمایش کاربران فعال گروه
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /info یا "اطلاعات" - نمایش اطلاعات کاربر
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} *دستورات اطلاعات مالی:*
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /currency یا "ارز" - نمایش قیمت ارزها
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /crypto یا "رمزارز" - نمایش قیمت ارزهای دیجیتال
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /gold یا "طلا" - نمایش قیمت طلا و سکه"""
        if is_admin:
            help_text += f"""
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} *دستورات مدیریتی:*
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /admin یا "ادمین" - دسترسی به پنل ادمین
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /ban یا "اخراج" - حذف کاربر از گروه
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /mute یا "سکوت" - بی‌صدا کردن کاربر
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /warn یا "اخطار" - اخطار به کاربر
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /lock یا "قفل" - قفل کردن گروه
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /pin یا "پین" - پین کردن پیام
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /voicechat یا "ویس چت" - ایجاد ویس چت"""
            if user_id == ADMIN_ID:
                help_text += f"""
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} *دستورات مدیریت ادمین‌ها:*
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /promote یا "ارتقا" - ارتقا کاربر به ادمین
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /demote یا "تنزل" - عزل کاربر از ادمینی
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /admins یا "لیست ادمین" - نمایش لیست ادمین‌ها"""
        help_text += f"""
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} *نکته:* می‌توانید دستورات را به فارسی هم استفاده کنید
{GLASS_DESIGN["footer"]}"""
        keyboard = []
        if is_admin:
            keyboard.append([
                InlineKeyboardButton(
                    GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['admin'] + " پنل مدیریت"), 
                    callback_data="admin_panel"
                )
            ])
        if keyboard:
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            reply_markup = None
        update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    def rules_command(self, update, context):
        """Handle the /rules command"""
        chat_id = update.effective_chat.id
        settings = self.db.get_group_settings(chat_id)
        if settings and settings["rules"]:
            rules_text = settings["rules"]
        else:
            rules_text = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["warning"]} *قوانین گروه هنوز تنظیم نشده است*
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} از ادمین گروه بخواهید قوانین را تنظیم کند
{GLASS_DESIGN["footer"]}"""
        user_id = update.effective_user.id
        is_admin = self.admin_panel.is_admin(user_id)
        keyboard = []
        if is_admin:
            keyboard.append([
                InlineKeyboardButton(
                    GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['settings'] + " تنظیم قوانین"), 
                    callback_data="admin_panel_rules"
                )
            ])
        if keyboard:
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            reply_markup = None
        update.message.reply_text(
            rules_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    def welcome_new_member(self, update, context):
        """Welcome new members to the group"""
        chat = update.effective_chat
        new_members = update.message.new_chat_members
        settings = self.db.get_group_settings(chat.id)
        if not settings or not settings["welcome_enabled"]:
            return
        persian_date, persian_time = self.get_iran_datetime()
        for new_member in new_members:
            if new_member.id == context.bot.id:
                continue
            self.db.add_user(
                new_member.id,
                new_member.username,
                new_member.first_name,
                new_member.last_name
            )
            self.db.add_group_member(chat.id, new_member.id)
            self.db.update_stats(chat.id, "new_members")
            is_tabchi = self.db.is_tabchi(
                new_member.id, 
                new_member.username, 
                new_member.first_name
            )
            if is_tabchi and settings["antitabchi_enabled"]:
                try:
                    context.bot.ban_chat_member(chat.id, new_member.id)
                    self.db.ban_user(chat.id, new_member.id)
                    self.db.update_stats(chat.id, "tabchi_blocked")
                    update.message.reply_text(
                        f"{GLASS_DESIGN['ban']} کاربر به دلیل تشخیص ربات تبچی از گروه اخراج شد."
                    )
                    return
                except Exception as e:
                    print(f"Error banning tabchi: {str(e)}")
            member_name = new_member.first_name
            if new_member.last_name:
                member_name += f" {new_member.last_name}"
            welcome_message = WELCOME_MESSAGE.format(
                name=member_name,
                group_name=chat.title,
                date=persian_date,
                time=persian_time
            )
            keyboard = [
                [
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['info'].replace('[TEXT]', GLASS_DESIGN['rules'] + " قوانین گروه"), 
                        callback_data="show_rules"
                    ),
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['success'].replace('[TEXT]', GLASS_DESIGN['settings'] + " راهنما"), 
                        callback_data="help"
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(
                chat_id=chat.id,
                text=welcome_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    def handle_message(self, update, context):
        """Handle regular messages"""
        if not update.effective_message:
            return
        message = update.effective_message
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        self.db.update_stats(chat_id, "messages_count")
        self.db.update_user_activity(chat_id, user_id)
        try:
            import datetime
            today = datetime.date.today().isoformat()
            if 'last_message_scan' not in context.bot_data:
                context.bot_data['last_message_scan'] = {}
            if chat_id not in context.bot_data['last_message_scan'] or context.bot_data['last_message_scan'][chat_id] != today:
                context.bot_data['last_message_scan'][chat_id] = today
                try:
                    persian_date, persian_time = self.get_iran_datetime()
                    print(f"[{persian_date} {persian_time}] Scanning previous messages for chat {chat_id}...")
                    import threading
                    def scan_previous_messages():
                        try:
                            offset = 0
                            limit = 100
                            total_scanned = 0
                            max_messages = 1000
                            try:
                                print(f"Scanning previous messages for chat {chat_id}...")
                                print(f"Finished scanning {total_scanned} previous messages for chat {chat_id}")
                            except Exception as e:
                                print(f"Error scanning messages: {str(e)}")
                        except Exception as e:
                            print(f"Error in scan_previous_messages: {str(e)}")
                    scan_thread = threading.Thread(target=scan_previous_messages)
                    scan_thread.daemon = True
                    scan_thread.start()
                except Exception as e:
                    print(f"Error setting up message scanning: {str(e)}")
        except Exception as e:
            print(f"Error in message history scanning setup: {str(e)}")
        if self.filters.should_delete_message(message, chat_id):
            reason = self.filters.get_violation_reason(message, chat_id)
            try:
                message.delete()
                persian_date, persian_time = self.get_iran_datetime()
                content_type = "نامشخص"
                if message.photo:
                    content_type = "تصویر"
                elif message.video:
                    content_type = "ویدیو"
                elif message.animation:
                    content_type = "گیف"
                elif message.document:
                    content_type = "فایل"
                elif message.sticker:
                    content_type = "استیکر"
                settings = self.db.get_group_settings(chat_id)
                if settings and settings.get("antiporn_enabled", False) and "پورن" in reason:
                    nsfw_message = MESSAGE_TEMPLATES["nsfw_detected"].format(
                        user=f"[{update.effective_user.first_name}](tg://user?id={user_id})",
                        content_type=content_type,
                        date=persian_date,
                        time=persian_time
                    )
                    context.bot.send_message(
                        chat_id,
                        nsfw_message,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    self.db.update_stats(chat_id, "porn_blocked")
                    if settings["strict_mode"]:
                        warnings = self.db.warn_user(chat_id, user_id)
                        self.db.update_stats(chat_id, "warnings_issued")
                        context.bot.send_message(
                            chat_id,
                            f"⚠️ [{update.effective_user.first_name}](tg://user?id={user_id}), "
                            f"به دلیل ارسال محتوای نامناسب اخطار دریافت کردید.\n\n"
                            f"تعداد اخطارها: {warnings}/3",
                            parse_mode=ParseMode.MARKDOWN
                        )
                        if warnings >= 3:
                            try:
                                until_date = int(time.time()) + 24 * 60 * 60
                                context.bot.restrict_chat_member(
                                    chat_id,
                                    user_id,
                                    ChatPermissions(
                                        can_send_messages=False,
                                        can_send_media_messages=False,
                                        can_send_other_messages=False,
                                        can_add_web_page_previews=False
                                    ),
                                    until_date=until_date
                                )
                                context.bot.send_message(
                                    chat_id,
                                    f"🔇 [{update.effective_user.first_name}](tg://user?id={user_id}) "
                                    f"به دلیل دریافت 3 اخطار، به مدت 24 ساعت بی‌صدا شد.",
                                    parse_mode=ParseMode.MARKDOWN
                                )
                                while self.db.unwarn_user(chat_id, user_id) > 0:
                                    pass
                            except (BadRequest, Unauthorized) as e:
                                context.bot.send_message(
                                    chat_id,
                                    f"❌ خطا در بی‌صدا کردن کاربر: {str(e)}"
                                )
                else:
                    if settings and settings["strict_mode"]:
                        warnings = self.db.warn_user(chat_id, user_id)
                        self.db.update_stats(chat_id, "warnings_issued")
                        persian_date, persian_time = self.get_iran_datetime()
                        if "اسپم" in reason or "پیام‌های مکرر" in reason or "spam" in reason.lower():
                            warning_message = MESSAGE_TEMPLATES["spam_warning"].format(
                                user=f"[{update.effective_user.first_name}](tg://user?id={user_id})",
                                warn_count=warnings,
                                date=persian_date,
                                time=persian_time
                            )
                            context.bot.send_message(
                                chat_id,
                                warning_message,
                                parse_mode=ParseMode.MARKDOWN
                            )
                        else:
                            context.bot.send_message(
                                chat_id,
                                f"⚠️ [{update.effective_user.first_name}](tg://user?id={user_id}), "
                                f"{reason}\n\n"
                                f"تعداد اخطارها: {warnings}/3",
                                parse_mode=ParseMode.MARKDOWN
                            )
                        if warnings >= 3:
                            try:
                                until_date = int(time.time()) + 24 * 60 * 60
                                context.bot.restrict_chat_member(
                                    chat_id,
                                    user_id,
                                    ChatPermissions(
                                        can_send_messages=False,
                                        can_send_media_messages=False,
                                        can_send_other_messages=False,
                                        can_add_web_page_previews=False
                                    ),
                                    until_date=until_date
                                )
                                context.bot.send_message(
                                    chat_id,
                                    f"🔇 [{update.effective_user.first_name}](tg://user?id={user_id}) "
                                    f"به دلیل دریافت 3 اخطار، به مدت 24 ساعت بی‌صدا شد.",
                                    parse_mode=ParseMode.MARKDOWN
                                )
                                while self.db.unwarn_user(chat_id, user_id) > 0:
                                    pass
                            except (BadRequest, Unauthorized) as e:
                                context.bot.send_message(
                                    chat_id,
                                    f"❌ خطا در بی‌صدا کردن کاربر: {str(e)}"
                                )
            except (BadRequest, Unauthorized) as e:
                print(f"Error deleting message: {str(e)}")
    def handle_custom_command(self, update, context):
        """Handle custom commands defined by group admins"""
        if not update.effective_message:
            return
        message = update.effective_message
        chat_id = update.effective_chat.id
        command = message.text.split()[0][1:].split('@')[0]
        response = self.db.get_custom_command(chat_id, command)
        if response:
            update.message.reply_text(
                response,
                parse_mode=ParseMode.MARKDOWN
            )
    def get_target_user(self, update, context):
        """Get the target user from a command"""
        message = update.effective_message
        if message.reply_to_message:
            return message.reply_to_message.from_user
        if context.args and len(context.args) > 0:
            username = context.args[0].replace('@', '')
            try:
                chat_member = context.bot.get_chat_member(
                    update.effective_chat.id,
                    username
                )
                return chat_member.user
            except:
                try:
                    user_id = int(username)
                    chat_member = context.bot.get_chat_member(
                        update.effective_chat.id,
                        user_id
                    )
                    return chat_member.user
                except:
                    pass
        return None
    def ban_command(self, update, context):
        """Handle the /ban command"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        if not self.admin_panel.is_admin(user.id):
            update.message.reply_text(f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["error"]} *خطای دسترسی* {GLASS_DESIGN["shield"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} شما دسترسی به این دستور را ندارید.
{GLASS_DESIGN["footer"]}""", parse_mode=ParseMode.MARKDOWN)
            return
        target_user = self.get_target_user(update, context)
        if not target_user:
            update.message.reply_text(f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["error"]} *خطای دستور* {GLASS_DESIGN["info"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} لطفا کاربر مورد نظر را مشخص کنید.
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} می‌توانید روی پیام کاربر ریپلای کنید یا نام کاربری او را بنویسید.
{GLASS_DESIGN["footer"]}""", parse_mode=ParseMode.MARKDOWN)
            return
        is_admin = False
        try:
            chat_member = context.bot.get_chat_member(chat_id, target_user.id)
            is_admin = chat_member.status in ["creator", "administrator"]
        except Exception as e:
            print(f"Error checking admin status: {str(e)}")
        if is_admin:
            update.message.reply_text(f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["error"]} *عملیات ناموفق* {GLASS_DESIGN["shield"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} نمی‌توانید ادمین را اخراج کنید.
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} ادمین‌ها قابل اخراج نیستند.
{GLASS_DESIGN["footer"]}""", parse_mode=ParseMode.MARKDOWN)
            return
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "دلیل مشخص نشده"
        try:
            context.bot.kick_chat_member(chat_id, target_user.id)
            self.db.ban_user(chat_id, target_user.id)
            self.db.update_stats(chat_id, "removed_members")
            persian_date, persian_time = self.get_iran_datetime()
            ban_message = MESSAGE_TEMPLATES["ban"].format(
                user=f"[{target_user.first_name}](tg://user?id={target_user.id})",
                admin=f"[{user.first_name}](tg://user?id={user.id})",
                reason=reason,
                date=persian_date,
                time=persian_time
            )
            update.message.reply_text(
                ban_message,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            error_message = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["error"]} *خطا در اخراج کاربر* {GLASS_DESIGN["warning"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} دلیل خطا: {str(e)}
{GLASS_DESIGN["side"]} 
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bulb"]} راهکارهای ممکن:
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} اطمینان از ادمین بودن ربات
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} اطمینان از دسترسی کافی ربات
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} اطمینان از عدم ادمین بودن کاربر هدف
{GLASS_DESIGN["footer"]}"""
            update.message.reply_text(
                error_message,
                parse_mode=ParseMode.MARKDOWN
            )
    def unban_command(self, update, context):
        """Unban a user from the group"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        if not self.admin_panel.is_admin(user_id):
            update.message.reply_text("شما دسترسی به این دستور را ندارید.")
            return
        target_user = self.get_target_user(update, context)
        if not target_user:
            update.message.reply_text("لطفا کاربر مورد نظر را مشخص کنید (با ریپلای یا نام کاربری).")
            return
        try:
            context.bot.unban_chat_member(chat_id, target_user.id)
            self.db.ban_user(chat_id, target_user.id, False)
            update.message.reply_text(
                f"✅ محدودیت کاربر [{target_user.first_name}](tg://user?id={target_user.id}) برداشته شد.",
                parse_mode=ParseMode.MARKDOWN
            )
        except (BadRequest, Unauthorized) as e:
            update.message.reply_text(f"❌ خطا در رفع محدودیت کاربر: {str(e)}")
    def mute_command(self, update, context):
        """Handle the /mute command"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        if not self.admin_panel.is_admin(user.id):
            update.message.reply_text(f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["error"]} *خطای دسترسی* {GLASS_DESIGN["shield"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} شما دسترسی به این دستور را ندارید.
{GLASS_DESIGN["footer"]}""", parse_mode=ParseMode.MARKDOWN)
            return
        target_user = self.get_target_user(update, context)
        if not target_user:
            update.message.reply_text(f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["error"]} *خطای دستور* {GLASS_DESIGN["info"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} لطفا کاربر مورد نظر را مشخص کنید.
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} می‌توانید روی پیام کاربر ریپلای کنید یا نام کاربری او را بنویسید.
{GLASS_DESIGN["footer"]}""", parse_mode=ParseMode.MARKDOWN)
            return
        is_admin = False
        try:
            chat_member = context.bot.get_chat_member(chat_id, target_user.id)
            is_admin = chat_member.status in ["creator", "administrator"]
        except Exception as e:
            print(f"Error checking admin status: {str(e)}")
        if is_admin:
            update.message.reply_text(f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["error"]} *عملیات ناموفق* {GLASS_DESIGN["shield"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} نمی‌توانید ادمین را بی‌صدا کنید.
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} ادمین‌ها قابل بی‌صدا شدن نیستند.
{GLASS_DESIGN["footer"]}""", parse_mode=ParseMode.MARKDOWN)
            return
        duration = None
        if len(context.args) > 1:
            try:
                time_arg = context.args[1].lower()
                value = int(''.join(filter(str.isdigit, time_arg)))
                if 'm' in time_arg:
                    duration = value * 60
                elif 'h' in time_arg:
                    duration = value * 3600
                elif 'd' in time_arg:
                    duration = value * 86400
                else:
                    duration = int(time_arg)
            except:
                duration = None
        duration_text = "نامحدود"
        if duration:
            if duration < 60:
                duration_text = f"{duration} ثانیه"
            elif duration < 3600:
                duration_text = f"{duration // 60} دقیقه"
            elif duration < 86400:
                duration_text = f"{duration // 3600} ساعت"
            else:
                duration_text = f"{duration // 86400} روز"
        try:
            permissions = ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            )
            if duration:
                until_date = int(time.time()) + duration
                context.bot.restrict_chat_member(chat_id, target_user.id, permissions, until_date=until_date)
            else:
                context.bot.restrict_chat_member(chat_id, target_user.id, permissions)
            self.db.mute_user(chat_id, target_user.id)
            persian_date, persian_time = self.get_iran_datetime()
            mute_message = MESSAGE_TEMPLATES["mute"].format(
                user=f"[{target_user.first_name}](tg://user?id={target_user.id})",
                admin=f"[{user.first_name}](tg://user?id={user.id})",
                duration=duration_text,
                date=persian_date,
                time=persian_time
            )
            update.message.reply_text(
                mute_message,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            error_message = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["error"]} *خطا در بی‌صدا کردن کاربر* {GLASS_DESIGN["warning"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} دلیل خطا: {str(e)}
{GLASS_DESIGN["side"]} 
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bulb"]} راهکارهای ممکن:
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} اطمینان از ادمین بودن ربات
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} اطمینان از دسترسی کافی ربات
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} اطمینان از عدم ادمین بودن کاربر هدف
{GLASS_DESIGN["footer"]}"""
            update.message.reply_text(
                error_message,
                parse_mode=ParseMode.MARKDOWN
            )
    def unmute_command(self, update, context):
        """Unmute a user in the group"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        if not self.admin_panel.is_admin(user_id):
            update.message.reply_text(f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["error"]} *خطای دسترسی* {GLASS_DESIGN["shield"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} شما دسترسی به این دستور را ندارید.
{GLASS_DESIGN["footer"]}""", parse_mode=ParseMode.MARKDOWN)
            return
        target_user = self.get_target_user(update, context)
        if not target_user:
            update.message.reply_text(f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["error"]} *خطای دستور* {GLASS_DESIGN["info"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} لطفا کاربر مورد نظر را مشخص کنید.
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} می‌توانید روی پیام کاربر ریپلای کنید یا نام کاربری او را بنویسید.
{GLASS_DESIGN["footer"]}""", parse_mode=ParseMode.MARKDOWN)
            return
        try:
            context.bot.restrict_chat_member(
                chat_id,
                target_user.id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )
            self.db.mute_user(chat_id, target_user.id, False)
            persian_date, persian_time = self.get_iran_datetime()
            unmute_message = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["unmute"]} *رفع محدودیت کاربر* {GLASS_DESIGN["success"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["user"]} *کاربر:* [{target_user.first_name}](tg://user?id={target_user.id})
{GLASS_DESIGN["side"]} {GLASS_DESIGN["admin"]} *توسط:* [{update.effective_user.first_name}](tg://user?id={update.effective_user.id})
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} کاربر اکنون می‌تواند در گروه صحبت کند.
{GLASS_DESIGN["side"]} {GLASS_DESIGN["diamond_blue"]} ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ {GLASS_DESIGN["diamond_blue"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["calendar"]} *تاریخ:* {persian_date}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["clock"]} *ساعت:* {persian_time}
{GLASS_DESIGN["footer"]}"""
            update.message.reply_text(
                unmute_message,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            error_message = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["error"]} *خطا در رفع محدودیت کاربر* {GLASS_DESIGN["warning"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} دلیل خطا: {str(e)}
{GLASS_DESIGN["side"]} 
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bulb"]} راهکارهای ممکن:
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} اطمینان از ادمین بودن ربات
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} اطمینان از دسترسی کافی ربات
{GLASS_DESIGN["footer"]}"""
            update.message.reply_text(
                error_message,
                parse_mode=ParseMode.MARKDOWN
            )
    def warn_command(self, update, context):
        """Handle the /warn command"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        if not self.admin_panel.is_admin(user.id):
            update.message.reply_text(f"{GLASS_DESIGN['error']} شما دسترسی به این دستور را ندارید.")
            return
        target_user = self.get_target_user(update, context)
        if not target_user:
            update.message.reply_text(f"{GLASS_DESIGN['error']} لطفا کاربر مورد نظر را مشخص کنید.")
            return
        if self.admin_panel.is_admin(target_user.id):
            update.message.reply_text(f"{GLASS_DESIGN['error']} نمی‌توانید به ادمین اخطار دهید.")
            return
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "دلیل مشخص نشده"
        try:
            self.db.add_group_member(chat_id, target_user.id)
            warnings = self.db.warn_user(chat_id, target_user.id)
            self.db.update_stats(chat_id, "warnings_issued")
            persian_date, persian_time = self.get_iran_datetime()
            warn_message = MESSAGE_TEMPLATES["warn"].format(
                user=f"[{target_user.first_name}](tg://user?id={target_user.id})",
                warn_count=warnings,
                reason=reason,
                date=persian_date,
                time=persian_time
            )
            update.message.reply_text(
                warn_message,
                parse_mode=ParseMode.MARKDOWN
            )
            if warnings >= 3:
                try:
                    permissions = ChatPermissions(
                        can_send_messages=False,
                        can_send_media_messages=False,
                        can_send_polls=False,
                        can_send_other_messages=False,
                        can_add_web_page_previews=False,
                        can_change_info=False,
                        can_invite_users=False,
                        can_pin_messages=False
                    )
                    until_date = int(time.time()) + 86400
                    context.bot.restrict_chat_member(chat_id, target_user.id, permissions, until_date=until_date)
                    self.db.mute_user(chat_id, target_user.id)
                    self.db.unwarn_user(chat_id, target_user.id)
                    self.db.unwarn_user(chat_id, target_user.id)
                    self.db.unwarn_user(chat_id, target_user.id)
                    persian_date, persian_time = self.get_iran_datetime()
                    update.message.reply_text(
                        f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["mute"]} *کاربر به دلیل دریافت 3 اخطار بی‌صدا شد* {GLASS_DESIGN["lock"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["user"]} *کاربر:* [{target_user.first_name}](tg://user?id={target_user.id})
{GLASS_DESIGN["side"]} {GLASS_DESIGN["timer"]} *مدت زمان:* 24 ساعت
{GLASS_DESIGN["side"]} {GLASS_DESIGN["calendar"]} *تاریخ:* {persian_date}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["clock"]} *ساعت:* {persian_time}
{GLASS_DESIGN["footer"]}""",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    persian_date, persian_time = self.get_iran_datetime()
                    mute_message = MESSAGE_TEMPLATES["mute_after_warns"].format(
                        user=f"[{target_user.first_name}](tg://user?id={target_user.id})",
                        date=persian_date,
                        time=persian_time
                    )
                    context.bot.send_message(
                        chat_id,
                        mute_message,
                        parse_mode=ParseMode.MARKDOWN
                    )
                except Exception as e:
                    update.message.reply_text(f"{GLASS_DESIGN['error']} خطا در بی‌صدا کردن کاربر: {str(e)}")
        except Exception as e:
            update.message.reply_text(f"{GLASS_DESIGN['error']} خطا در اخطار دادن به کاربر: {str(e)}")
    def unwarn_command(self, update, context):
        """Remove a warning from a user"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        if not self.admin_panel.is_admin(user_id):
            update.message.reply_text("شما دسترسی به این دستور را ندارید.")
            return
        target_user = self.get_target_user(update, context)
        if not target_user:
            update.message.reply_text("لطفا کاربر مورد نظر را مشخص کنید (با ریپلای یا نام کاربری).")
            return
        warnings = self.db.unwarn_user(chat_id, target_user.id)
        update.message.reply_text(
            f"✅ یک اخطار از کاربر [{target_user.first_name}](tg://user?id={target_user.id}) حذف شد.\n"
            f"تعداد اخطارها: {warnings}/3",
            parse_mode=ParseMode.MARKDOWN
        )
    def admin_panel_button(self, update, context):
        """Handle the admin panel button callback"""
        query = update.callback_query
        query.answer("در حال باز کردن پنل مدیریت...")
        return self.admin_panel.handle_admin_command(update, context)
    def bot_rules_button(self, update, context):
        """Handle the bot_rules button callback"""
        query = update.callback_query
        query.answer()
        rules_text = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["rules"]} *قوانین استفاده از ربات* {GLASS_DESIGN["sparkle"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} ربات باید ادمین گروه با دسترسی کامل باشد
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} امکان حذف پیام و محدودکردن کاربران لازم است
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} تنظیمات ربات فقط توسط ادمین‌ها قابل تغییر است
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} از دستورات ربات سوءاستفاده نکنید
{GLASS_DESIGN["footer"]}"""
        query.edit_message_text(
            text=rules_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['back'] + " بازگشت"),
                    callback_data="back_to_start"
                )]
            ])
        )
    def show_rules_button(self, update, context):
        """Handle the show_rules button callback"""
        query = update.callback_query
        query.answer()
        chat_id = update.effective_chat.id
        settings = self.db.get_group_settings(chat_id)
        if settings and settings["rules"]:
            rules_text = settings["rules"]
        else:
            rules_text = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["warning"]} *قوانین گروه هنوز تنظیم نشده است*
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} از ادمین گروه بخواهید قوانین را تنظیم کند
{GLASS_DESIGN["footer"]}"""
        query.edit_message_text(
            text=rules_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['back'] + " بازگشت"),
                    callback_data="back_to_start"
                )]
            ])
        )
    def help_button(self, update, context):
        """Handle the help button callback"""
        query = update.callback_query
        query.answer()
        user_id = update.effective_user.id
        is_admin = self.admin_panel.is_admin(user_id)
        help_text = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["sparkle"]} *راهنمای دستورات ربات* {GLASS_DESIGN["sparkle"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} *دستورات عمومی:*
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /start - شروع کار با ربات
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /help یا "راهنما" - نمایش این راهنما
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /rules یا "قوانین" - نمایش قوانین گروه
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /time یا "زمان" - نمایش ساعت و تاریخ ایران
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /top یا "برترین" - نمایش کاربران فعال گروه
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /info یا "اطلاعات" - نمایش اطلاعات کاربر
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} *دستورات اطلاعات مالی:*
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /currency یا "ارز" - نمایش قیمت ارزها
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /crypto یا "رمزارز" - نمایش قیمت ارزهای دیجیتال
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /gold یا "طلا" - نمایش قیمت طلا و سکه"""
        if is_admin:
            help_text += f"""
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} *دستورات مدیریتی:*
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /admin یا "ادمین" - دسترسی به پنل ادمین
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /ban یا "اخراج" - حذف کاربر از گروه
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /mute یا "سکوت" - بی‌صدا کردن کاربر
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /warn یا "اخطار" - اخطار به کاربر
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /lock یا "قفل" - قفل کردن گروه
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /pin یا "پین" - پین کردن پیام
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /voicechat یا "ویس چت" - ایجاد ویس چت"""
            if user_id == ADMIN_ID:
                help_text += f"""
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} *دستورات مدیریت ادمین‌ها:*
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /promote یا "ارتقا" - ارتقا کاربر به ادمین
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /demote یا "تنزل" - عزل کاربر از ادمینی
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} /admins یا "لیست ادمین" - نمایش لیست ادمین‌ها"""
        help_text += f"""
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} *نکته:* می‌توانید دستورات را به فارسی هم استفاده کنید
{GLASS_DESIGN["footer"]}"""
        keyboard = []
        if is_admin:
            keyboard.append([
                InlineKeyboardButton(
                    GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['admin'] + " پنل مدیریت"), 
                    callback_data="admin_panel"
                )
            ])
        if keyboard:
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            reply_markup = None
        update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    def back_to_start_button(self, update, context):
        """Handle the back to start button callback"""
        query = update.callback_query
        query.answer()
        persian_date, persian_time = self.get_iran_datetime()
        user = update.effective_user
        chat_type = update.effective_chat.type
        if chat_type == "private":
            keyboard = [
                [
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['add'] + " افزودن به گروه"), 
                        url=f"https://t.me/{context.bot.username}?startgroup=start"
                    )
                ],
                [
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['info'].replace('[TEXT]', GLASS_DESIGN['rules'] + " قوانین ربات"), 
                        callback_data="bot_rules"
                    ),
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['success'].replace('[TEXT]', GLASS_DESIGN['settings'] + " راهنما"), 
                        callback_data="help"
                    )
                ]
            ]
            if user.id == ADMIN_ID:
                keyboard.append([
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['danger'].replace('[TEXT]', GLASS_DESIGN['admin'] + " پنل مدیریت کل"), 
                        callback_data="admin_panel"
                    )
                ])
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["sparkle"]} *خوش آمدید {user.first_name}* {GLASS_DESIGN["welcome"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["fire"]} *ربات مدیریت گروه با طراحی شیشه‌ای*
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} ضد لینک و ضد فوروارد پیشرفته
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} ضد فحش هوشمند فارسی
{GLASS_DESIGN["side"]} {GLASS_DESIGN["bullet_point"]} قفل مدت‌دار گروه و مدیریت کامل
{GLASS_DESIGN["side"]} {GLASS_DESIGN["calendar"]} *تاریخ:* {persian_date} | {GLASS_DESIGN["clock"]} *ساعت:* {persian_time}
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            group_id = update.effective_chat.id
            group_title = update.effective_chat.title
            is_admin = False
            try:
                chat_member = context.bot.get_chat_member(group_id, user.id)
                is_admin = chat_member.status in ["creator", "administrator"]
            except:
                pass
            keyboard = []
            if is_admin or user.id == ADMIN_ID:
                keyboard.append([
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['admin'] + " پنل مدیریت"), 
                        callback_data="admin_panel"
                    ),
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['info'].replace('[TEXT]', GLASS_DESIGN['rules'] + " قوانین گروه"), 
                        callback_data="show_rules"
                    )
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['info'].replace('[TEXT]', GLASS_DESIGN['rules'] + " قوانین گروه"), 
                        callback_data="show_rules"
                    ),
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['success'].replace('[TEXT]', GLASS_DESIGN['settings'] + " راهنما"), 
                        callback_data="help"
                    )
                ])
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["sparkle"]} *ربات مدیریت گروه فعال شد* {GLASS_DESIGN["sparkle"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["group"]} *گروه:* {group_title}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["user"]} *کاربر:* {user.first_name}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} برای دیدن دستورات، /help را بفرستید
{GLASS_DESIGN["side"]} {GLASS_DESIGN["calendar"]} *تاریخ:* {persian_date} | {GLASS_DESIGN["clock"]} *ساعت:* {persian_time}
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    def persian_mute_command(self, update, context):
        """Handle Persian mute command"""
        text = update.message.text.strip()
        parts = text.split()
        if len(parts) > 1:
            context.args = parts[1:]
        else:
            context.args = []
        return self.mute_command(update, context)
    def persian_unmute_command(self, update, context):
        """Handle Persian unmute command"""
        text = update.message.text.strip()
        parts = text.split()
        if len(parts) > 1:
            context.args = parts[1:]
        else:
            context.args = []
        return self.unmute_command(update, context)
    def persian_ban_command(self, update, context):
        """Handle Persian ban command"""
        text = update.message.text.strip()
        parts = text.split()
        if len(parts) > 1:
            context.args = parts[1:]
        else:
            context.args = []
        return self.ban_command(update, context)
    def persian_unban_command(self, update, context):
        """Handle Persian unban command"""
        text = update.message.text.strip()
        parts = text.split()
        if len(parts) > 1:
            context.args = parts[1:]
        else:
            context.args = []
        return self.unban_command(update, context)
    def persian_warn_command(self, update, context):
        """Handle Persian warn command"""
        text = update.message.text.strip()
        parts = text.split()
        if len(parts) > 1:
            context.args = parts[1:]
        else:
            context.args = []
        return self.warn_command(update, context)
    def persian_unwarn_command(self, update, context):
        """Handle Persian unwarn command"""
        text = update.message.text.strip()
        parts = text.split()
        if len(parts) > 1:
            context.args = parts[1:]
        else:
            context.args = []
        return self.unwarn_command(update, context)
    def persian_admin_command(self, update, context):
        """Handle Persian admin command"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        if chat_type not in ["group", "supergroup"]:
            update.message.reply_text(f"{GLASS_DESIGN['error']} این دستور فقط در گروه‌ها قابل استفاده است.")
            return
        try:
            chat_member = context.bot.get_chat_member(chat_id, user_id)
            is_admin = chat_member.status in ["creator", "administrator"]
        except:
            is_admin = False
        if not is_admin and user_id != ADMIN_ID:
            update.message.reply_text(f"{GLASS_DESIGN['error']} شما دسترسی به پنل ادمین را ندارید.")
            return
        is_large_public_group = False
        try:
            if chat_type == "supergroup" and not update.effective_chat.username:
                member_count = context.bot.get_chat_member_count(chat_id)
                is_large_public_group = member_count > 1000
        except Exception:
            is_large_public_group = chat_type == "supergroup"
        admin_panel_text = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["crown"]} *پنل مدیریت گروه* {GLASS_DESIGN["crown"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["sparkle"]} به پنل مدیریت گروه خوش آمدید.
{GLASS_DESIGN["side"]} {GLASS_DESIGN["arrow_right"]} لطفا یکی از گزینه‌های زیر را انتخاب کنید:
{GLASS_DESIGN["footer"]}"""
        if is_large_public_group:
            keyboard = [
                [InlineKeyboardButton(GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['settings'] + " تنظیمات گروه"), callback_data="settings")],
                [InlineKeyboardButton(GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['rules'] + " تنظیم قوانین"), callback_data="set_rules")],
                [InlineKeyboardButton(GLASS_DESIGN['button']['danger'].replace('[TEXT]', GLASS_DESIGN['close'] + " بستن"), callback_data="close")]
            ]
            admin_panel_text += f"\n\n{GLASS_DESIGN['info']} نمایش ساده شده برای گروه‌های بزرگ"
            sent_message = update.message.reply_text(
                admin_panel_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            context.job_queue.run_once(
                self.remove_keyboard_callback,
                60,
                context={'chat_id': chat_id, 'message_id': sent_message.message_id}
            )
        else:
            self.admin_panel.handle_admin_command(update, context)
    def get_iran_datetime(self):
        """Get current date and time in Iran timezone"""
        tehran_tz = pytz.timezone('Asia/Tehran')
        now = datetime.datetime.now(tehran_tz)
        persian_month_names = [
            "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", 
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ]
        persian_weekday_names = [
            "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یکشنبه"
        ]
        year = now.year - 621
        month_idx = now.month - 1
        day = now.day
        weekday_idx = now.weekday()
        if now.month < 3 or (now.month == 3 and now.day < 21):
            year -= 1
        if now.month == 1 and now.day < 21:
            month_idx = 9
            day += 10
        elif now.month == 2 and now.day < 20:
            month_idx = 10
            day += 11
        elif now.month == 3 and now.day < 21:
            month_idx = 11
            day += 9
        elif now.month == 4 and now.day < 21:
            month_idx = 0
            day += 11
        elif now.month == 5 and now.day < 22:
            month_idx = 1
            day += 10
        elif now.month == 6 and now.day < 22:
            month_idx = 2
            day += 10
        elif now.month == 7 and now.day < 23:
            month_idx = 3
            day += 9
        elif now.month == 8 and now.day < 23:
            month_idx = 4
            day += 9
        elif now.month == 9 and now.day < 23:
            month_idx = 5
            day += 9
        elif now.month == 10 and now.day < 23:
            month_idx = 6
            day += 8
        elif now.month == 11 and now.day < 22:
            month_idx = 7
            day += 9
        elif now.month == 12 and now.day < 22:
            month_idx = 8
            day += 9
        else:
            month_idx = 9
            day -= 21
        persian_date = f"{persian_weekday_names[weekday_idx]} {day} {persian_month_names[month_idx]} {year}"
        persian_time = now.strftime("%H:%M:%S")
        return persian_date, persian_time
    def time_command(self, update, context):
        """Handle the /time command"""
        persian_date, persian_time = self.get_iran_datetime()
        now = datetime.datetime.now(pytz.timezone('Asia/Tehran'))
        weekday_persian = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یکشنبه"][now.weekday()]
        time_text = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["sparkle"]} *ساعت و تاریخ ایران* {GLASS_DESIGN["clock"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["calendar"]} *تاریخ:* {persian_date}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["clock"]} *ساعت:* {persian_time}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["star"]} *روز هفته:* {weekday_persian}
{GLASS_DESIGN["footer"]}"""
        update.message.reply_text(
            time_text,
            parse_mode=ParseMode.MARKDOWN
        )
    def lock_command(self, update, context):
        """Lock the group for a specified duration"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        if not self.admin_panel.is_admin(user.id):
            update.message.reply_text(f"{GLASS_DESIGN['error']} شما دسترسی به این دستور را ندارید.")
            return
        duration = None
        if context.args and len(context.args) > 0:
            try:
                time_arg = context.args[0].lower()
                value = int(''.join(filter(str.isdigit, time_arg)))
                if 'm' in time_arg:
                    duration = value * 60
                elif 'h' in time_arg:
                    duration = value * 3600
                elif 'd' in time_arg:
                    duration = value * 86400
                else:
                    duration = int(time_arg)
            except:
                duration = 3600
        else:
            duration = 3600
        if duration < 60:
            duration_text = f"{duration} ثانیه"
        elif duration < 3600:
            duration_text = f"{duration // 60} دقیقه"
        elif duration < 86400:
            duration_text = f"{duration // 3600} ساعت"
        else:
            duration_text = f"{duration // 86400} روز"
        try:
            permissions = ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            )
            context.bot.set_chat_permissions(chat_id, permissions)
            self.db.update_group_setting(chat_id, "locked", True)
            start_date, start_time = self.get_iran_datetime()
            end_timestamp = time.time() + duration
            end_datetime = datetime.datetime.fromtimestamp(end_timestamp, pytz.timezone('Asia/Tehran'))
            if duration >= 86400:
                days = duration // 86400
                tehran_tz = pytz.timezone('Asia/Tehran')
                now = datetime.datetime.now(tehran_tz)
                future_date = now + datetime.timedelta(days=days)
                future_persian_date, _ = self.get_iran_datetime_from_datetime(future_date)
                end_date = future_persian_date
            else:
                end_date = start_date
            end_time = end_datetime.strftime("%H:%M:%S")
            context.job_queue.run_once(
                self.unlock_job,
                duration,
                context={'chat_id': chat_id, 'user_id': user.id}
            )
            lock_message = MESSAGE_TEMPLATES["timed_lock"].format(
                admin=f"[{user.first_name}](tg://user?id={user.id})",
                duration=duration_text,
                start_date=start_date,
                start_time=start_time,
                end_date=end_date,
                end_time=end_time
            )
            update.message.reply_text(
                lock_message,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            update.message.reply_text(f"{GLASS_DESIGN['error']} خطا در قفل کردن گروه: {str(e)}")
    def unlock_job(self, context):
        """Job to unlock the group after the specified duration"""
        job_data = context.job.context
        chat_id = job_data['chat_id']
        user_id = job_data['user_id']
        try:
            permissions = ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
            context.bot.set_chat_permissions(chat_id, permissions)
            self.db.update_group_setting(chat_id, "locked", False)
            current_date, current_time = self.get_iran_datetime()
            unlock_message = MESSAGE_TEMPLATES["unlock"].format(
                admin="سیستم (زمان قفل به پایان رسید)",
                date=current_date,
                time=current_time
            )
            context.bot.send_message(
                chat_id,
                unlock_message,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            print(f"Error in unlock_job: {str(e)}")
    def unlock_command(self, update, context):
        """Unlock the group manually"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        if not self.admin_panel.is_admin(user.id):
            update.message.reply_text(f"{GLASS_DESIGN['error']} شما دسترسی به این دستور را ندارید.")
            return
        try:
            permissions = ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
            context.bot.set_chat_permissions(chat_id, permissions)
            self.db.update_group_setting(chat_id, "locked", False)
            current_date, current_time = self.get_iran_datetime()
            unlock_message = MESSAGE_TEMPLATES["unlock"].format(
                admin=f"[{user.first_name}](tg://user?id={user.id})",
                date=current_date,
                time=current_time
            )
            update.message.reply_text(
                unlock_message,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            update.message.reply_text(f"{GLASS_DESIGN['error']} خطا در باز کردن قفل گروه: {str(e)}")
    def persian_lock_command(self, update, context):
        """Handle Persian lock command"""
        text = update.message.text.strip()
        parts = text.split()
        if len(parts) > 1:
            context.args = parts[1:]
        else:
            context.args = []
        return self.lock_command(update, context)
    def persian_unlock_command(self, update, context):
        """Handle Persian unlock command"""
        return self.unlock_command(update, context)
    def create_voice_call(self, update, context):
        """Create a voice chat in the group"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        if not self.admin_panel.is_admin(user.id):
            update.message.reply_text(f"{GLASS_DESIGN['error']} شما دسترسی به این دستور را ندارید.")
            return
        try:
            context.bot.create_chat_invite_link(chat_id)
            persian_date, persian_time = self.get_iran_datetime()
            update.message.reply_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} 🎙️ *ویس چت ایجاد شد* ✨
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["admin"]} *توسط:* [{user.first_name}](tg://user?id={user.id})
{GLASS_DESIGN["side"]} {GLASS_DESIGN["calendar"]} *تاریخ:* {persian_date}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["clock"]} *ساعت:* {persian_time}
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            update.message.reply_text(f"{GLASS_DESIGN['error']} خطا در ایجاد ویس چت: {str(e)}")
    def end_voice_call(self, update, context):
        """End a voice chat in the group"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        if not self.admin_panel.is_admin(user.id):
            update.message.reply_text(f"{GLASS_DESIGN['error']} شما دسترسی به این دستور را ندارید.")
            return
        try:
            persian_date, persian_time = self.get_iran_datetime()
            update.message.reply_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} 🎙️ *ویس چت پایان یافت* 🔇
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["admin"]} *توسط:* [{user.first_name}](tg://user?id={user.id})
{GLASS_DESIGN["side"]} {GLASS_DESIGN["calendar"]} *تاریخ:* {persian_date}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["clock"]} *ساعت:* {persian_time}
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            update.message.reply_text(f"{GLASS_DESIGN['error']} خطا در پایان دادن به ویس چت: {str(e)}")
    def pin_message(self, update, context):
        """Pin a message in the group"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        if not self.admin_panel.is_admin(user.id):
            update.message.reply_text(f"{GLASS_DESIGN['error']} شما دسترسی به این دستور را ندارید.")
            return
        if not update.message.reply_to_message:
            update.message.reply_text(f"{GLASS_DESIGN['error']} لطفا این دستور را روی پیام مورد نظر ریپلای کنید.")
            return
        try:
            message_id = update.message.reply_to_message.message_id
            context.bot.pin_chat_message(chat_id, message_id)
            persian_date, persian_time = self.get_iran_datetime()
            update.message.reply_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} 📌 *پیام پین شد* ✨
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["admin"]} *توسط:* [{user.first_name}](tg://user?id={user.id})
{GLASS_DESIGN["side"]} {GLASS_DESIGN["calendar"]} *تاریخ:* {persian_date}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["clock"]} *ساعت:* {persian_time}
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            update.message.reply_text(f"{GLASS_DESIGN['error']} خطا در پین کردن پیام: {str(e)}")
    def unpin_message(self, update, context):
        """Unpin a message in the group"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        if not self.admin_panel.is_admin(user.id):
            update.message.reply_text(f"{GLASS_DESIGN['error']} شما دسترسی به این دستور را ندارید.")
            return
        try:
            if update.message.reply_to_message:
                message_id = update.message.reply_to_message.message_id
                context.bot.unpin_chat_message(chat_id, message_id)
            else:
                context.bot.unpin_chat_message(chat_id)
            persian_date, persian_time = self.get_iran_datetime()
            update.message.reply_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} 📌 *پیام از پین برداشته شد* 🔄
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["admin"]} *توسط:* [{user.first_name}](tg://user?id={user.id})
{GLASS_DESIGN["side"]} {GLASS_DESIGN["calendar"]} *تاریخ:* {persian_date}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["clock"]} *ساعت:* {persian_time}
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            update.message.reply_text(f"{GLASS_DESIGN['error']} خطا در برداشتن پین پیام: {str(e)}")
    def delete_messages(self, update, context):
        """Delete messages in the group"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        if not self.admin_panel.is_admin(user.id):
            update.message.reply_text(f"{GLASS_DESIGN['error']} شما دسترسی به این دستور را ندارید.")
            return
        if not update.message.reply_to_message:
            update.message.reply_text(f"{GLASS_DESIGN['error']} لطفا این دستور را روی پیام مورد نظر ریپلای کنید.")
            return
        try:
            message_id = update.message.reply_to_message.message_id
            context.bot.delete_message(chat_id, message_id)
            context.bot.delete_message(chat_id, update.message.message_id)
        except Exception as e:
            update.message.reply_text(f"{GLASS_DESIGN['error']} خطا در حذف پیام: {str(e)}")
    def persian_pin_command(self, update, context):
        """Handle Persian pin command"""
        return self.pin_message(update, context)
    def persian_unpin_command(self, update, context):
        """Handle Persian unpin command"""
        return self.unpin_message(update, context)
    def persian_delete_command(self, update, context):
        """Handle Persian delete command"""
        return self.delete_messages(update, context)
    def persian_voice_call_command(self, update, context):
        """Handle Persian voice call command"""
        text = update.message.text.strip().lower()
        if "ایجاد" in text or "شروع" in text:
            return self.create_voice_call(update, context)
        else:
            return self.end_voice_call(update, context) 
    def persian_user_info_command(self, update, context):
        """Handle Persian user info command"""
        text = update.message.text.strip()
        parts = text.split()
        if len(parts) > 1:
            context.args = parts[1:]
        else:
            context.args = []
        return self.user_info_command(update, context)
    def top_command(self, update, context):
        """Show top users in the group"""
        chat_id = update.effective_chat.id
        keyboard = [
            [
                InlineKeyboardButton(
                    GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['user'] + " کاربران فعال"),
                    callback_data="top_users"
                ),
                InlineKeyboardButton(
                    GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['admin'] + " ادمین‌های فعال"),
                    callback_data="top_admins"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        persian_date, persian_time = self.get_iran_datetime()
        update.message.reply_text(
            f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["stats"]} *کاربران برتر گروه* {GLASS_DESIGN["crown"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} لطفا یکی از گزینه‌های زیر را انتخاب کنید:
{GLASS_DESIGN["side"]} 
{GLASS_DESIGN["side"]} {GLASS_DESIGN["user"]} کاربران فعال: 10 کاربر با بیشترین فعالیت
{GLASS_DESIGN["side"]} {GLASS_DESIGN["admin"]} ادمین‌های فعال: 10 ادمین با بیشترین فعالیت
{GLASS_DESIGN["side"]} 
{GLASS_DESIGN["side"]} {GLASS_DESIGN["calendar"]} *تاریخ:* {persian_date}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["clock"]} *ساعت:* {persian_time}
{GLASS_DESIGN["footer"]}""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    def top_button_handler(self, update, context):
        """Handle top users button callbacks"""
        query = update.callback_query
        chat_id = query.message.chat_id
        callback_data = query.data
        query.answer()
        persian_date, persian_time = self.get_iran_datetime()
        if callback_data == "top_users":
            top_users = self.db.get_top_users(chat_id, 10, admins_only=False)
            message = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["user"]} 10 کاربر برتر گروه {GLASS_DESIGN["fire"]}
{GLASS_DESIGN["separator"]}"""
            for i, user in enumerate(top_users):
                if user['is_admin']:
                    continue
                rank_emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
                name = user['first_name']
                if user['last_name']:
                    name += f" {user['last_name']}"
                username = f"@{user['username']}" if user['username'] else ""
                safe_name = name.replace("*", "").replace("_", "").replace("`", "").replace("[", "").replace("]", "")
                message += f"""
{GLASS_DESIGN["side"]} {rank_emoji} {safe_name} {username}
{GLASS_DESIGN["side"]}   {GLASS_DESIGN["message_limit"]} تعداد پیام: {user['message_count']}"""
            message += f"""
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["calendar"]} تاریخ: {persian_date}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["clock"]} ساعت: {persian_time}
{GLASS_DESIGN["footer"]}"""
            keyboard = [
                [
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['secondary'].replace('[TEXT]', GLASS_DESIGN['back'] + " بازگشت"),
                        callback_data="top_back"
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            try:
                query.edit_message_text(
                    message,
                    parse_mode=None,
                    reply_markup=reply_markup
                )
            except Exception as e:
                print(f"Error in edit_message_text: {str(e)}")
                short_message = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["user"]} 10 کاربر برتر گروه {GLASS_DESIGN["fire"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} خطا در نمایش لیست کاربران
{GLASS_DESIGN["footer"]}"""
                query.edit_message_text(
                    short_message,
                    parse_mode=None,
                    reply_markup=reply_markup
                )
        elif callback_data == "top_admins":
            top_admins = self.db.get_top_users(chat_id, 10, admins_only=True)
            message = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["admin"]} 10 ادمین برتر گروه {GLASS_DESIGN["crown"]}
{GLASS_DESIGN["separator"]}"""
            for i, admin in enumerate(top_admins):
                rank_emoji = "👑" if i == 0 else "💎" if i == 1 else "🏆" if i == 2 else f"{i+1}."
                name = admin['first_name']
                if admin['last_name']:
                    name += f" {admin['last_name']}"
                username = f"@{admin['username']}" if admin['username'] else ""
                safe_name = name.replace("*", "").replace("_", "").replace("`", "").replace("[", "").replace("]", "")
                message += f"""
{GLASS_DESIGN["side"]} {rank_emoji} {safe_name} {username}
{GLASS_DESIGN["side"]}   {GLASS_DESIGN["message_limit"]} تعداد پیام: {admin['message_count']}"""
            message += f"""
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["calendar"]} تاریخ: {persian_date}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["clock"]} ساعت: {persian_time}
{GLASS_DESIGN["footer"]}"""
            keyboard = [
                [
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['secondary'].replace('[TEXT]', GLASS_DESIGN['back'] + " بازگشت"),
                        callback_data="top_back"
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            try:
                query.edit_message_text(
                    message,
                    parse_mode=None,
                    reply_markup=reply_markup
                )
            except Exception as e:
                print(f"Error in edit_message_text: {str(e)}")
                short_message = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["admin"]} 10 ادمین برتر گروه {GLASS_DESIGN["crown"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} خطا در نمایش لیست ادمین‌ها
{GLASS_DESIGN["footer"]}"""
                query.edit_message_text(
                    short_message,
                    parse_mode=None,
                    reply_markup=reply_markup
                )
        elif callback_data == "top_back":
            keyboard = [
                [
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['user'] + " کاربران فعال"),
                        callback_data="top_users"
                    ),
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['admin'] + " ادمین‌های فعال"),
                        callback_data="top_admins"
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["stats"]} کاربران برتر گروه {GLASS_DESIGN["crown"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} لطفا یکی از گزینه‌های زیر را انتخاب کنید:
{GLASS_DESIGN["side"]} 
{GLASS_DESIGN["side"]} {GLASS_DESIGN["user"]} کاربران فعال: 10 کاربر با بیشترین فعالیت
{GLASS_DESIGN["side"]} {GLASS_DESIGN["admin"]} ادمین‌های فعال: 10 ادمین با بیشترین فعالیت
{GLASS_DESIGN["side"]} 
{GLASS_DESIGN["side"]} {GLASS_DESIGN["calendar"]} تاریخ: {persian_date}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["clock"]} ساعت: {persian_time}
{GLASS_DESIGN["footer"]}""",
                parse_mode=None,
                reply_markup=reply_markup
            )
    def promote_command(self, update, context):
        """Promote a user to admin"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        if user.id != ADMIN_ID:
            update.message.reply_text(f"{GLASS_DESIGN['error']} فقط ادمین اصلی می‌تواند کاربران را ارتقا دهد.")
            return
        target_user = self.get_target_user(update, context)
        if not target_user:
            update.message.reply_text(f"{GLASS_DESIGN['error']} لطفا کاربر مورد نظر را مشخص کنید.")
            return
        if self.admin_panel.is_admin(target_user.id):
            update.message.reply_text(f"{GLASS_DESIGN['error']} این کاربر در حال حاضر ادمین است.")
            return
        try:
            self.db.promote_user_to_admin(target_user.id)
            try:
                context.bot.promote_chat_member(
                    chat_id, 
                    target_user.id,
                    can_change_info=True,
                    can_delete_messages=True,
                    can_invite_users=True,
                    can_restrict_members=True,
                    can_pin_messages=True,
                    can_promote_members=False
                )
            except Exception as e:
                print(f"Could not promote user in Telegram: {str(e)}")
            persian_date, persian_time = self.get_iran_datetime()
            update.message.reply_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} 👑 *کاربر به ادمین ارتقا یافت* 👑
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["user"]} *کاربر:* [{target_user.first_name}](tg://user?id={target_user.id})
{GLASS_DESIGN["side"]} {GLASS_DESIGN["admin"]} *توسط:* [{user.first_name}](tg://user?id={user.id})
{GLASS_DESIGN["side"]} {GLASS_DESIGN["calendar"]} *تاریخ:* {persian_date}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["clock"]} *ساعت:* {persian_time}
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            update.message.reply_text(f"{GLASS_DESIGN['error']} خطا در ارتقا کاربر: {str(e)}")
    def demote_command(self, update, context):
        """Demote a user from admin"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        if user.id != ADMIN_ID:
            update.message.reply_text(f"{GLASS_DESIGN['error']} فقط ادمین اصلی می‌تواند ادمین‌ها را عزل کند.")
            return
        target_user = self.get_target_user(update, context)
        if not target_user:
            update.message.reply_text(f"{GLASS_DESIGN['error']} لطفا کاربر مورد نظر را مشخص کنید.")
            return
        if not self.admin_panel.is_admin(target_user.id):
            update.message.reply_text(f"{GLASS_DESIGN['error']} این کاربر ادمین نیست.")
            return
        if target_user.id == ADMIN_ID:
            update.message.reply_text(f"{GLASS_DESIGN['error']} نمی‌توانید ادمین اصلی را عزل کنید.")
            return
        try:
            self.db.demote_admin(target_user.id)
            try:
                context.bot.promote_chat_member(
                    chat_id, 
                    target_user.id,
                    can_change_info=False,
                    can_delete_messages=False,
                    can_invite_users=False,
                    can_restrict_members=False,
                    can_pin_messages=False,
                    can_promote_members=False
                )
            except Exception as e:
                print(f"Could not demote user in Telegram: {str(e)}")
            persian_date, persian_time = self.get_iran_datetime()
            update.message.reply_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} ⬇️ *کاربر از ادمینی عزل شد* ⬇️
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["user"]} *کاربر:* [{target_user.first_name}](tg://user?id={target_user.id})
{GLASS_DESIGN["side"]} {GLASS_DESIGN["admin"]} *توسط:* [{user.first_name}](tg://user?id={user.id})
{GLASS_DESIGN["side"]} {GLASS_DESIGN["calendar"]} *تاریخ:* {persian_date}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["clock"]} *ساعت:* {persian_time}
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            update.message.reply_text(f"{GLASS_DESIGN['error']} خطا در عزل ادمین: {str(e)}")
    def list_admins_command(self, update, context):
        """List all admins"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        admins = self.db.get_all_admins()
        if not admins:
            update.message.reply_text(f"{GLASS_DESIGN['error']} هیچ ادمینی یافت نشد.")
            return
        persian_date, persian_time = self.get_iran_datetime()
        admin_list = ""
        for i, admin in enumerate(admins):
            name = admin['first_name']
            if admin['last_name']:
                name += f" {admin['last_name']}"
            username = f"@{admin['username']}" if admin['username'] else ""
            crown = "👑 " if admin['user_id'] == ADMIN_ID else ""
            admin_list += f"\n{GLASS_DESIGN['side']} {i+1}. {crown}[{name}](tg://user?id={admin['user_id']}) {username}"
        update.message.reply_text(
            f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} 👥 *لیست ادمین‌های گروه* 👥
{GLASS_DESIGN["separator"]}{admin_list}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["calendar"]} *تاریخ:* {persian_date}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["clock"]} *ساعت:* {persian_time}
{GLASS_DESIGN["footer"]}""",
            parse_mode=ParseMode.MARKDOWN
        )
    def persian_promote_command(self, update, context):
        """Handle Persian promote command"""
        text = update.message.text.strip()
        parts = text.split()
        if len(parts) > 1:
            context.args = parts[1:]
        else:
            context.args = []
        return self.promote_command(update, context)
    def persian_demote_command(self, update, context):
        """Handle Persian demote command"""
        text = update.message.text.strip()
        parts = text.split()
        if len(parts) > 1:
            context.args = parts[1:]
        else:
            context.args = []
        return self.demote_command(update, context)
    def currency_command(self, update, context):
        """Handle the /currency command to show currency rates"""
        try:
            rates = self.currency_api.get_current_rates()
            message = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} 💱 *نرخ ارز و طلا در بازار آزاد* 💱
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} 📅 *تاریخ:* {rates['date']}
{GLASS_DESIGN["side"]} 🕒 *ساعت:* {rates['time']}
{GLASS_DESIGN["separator"]}
"""
            for currency_code, currency_data in rates['currencies'].items():
                message += f"{GLASS_DESIGN['side']} {currency_data['flag']} *{currency_data['name']}:* {currency_data['price']} تومان\n"
            message += f"{GLASS_DESIGN['separator']}\n"
            message += f"{GLASS_DESIGN['side']} 🔄 برای مشاهده قیمت طلا: /gold\n"
            message += f"{GLASS_DESIGN['side']} 🔄 برای مشاهده قیمت ارزهای دیجیتال: /crypto\n"
            message += f"{GLASS_DESIGN['footer']}"
            update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            update.message.reply_text(f"خطا در دریافت نرخ ارز: {str(e)}")
    def crypto_command(self, update, context):
        """Handle the /crypto command to show cryptocurrency rates"""
        try:
            rates = self.currency_api.get_current_rates()
            message = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} 💰 *قیمت ارزهای دیجیتال* 💰
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} 📅 *تاریخ:* {rates['date']}
{GLASS_DESIGN["side"]} 🕒 *ساعت:* {rates['time']}
{GLASS_DESIGN["separator"]}
"""
            for crypto_code, crypto_data in rates['crypto'].items():
                if crypto_code == "usdt":
                    message += f"{GLASS_DESIGN['side']} {crypto_data['symbol']} *{crypto_data['name']}:* {crypto_data['price']} تومان\n"
                else:
                    message += f"{GLASS_DESIGN['side']} {crypto_data['symbol']} *{crypto_data['name']}:* {crypto_data['price']} دلار\n"
            message += f"{GLASS_DESIGN['separator']}\n"
            message += f"{GLASS_DESIGN['side']} 🔄 برای مشاهده قیمت ارز: /arz\n"
            message += f"{GLASS_DESIGN['side']} 🔄 برای مشاهده قیمت طلا: /gold\n"
            message += f"{GLASS_DESIGN['footer']}"
            update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            update.message.reply_text(f"خطا در دریافت قیمت ارزهای دیجیتال: {str(e)}")
    def gold_command(self, update, context):
        """Handle the /gold command to show gold rates"""
        try:
            rates = self.currency_api.get_current_rates()
            message = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} 🏆 *قیمت طلا و سکه* 🏆
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} 📅 *تاریخ:* {rates['date']}
{GLASS_DESIGN["side"]} 🕒 *ساعت:* {rates['time']}
{GLASS_DESIGN["separator"]}
"""
            for gold_code, gold_data in rates['gold'].items():
                message += f"{GLASS_DESIGN['side']} 🏆 *{gold_data['name']}:* {gold_data['price']} تومان\n"
            message += f"{GLASS_DESIGN['separator']}\n"
            message += f"{GLASS_DESIGN['side']} 🔄 برای مشاهده قیمت ارز: /arz\n"
            message += f"{GLASS_DESIGN['side']} 🔄 برای مشاهده قیمت ارزهای دیجیتال: /crypto\n"
            message += f"{GLASS_DESIGN['footer']}"
            update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            update.message.reply_text(f"خطا در دریافت قیمت طلا: {str(e)}")
    def get_iran_datetime_from_datetime(self, dt):
        """تبدیل یک تاریخ میلادی به تاریخ شمسی"""
        persian_month_names = [
            "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", 
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ]
        persian_weekday_names = [
            "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یکشنبه"
        ]
        year = dt.year - 621
        month_idx = dt.month - 1
        day = dt.day
        weekday_idx = dt.weekday()
        if dt.month < 3 or (dt.month == 3 and dt.day < 21):
            year -= 1
        if dt.month == 1 and dt.day < 21:
            month_idx = 9
            day += 10
        elif dt.month == 2 and dt.day < 20:
            month_idx = 10
            day += 11
        elif dt.month == 3 and dt.day < 21:
            month_idx = 11
            day += 9
        elif dt.month == 4 and dt.day < 21:
            month_idx = 0
            day += 11
        elif dt.month == 5 and dt.day < 22:
            month_idx = 1
            day += 10
        elif dt.month == 6 and dt.day < 22:
            month_idx = 2
            day += 10
        elif dt.month == 7 and dt.day < 23:
            month_idx = 3
            day += 9
        elif dt.month == 8 and dt.day < 23:
            month_idx = 4
            day += 9
        elif dt.month == 9 and dt.day < 23:
            month_idx = 5
            day += 9
        elif dt.month == 10 and dt.day < 23:
            month_idx = 6
            day += 8
        elif dt.month == 11 and dt.day < 22:
            month_idx = 7
            day += 9
        elif dt.month == 12 and dt.day < 22:
            month_idx = 8
            day += 9
        else:
            month_idx = 9
            day -= 21
        persian_date = f"{persian_weekday_names[weekday_idx]} {day} {persian_month_names[month_idx]} {year}"
        persian_time = dt.strftime("%H:%M:%S")
        return persian_date, persian_time
    def user_info_command(self, update, context):
        """Handle the /user command to show user info"""
        chat_id = update.effective_chat.id
        message = update.message
        target_user = self.get_target_user(update, context)
        if not target_user:
            message.reply_text("لطفا روی پیام کاربر ریپلای کنید یا نام کاربری را وارد کنید.")
            return
        self.cursor.execute('''
        SELECT message_count, last_active FROM user_activity
        WHERE group_id = ? AND user_id = ?
        ''', (chat_id, target_user.id))
        activity_data = self.cursor.fetchone()
        message_count = activity_data[0] if activity_data else 0
        last_active = activity_data[1] if activity_data else "نامشخص"
        self.cursor.execute('''
        SELECT warnings FROM group_members
        WHERE group_id = ? AND user_id = ?
        ''', (chat_id, target_user.id))
        warnings_data = self.cursor.fetchone()
        warnings = warnings_data[0] if warnings_data else 0
        try:
            chat_member = context.bot.get_chat_member(chat_id, target_user.id)
            status = chat_member.status
            status_persian = {
                "creator": "مالک گروه",
                "administrator": "ادمین",
                "member": "عضو عادی",
                "restricted": "محدود شده",
                "left": "ترک کرده",
                "kicked": "اخراج شده",
                "banned": "مسدود شده"
            }.get(status, status)
        except:
            status_persian = "نامشخص"
        self.cursor.execute('''
        SELECT joined_at FROM group_members
        WHERE group_id = ? AND user_id = ?
        ''', (chat_id, target_user.id))
        join_data = self.cursor.fetchone()
        join_date = join_data[0] if join_data else "نامشخص"
        is_admin = self.admin_panel.is_admin(target_user.id)
        role = "ادمین ربات" if is_admin else status_persian
        persian_date, persian_time = self.get_iran_datetime()
        username_text = f"@{target_user.username}" if target_user.username else "ندارد"
        account_creation = creation_date(target_user.id)
        from html import escape
        user_info = MESSAGE_TEMPLATES["user_info"].format(
            name=escape(f"{target_user.first_name} {target_user.last_name if target_user.last_name else ''}"),
            user_id=str(target_user.id),
            username=escape(username_text),
            message_count=str(message_count),
            warnings=str(warnings),
            status=escape(status_persian),
            join_date=escape(str(join_date)),
            last_active=escape(str(last_active)),
            role=escape(role),
            date=escape(persian_date),
            time=escape(persian_time),
            creation_date=escape(account_creation)
        )
        message.reply_text(
            user_info,
            parse_mode=ParseMode.HTML
        )
    def get_optimized_keyboard_for_large_groups(self, buttons_data, max_buttons_per_row=3, max_rows=2):
        """Create an optimized keyboard for large public groups
        Args:
            buttons_data: List of tuples (button_text, callback_data)
            max_buttons_per_row: Maximum buttons per row (default: 3)
            max_rows: Maximum number of rows (default: 2)
        """
        keyboard = []
        current_row = []
        limited_buttons = buttons_data[:max_buttons_per_row * max_rows]
        for i, (text, callback_data) in enumerate(limited_buttons):
            if i % max_buttons_per_row == 0 and current_row:
                keyboard.append(current_row)
                current_row = []
            current_row.append(InlineKeyboardButton(text, callback_data=callback_data))
        if current_row:
            keyboard.append(current_row)
        return InlineKeyboardMarkup(keyboard)
    def handle_keyboard_for_group_size(self, update, context, message_text, buttons_data):
        """Send appropriate keyboard based on group size
        For large public groups, use optimized keyboard with fewer buttons
        For smaller groups, use normal keyboard
        """
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        is_large_public_group = False
        try:
            if chat_type in ["supergroup"] and not update.effective_chat.username:
                member_count = context.bot.get_chat_member_count(chat_id)
                is_large_public_group = member_count > 1000
        except Exception:
            is_large_public_group = chat_type in ["supergroup"]
        if is_large_public_group:
            keyboard = self.get_optimized_keyboard_for_large_groups(buttons_data)
            sent_message = context.bot.send_message(
                chat_id=chat_id,
                text=f"{message_text}\n\n{GLASS_DESIGN['info']} این دکمه‌ها برای بهبود عملکرد در گروه‌های بزرگ بهینه شده‌اند.",
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
            context.job_queue.run_once(
                self.remove_keyboard_callback,
                60,
                context={'chat_id': chat_id, 'message_id': sent_message.message_id}
            )
        else:
            keyboard = []
            current_row = []
            for i, (text, callback_data) in enumerate(buttons_data):
                if i % 2 == 0 and current_row:
                    keyboard.append(current_row)
                    current_row = []
                current_row.append(InlineKeyboardButton(text, callback_data=callback_data))
            if current_row:
                keyboard.append(current_row)
            context.bot.send_message(
                chat_id=chat_id,
                text=message_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
    def remove_keyboard_callback(self, context):
        """Callback to remove keyboard after timeout"""
        job_data = context.job.context
        chat_id = job_data['chat_id']
        message_id = job_data['message_id']
        try:
            context.bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=None
            )
        except (BadRequest, Unauthorized):
            pass