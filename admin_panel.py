from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ChatPermissions
from telegram.ext import ConversationHandler
from config import ADMIN_ID, ADMIN_PANEL_SETTINGS, GLASS_DESIGN, MESSAGE_TEMPLATES
import datetime
import pytz
import time
MAIN_MENU, GROUP_SETTINGS, STATS, CUSTOM_COMMANDS, SET_RULES, ADMIN_MANAGEMENT = range(6)
class AdminPanel:
    def __init__(self, db):
        self.db = db
    def is_admin(self, user_id):
        """Check if user is the main admin or a group admin"""
        return user_id == ADMIN_ID or self.db.is_user_admin(user_id)
    def get_main_menu_keyboard(self):
        """Get the main admin panel keyboard"""
        keyboard = [
            [InlineKeyboardButton(GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['settings'] + " تنظیمات گروه"), callback_data="settings")],
            [InlineKeyboardButton(GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['stats'] + " آمار گروه"), callback_data="stats")],
            [InlineKeyboardButton(GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['custom_commands'] + " دستورات سفارشی"), callback_data="custom_commands")],
            [InlineKeyboardButton(GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['rules'] + " تنظیم قوانین"), callback_data="set_rules")],
            [InlineKeyboardButton(GLASS_DESIGN['button']['primary'].replace('[TEXT]', GLASS_DESIGN['admin'] + " مدیریت ادمین‌ها"), callback_data="admin_management")],
            [InlineKeyboardButton(GLASS_DESIGN['button']['danger'].replace('[TEXT]', GLASS_DESIGN['close'] + " بستن"), callback_data="close")]
        ]
        return InlineKeyboardMarkup(keyboard)
    def get_settings_keyboard(self, chat_id, is_large_group=False):
        """Get the settings keyboard for a group"""
        settings = self.db.get_group_settings(chat_id)
        if not settings:
            return None
        if is_large_group:
            keyboard = [
                [InlineKeyboardButton(
                    f"{GLASS_DESIGN['link']} ضد لینک: {'✅' if settings['antilink_enabled'] else '❌'}",
                    callback_data=f"toggle_antilink_{0 if settings['antilink_enabled'] else 1}"
                )],
                [InlineKeyboardButton(
                    f"{GLASS_DESIGN['profanity']} ضد فحش: {'✅' if settings['antiprofanity_enabled'] else '❌'}",
                    callback_data=f"toggle_antiprofanity_{0 if settings['antiprofanity_enabled'] else 1}"
                )],
                [InlineKeyboardButton(
                    f"🔄 ضد اسپم: {'✅' if settings['antispam_enabled'] else '❌'}",
                    callback_data=f"toggle_antispam_{0 if settings['antispam_enabled'] else 1}"
                )],
                [InlineKeyboardButton(
                    f"{GLASS_DESIGN['welcome']} خوشامدگویی: {'✅' if settings['welcome_enabled'] else '❌'}",
                    callback_data=f"toggle_welcome_{0 if settings['welcome_enabled'] else 1}"
                )],
                [InlineKeyboardButton(
                    GLASS_DESIGN['button']['secondary'].replace('[TEXT]', GLASS_DESIGN['back'] + " بازگشت"),
                    callback_data="back_to_main"
                )]
            ]
            return InlineKeyboardMarkup(keyboard)
        keyboard = [
            [InlineKeyboardButton(
                f"{GLASS_DESIGN['link']} ضد لینک: {'✅' if settings['antilink_enabled'] else '❌'}",
                callback_data=f"toggle_antilink_{0 if settings['antilink_enabled'] else 1}"
            )],
            [InlineKeyboardButton(
                f"{GLASS_DESIGN['profanity']} ضد فحش: {'✅' if settings['antiprofanity_enabled'] else '❌'}",
                callback_data=f"toggle_antiprofanity_{0 if settings['antiprofanity_enabled'] else 1}"
            )],
            [InlineKeyboardButton(
                f"{GLASS_DESIGN['forward']} ضد فوروارد: {'✅' if settings['antiforward_enabled'] else '❌'}",
                callback_data=f"toggle_antiforward_{0 if settings['antiforward_enabled'] else 1}"
            )],
            [InlineKeyboardButton(
                f"{GLASS_DESIGN['porn']} ضد پورن: {'✅' if settings['antiporn_enabled'] else '❌'}",
                callback_data=f"toggle_antiporn_{0 if settings['antiporn_enabled'] else 1}"
            )],
            [InlineKeyboardButton(
                f"🔄 ضد اسپم: {'✅' if settings['antispam_enabled'] else '❌'}",
                callback_data=f"toggle_antispam_{0 if settings['antispam_enabled'] else 1}"
            )],
            [InlineKeyboardButton(
                f"🚫 ضد خیانت: {'✅' if settings['anticheating_enabled'] else '❌'}",
                callback_data=f"toggle_anticheating_{0 if settings['anticheating_enabled'] else 1}"
            )],
            [InlineKeyboardButton(
                f"🤖 ضد تبچی: {'✅' if settings['antitabchi_enabled'] else '❌'}",
                callback_data=f"toggle_antitabchi_{0 if settings['antitabchi_enabled'] else 1}"
            )],
            [InlineKeyboardButton(
                f"{GLASS_DESIGN['welcome']} خوشامدگویی: {'✅' if settings['welcome_enabled'] else '❌'}",
                callback_data=f"toggle_welcome_{0 if settings['welcome_enabled'] else 1}"
            )],
            [InlineKeyboardButton(
                f"{GLASS_DESIGN['strict']} حالت سختگیرانه: {'✅' if settings['strict_mode'] else '❌'}",
                callback_data=f"toggle_strict_{0 if settings['strict_mode'] else 1}"
            )],
            [InlineKeyboardButton(
                f"{GLASS_DESIGN['lock']} قفل گروه: {'✅' if settings['locked'] else '❌'}",
                callback_data=f"toggle_lock_{0 if settings['locked'] else 1}"
            )],
            [InlineKeyboardButton(
                GLASS_DESIGN['button']['secondary'].replace('[TEXT]', GLASS_DESIGN['back'] + " بازگشت"),
                callback_data="back_to_main"
            )]
        ]
        return InlineKeyboardMarkup(keyboard)
    def get_stats_keyboard(self, chat_id):
        """Get the stats keyboard"""
        keyboard = [
            [
                InlineKeyboardButton(GLASS_DESIGN['button']['info'].replace('[TEXT]', '7 روز'), callback_data="stats_7"),
                InlineKeyboardButton(GLASS_DESIGN['button']['info'].replace('[TEXT]', '30 روز'), callback_data="stats_30")
            ],
            [InlineKeyboardButton(
                GLASS_DESIGN['button']['secondary'].replace('[TEXT]', GLASS_DESIGN['back'] + " بازگشت"), 
                callback_data="back_to_main"
            )]
        ]
        return InlineKeyboardMarkup(keyboard)
    def get_custom_commands_keyboard(self, chat_id):
        """Get the custom commands keyboard"""
        commands = self.db.get_all_custom_commands(chat_id)
        button_text = GLASS_DESIGN['button']['success'].replace('[TEXT]', GLASS_DESIGN['add'] + " افزودن دستور جدید")
        keyboard = [
            [InlineKeyboardButton(
                button_text, 
                callback_data="add_command"
            )]
        ]
        for cmd in commands:
            keyboard.append([
                InlineKeyboardButton(f"/{cmd}", callback_data=f"view_command_{cmd}"),
                InlineKeyboardButton(
                    GLASS_DESIGN['button']['danger'].replace('[TEXT]', GLASS_DESIGN['remove']), 
                    callback_data=f"delete_command_{cmd}"
                )
            ])
        button_text = GLASS_DESIGN['button']['secondary'].replace('[TEXT]', GLASS_DESIGN['back'] + " بازگشت")
        keyboard.append([InlineKeyboardButton(
            button_text, 
            callback_data="back_to_main"
        )])
        return InlineKeyboardMarkup(keyboard)
    def get_admin_management_keyboard(self, chat_id):
        """Get the admin management keyboard"""
        admins = self.db.get_all_admins()
        keyboard = [
            [InlineKeyboardButton(
                GLASS_DESIGN['button']['success'].replace('[TEXT]', GLASS_DESIGN['add'] + " افزودن ادمین جدید"), 
                callback_data="add_admin"
            )]
        ]
        for admin in admins:
            if admin['user_id'] != ADMIN_ID:
                name = admin['first_name']
                if admin['last_name']:
                    name += f" {admin['last_name']}"
                keyboard.append([
                    InlineKeyboardButton(
                        f"{name} {'@' + admin['username'] if admin['username'] else ''}",
                        callback_data=f"view_admin_{admin['user_id']}"
                    ),
                    InlineKeyboardButton(
                        GLASS_DESIGN['button']['danger'].replace('[TEXT]', GLASS_DESIGN['remove']),
                        callback_data=f"demote_admin_{admin['user_id']}"
                    )
                ])
        keyboard.append([
            InlineKeyboardButton(
                GLASS_DESIGN['button']['secondary'].replace('[TEXT]', GLASS_DESIGN['back'] + " بازگشت"),
                callback_data="back_to_main"
            )
        ])
        return InlineKeyboardMarkup(keyboard)
    def format_stats(self, stats, days=7):
        """Format statistics for display"""
        if not stats:
            return f"{GLASS_DESIGN['side']} {GLASS_DESIGN['info']} آماری موجود نیست"
        total_messages = sum(day_stats["messages_count"] for day_stats in stats.values())
        total_new_members = sum(day_stats["new_members"] for day_stats in stats.values())
        total_removed = sum(day_stats["removed_members"] for day_stats in stats.values())
        total_warnings = sum(day_stats["warnings_issued"] for day_stats in stats.values())
        total_links = sum(day_stats["links_blocked"] for day_stats in stats.values())
        total_profanity = sum(day_stats["profanity_blocked"] for day_stats in stats.values())
        total_forwards = sum(day_stats["forwards_blocked"] for day_stats in stats.values())
        total_porn = sum(day_stats.get("porn_blocked", 0) for day_stats in stats.values())
        total_spam = sum(day_stats.get("spam_blocked", 0) for day_stats in stats.values())
        total_cheating = sum(day_stats.get("cheating_blocked", 0) for day_stats in stats.values())
        total_tabchi = sum(day_stats.get("tabchi_blocked", 0) for day_stats in stats.values())
        return f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["sparkle"]} *آمار گروه در {days} روز گذشته* {GLASS_DESIGN["sparkle"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["message_limit"]} *تعداد پیام‌ها:* {total_messages}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["user"]} *اعضای جدید:* {total_new_members}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["ban"]} *اعضای حذف شده:* {total_removed}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["warn"]} *اخطارهای صادر شده:* {total_warnings}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["link"]} *لینک‌های مسدود شده:* {total_links}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["profanity"]} *پیام‌های حاوی فحش:* {total_profanity}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["forward"]} *فوروارد‌های مسدود شده:* {total_forwards}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["porn"]} *محتوای نامناسب مسدود شده:* {total_porn}
{GLASS_DESIGN["side"]} 🔄 *اسپم‌های مسدود شده:* {total_spam}
{GLASS_DESIGN["side"]} 🚫 *تبلیغات خارجی مسدود شده:* {total_cheating}
{GLASS_DESIGN["side"]} 🤖 *تبچی‌های شناسایی شده:* {total_tabchi}
{GLASS_DESIGN["footer"]}"""
    def handle_admin_command(self, update, context):
        """Handle the /admin command"""
        if update.callback_query:
            query = update.callback_query
            user_id = query.from_user.id
            chat_id = query.message.chat_id
            if not self.is_admin(user_id):
                query.answer(f"{GLASS_DESIGN['error']} شما دسترسی به پنل ادمین را ندارید.")
                return ConversationHandler.END
            is_large_public_group = False
            try:
                chat = context.bot.get_chat(chat_id)
                if chat.type in ["supergroup"] and not chat.username:
                    member_count = context.bot.get_chat_member_count(chat_id)
                    is_large_public_group = member_count > 1000
            except Exception:
                pass
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
            else:
                keyboard = self.get_main_menu_keyboard().inline_keyboard
            query.edit_message_text(
                admin_panel_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            user_id = update.effective_user.id
            if not self.is_admin(user_id):
                update.message.reply_text(f"{GLASS_DESIGN['error']} شما دسترسی به پنل ادمین را ندارید.")
                return ConversationHandler.END
            chat_id = update.effective_chat.id
            is_large_public_group = False
            try:
                chat = context.bot.get_chat(chat_id)
                if chat.type in ["supergroup"] and not chat.username:
                    member_count = context.bot.get_chat_member_count(chat_id)
                    is_large_public_group = member_count > 1000
            except Exception:
                if update.effective_chat.type in ["supergroup"]:
                    is_large_public_group = True
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
                update.message.reply_text(
                    admin_panel_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.get_main_menu_keyboard()
                )
        return MAIN_MENU
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
        except Exception:
            pass
    def handle_callback(self, update, context):
        """Handle callback queries from admin panel buttons"""
        query = update.callback_query
        user_id = query.from_user.id
        chat_id = query.message.chat_id
        callback_data = query.data
        print(f"Admin panel received callback: {callback_data}")
        query.answer()
        if not self.is_admin(user_id):
            query.answer(f"{GLASS_DESIGN['error']} شما دسترسی به پنل ادمین را ندارید.")
            return ConversationHandler.END
        if callback_data == "settings":
            is_large_group = False
            try:
                chat = context.bot.get_chat(chat_id)
                if chat.type in ["supergroup"] and not chat.username:
                    member_count = context.bot.get_chat_member_count(chat_id)
                    is_large_group = member_count > 1000
            except Exception:
                if context.bot.get_chat(chat_id).type in ["supergroup"]:
                    is_large_group = True
            settings_text = f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["settings"]} *تنظیمات گروه* {GLASS_DESIGN["settings"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["arrow_right"]} لطفا یکی از تنظیمات زیر را تغییر دهید:
{GLASS_DESIGN["footer"]}"""
            if is_large_group:
                settings_text += f"\n\n{GLASS_DESIGN['info']} نمایش ساده شده برای گروه‌های بزرگ"
            query.edit_message_text(
                settings_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.get_settings_keyboard(chat_id, is_large_group)
            )
            return GROUP_SETTINGS
        elif callback_data == "stats":
            query.edit_message_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["stats"]} *آمار گروه* {GLASS_DESIGN["stats"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["arrow_right"]} لطفا بازه زمانی مورد نظر را انتخاب کنید:
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.get_stats_keyboard(chat_id)
            )
            return STATS
        elif callback_data == "custom_commands":
            query.edit_message_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["custom_commands"]} *دستورات سفارشی* {GLASS_DESIGN["custom_commands"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["arrow_right"]} مدیریت دستورات سفارشی گروه:
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.get_custom_commands_keyboard(chat_id)
            )
            return CUSTOM_COMMANDS
        elif callback_data == "set_rules":
            query.edit_message_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["rules"]} *تنظیم قوانین گروه* {GLASS_DESIGN["rules"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} لطفا قوانین جدید گروه را ارسال کنید.
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} می‌توانید از Markdown استفاده کنید.
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} برای لغو، دستور /cancel را ارسال کنید.
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN
            )
            return SET_RULES
        elif callback_data == "close":
            query.edit_message_text(
                f"{GLASS_DESIGN['success']} پنل مدیریت بسته شد."
            )
            return ConversationHandler.END
        elif callback_data.startswith("toggle_"):
            parts = callback_data.split("_")
            setting_name = parts[1]
            value = int(parts[2])
            if setting_name == "antilink":
                self.db.update_group_setting(chat_id, "antilink_enabled", value)
                query.answer(f"ضد لینک {'فعال' if value else 'غیرفعال'} شد")
            elif setting_name == "antiprofanity":
                self.db.update_group_setting(chat_id, "antiprofanity_enabled", value)
                query.answer(f"ضد فحش {'فعال' if value else 'غیرفعال'} شد")
            elif setting_name == "antiforward":
                self.db.update_group_setting(chat_id, "antiforward_enabled", value)
                query.answer(f"ضد فوروارد {'فعال' if value else 'غیرفعال'} شد")
            elif setting_name == "antiporn":
                self.db.update_group_setting(chat_id, "antiporn_enabled", value)
                query.answer(f"ضد پورن {'فعال' if value else 'غیرفعال'} شد")
            elif setting_name == "antispam":
                self.db.update_group_setting(chat_id, "antispam_enabled", value)
                query.answer(f"ضد اسپم {'فعال' if value else 'غیرفعال'} شد")
            elif setting_name == "anticheating":
                self.db.update_group_setting(chat_id, "anticheating_enabled", value)
                query.answer(f"ضد خیانت {'فعال' if value else 'غیرفعال'} شد")
            elif setting_name == "antitabchi":
                self.db.update_group_setting(chat_id, "antitabchi_enabled", value)
                query.answer(f"ضد تبچی {'فعال' if value else 'غیرفعال'} شد")
            elif setting_name == "welcome":
                self.db.update_group_setting(chat_id, "welcome_enabled", value)
                query.answer(f"خوشامدگویی {'فعال' if value else 'غیرفعال'} شد")
            elif setting_name == "strict":
                self.db.update_group_setting(chat_id, "strict_mode", value)
                query.answer(f"حالت سختگیرانه {'فعال' if value else 'غیرفعال'} شد")
            elif setting_name == "lock":
                self.db.update_group_setting(chat_id, "locked", value)
                try:
                    bot = context.bot
                    if value:
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
                        bot.set_chat_permissions(chat_id, permissions)
                        tehran_tz = pytz.timezone('Asia/Tehran')
                        now = datetime.datetime.now(tehran_tz)
                        persian_date, persian_time = self.get_iran_datetime()
                        duration_text = "24 ساعت"
                        end_timestamp = time.time() + 86400
                        end_datetime = datetime.datetime.fromtimestamp(end_timestamp, pytz.timezone('Asia/Tehran'))
                        end_date = persian_date
                        end_time = end_datetime.strftime("%H:%M:%S")
                        lock_message = MESSAGE_TEMPLATES["timed_lock"].format(
                            admin=f"[{query.from_user.first_name}](tg://user?id={query.from_user.id})",
                            duration=duration_text,
                            start_date=persian_date,
                            start_time=persian_time,
                            end_date=end_date,
                            end_time=end_time
                        )
                        bot.send_message(
                            chat_id,
                            lock_message,
                            parse_mode=ParseMode.MARKDOWN
                        )
                    else:
                        permissions = ChatPermissions(
                            can_send_messages=True,
                            can_send_media_messages=True,
                            can_send_other_messages=True,
                            can_add_web_page_previews=True
                        )
                        bot.set_chat_permissions(chat_id, permissions)
                        persian_date, persian_time = self.get_iran_datetime()
                        unlock_message = MESSAGE_TEMPLATES["unlock"].format(
                            admin=f"[{query.from_user.first_name}](tg://user?id={query.from_user.id})",
                            date=persian_date,
                            time=persian_time
                        )
                        bot.send_message(
                            chat_id,
                            unlock_message,
                            parse_mode=ParseMode.MARKDOWN
                        )
                    query.answer(f"گروه {'قفل' if value else 'باز'} شد")
                except Exception as e:
                    query.answer(f"خطا در {'قفل' if value else 'باز'} کردن گروه: {str(e)}")
            is_large_group = False
            try:
                chat = context.bot.get_chat(chat_id)
                if chat.type in ["supergroup"] and not chat.username:
                    member_count = context.bot.get_chat_member_count(chat_id)
                    is_large_group = member_count > 1000
            except Exception:
                if context.bot.get_chat(chat_id).type in ["supergroup"]:
                    is_large_group = True
            query.edit_message_reply_markup(reply_markup=self.get_settings_keyboard(chat_id, is_large_group))
            return GROUP_SETTINGS
        elif callback_data == "set_message_limit":
            query.answer("این قابلیت هنوز پیاده‌سازی نشده است")
            return GROUP_SETTINGS
        elif callback_data == "back_to_main":
            query.edit_message_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["crown"]} *پنل مدیریت گروه* {GLASS_DESIGN["crown"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["crown"]} *پنل مدیریت گروه* {GLASS_DESIGN["crown"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["sparkle"]} به پنل مدیریت گروه خوش آمدید.
{GLASS_DESIGN["side"]} {GLASS_DESIGN["arrow_right"]} لطفا یکی از گزینه‌های زیر را انتخاب کنید:
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.get_main_menu_keyboard()
            )
            return MAIN_MENU
        elif callback_data.startswith("stats_"):
            days = int(callback_data.split("_")[1])
            stats = self.db.get_group_stats(chat_id, days)
            formatted_stats = self.format_stats(stats, days)
            query.edit_message_text(
                formatted_stats,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.get_stats_keyboard(chat_id)
            )
            return STATS
        elif callback_data == "add_command":
            query.edit_message_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["custom_commands"]} *افزودن دستور سفارشی* {GLASS_DESIGN["custom_commands"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["arrow_right"]} لطفا دستور را به صورت زیر ارسال کنید:
{GLASS_DESIGN["side"]} 
{GLASS_DESIGN["side"]} /نام_دستور پاسخ دستور
{GLASS_DESIGN["side"]} 
{GLASS_DESIGN["side"]} مثال: /سلام سلام، خوش آمدید!
{GLASS_DESIGN["side"]} 
{GLASS_DESIGN["side"]} برای لغو، /cancel را بفرستید.
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN
            )
            return CUSTOM_COMMANDS
        elif callback_data.startswith("view_command_"):
            command = callback_data.split("_")[2]
            response = self.db.get_custom_command(chat_id, command)
            query.edit_message_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["custom_commands"]} *دستور سفارشی* {GLASS_DESIGN["custom_commands"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["arrow_right"]} دستور: /{command}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["arrow_right"]} پاسخ: {response}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} برای بازگشت، دکمه بازگشت را بزنید.
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.get_custom_commands_keyboard(chat_id)
            )
            return CUSTOM_COMMANDS
        elif callback_data.startswith("delete_command_"):
            command = callback_data.split("_")[2]
            self.db.delete_custom_command(chat_id, command)
            query.edit_message_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["custom_commands"]} *دستورات سفارشی* {GLASS_DESIGN["custom_commands"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["success"]} دستور /{command} با موفقیت حذف شد.
{GLASS_DESIGN["side"]} {GLASS_DESIGN["arrow_right"]} لطفا یکی از گزینه‌های زیر را انتخاب کنید:
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.get_custom_commands_keyboard(chat_id)
            )
            return CUSTOM_COMMANDS
        elif callback_data == "admin_management":
            query.edit_message_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["admin"]} *مدیریت ادمین‌ها* {GLASS_DESIGN["admin"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["arrow_right"]} لطفا یکی از گزینه‌های زیر را انتخاب کنید:
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.get_admin_management_keyboard(chat_id)
            )
            return ADMIN_MANAGEMENT
        elif callback_data.startswith("view_admin_"):
            admin_id = int(callback_data.split("_")[2])
            admins = self.db.get_all_admins()
            admin = None
            for a in admins:
                if a['user_id'] == admin_id:
                    admin = a
                    break
            if admin:
                name = admin['first_name']
                if admin['last_name']:
                    name += f" {admin['last_name']}"
                username = f"@{admin['username']}" if admin['username'] else "بدون نام کاربری"
                query.edit_message_text(
                    f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["admin"]} *اطلاعات ادمین* {GLASS_DESIGN["admin"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["user"]} *نام:* {name}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} *نام کاربری:* {username}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} *شناسه کاربری:* {admin['user_id']}
{GLASS_DESIGN["footer"]}""",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.get_admin_management_keyboard(chat_id)
                )
            else:
                query.edit_message_text(
                    f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["error"]} *خطا* {GLASS_DESIGN["error"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["info"]} ادمین مورد نظر یافت نشد.
{GLASS_DESIGN["footer"]}""",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.get_admin_management_keyboard(chat_id)
                )
            return ADMIN_MANAGEMENT
        elif callback_data.startswith("demote_admin_"):
            admin_id = int(callback_data.split("_")[2])
            self.db.demote_admin(admin_id)
            query.edit_message_text(
                f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["admin"]} *مدیریت ادمین‌ها* {GLASS_DESIGN["admin"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["success"]} ادمین با موفقیت از سطح دسترسی کاسته شد.
{GLASS_DESIGN["footer"]}""",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.get_admin_management_keyboard(chat_id)
            )
            return ADMIN_MANAGEMENT
        query.answer("عملیات نامعتبر")
        return MAIN_MENU
    def set_rules(self, update, context):
        """Set new rules for the group"""
        chat_id = update.effective_chat.id
        new_rules = update.message.text
        self.db.update_group_setting(chat_id, "rules", new_rules)
        update.message.reply_text(
            f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["rules"]} *قوانین گروه* {GLASS_DESIGN["rules"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["success"]} قوانین گروه با موفقیت بروزرسانی شد.
{GLASS_DESIGN["footer"]}""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.get_main_menu_keyboard()
        )
        return MAIN_MENU
    def cancel(self, update, context):
        """Cancel the current operation"""
        update.message.reply_text(
            f"""{GLASS_DESIGN["header"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["close"]} *عملیات لغو شد* {GLASS_DESIGN["close"]}
{GLASS_DESIGN["separator"]}
{GLASS_DESIGN["side"]} {GLASS_DESIGN["arrow_right"]} به منوی اصلی بازگشتید.
{GLASS_DESIGN["footer"]}""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=self.get_main_menu_keyboard()
        )
        return MAIN_MENU
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