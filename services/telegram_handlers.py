import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from interfaces.telegram_authorization_store import ITelegramAuthorizationStore

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self, admin_id: int, auth_store: ITelegramAuthorizationStore):
        self.admin_id = int(admin_id)
        self.auth_store = auth_store

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if self.auth_store.is_authorized(user_id):
            await update.message.reply_text("✅ Bienvenido, ya tienes acceso.")
        else:
            keyboard = [[
                InlineKeyboardButton("✅ Aceptar", callback_data=f"accept_{user_id}"),
                InlineKeyboardButton("❌ Rechazar", callback_data=f"reject_{user_id}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=self.admin_id,
                text=f"👤 Usuario {update.effective_user.first_name} ({user_id}) quiere acceder.",
                reply_markup=reply_markup
            )
            await update.message.reply_text("⏳ Tu solicitud está pendiente de aprobación...")

    async def button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        action, user_id = query.data.split("_")
        user_id = int(user_id)
        logger.info(f"Admin {query.from_user.id} selected {action} for user {user_id}")

        if query.from_user.id == self.admin_id:
            if action == "accept":
                self.auth_store.add_user(user_id, username=update.effective_user.first_name)
                await query.edit_message_text(f"✅ Usuario {user_id} autorizado.")
                await context.bot.send_message(chat_id=user_id, text="🎉 ¡Tu acceso ha sido aprobado!")
            elif action == "reject":
                await query.edit_message_text(f"❌ Usuario {user_id} rechazado.")
                await context.bot.send_message(chat_id=user_id, text="🚫 Tu acceso fue rechazado.")
