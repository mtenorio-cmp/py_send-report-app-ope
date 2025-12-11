import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from interfaces.database_interface import IDatabaseConnection
from interfaces.telegram_authorization_store import ITelegramAuthorizationStore
from interfaces.telegram_handlers_interfce import IBotHandlers
from services.data_analysis_service import DataAnalysisService
from services.documento_query_service import DocumentoQueryService
from datetime import date
from telegram import InputFile
import os

logger = logging.getLogger(__name__)


class BotHandlers(IBotHandlers):
    def __init__(
        self,
        admin_id: int,
        auth_store: ITelegramAuthorizationStore,
        db_connection: IDatabaseConnection,
    ):
        self.admin_id = int(admin_id)
        self.auth_store = auth_store
        self.db_connection = db_connection

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if self.auth_store.is_authorized(user_id):
            await update.message.reply_text("✅ Bienvenido, ya tienes acceso.")
        else:
            keyboard = [
                [
                    InlineKeyboardButton(
                        "✅ Aceptar", callback_data=f"accept_{user_id}"
                    ),
                    InlineKeyboardButton(
                        "❌ Rechazar", callback_data=f"reject_{user_id}"
                    ),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=self.admin_id,
                text=f"👤 Usuario {update.effective_user.first_name} ({user_id}) quiere acceder.",
                reply_markup=reply_markup,
            )
            await update.message.reply_text(
                "⏳ Tu solicitud está pendiente de aprobación..."
            )

    async def button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        action, user_id = query.data.split("_")
        user_id = int(user_id)
        logger.info(f"Admin {query.from_user.id} selected {action} for user {user_id}")

        if query.from_user.id == self.admin_id:
            if action == "accept":
                self.auth_store.add_user(
                    user_id, username=update.effective_user.first_name
                )
                await query.edit_message_text(f"✅ Usuario {user_id} autorizado.")
                await context.bot.send_message(
                    chat_id=user_id, text="🎉 ¡Tu acceso ha sido aprobado!"
                )
            elif action == "reject":
                await query.edit_message_text(f"❌ Usuario {user_id} rechazado.")
                await context.bot.send_message(
                    chat_id=user_id, text="🚫 Tu acceso fue rechazado."
                )

    async def ruta_programada_hoy(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user_id = update.effective_user.id
        if self.auth_store.is_authorized(user_id):
            mode = os.getenv("DEBUG")
            date_value = "2025-01-02" if mode == "True" else date.today()
            documento_query_service = DocumentoQueryService(
                db_connection=self.db_connection
            )  # Aquí deberías pasar la conexión real
            data_analysis_service = DataAnalysisService()

            df = documento_query_service.get_programados_del_dia(date_value)
            if df.empty:
                await update.message.reply_text("📭 No hay rutas programadas para hoy.")
                return

            path_rute_image = data_analysis_service.despachados_del_dia_detallado(
                df=df,
                ruta_salida="reporte_programados_hoy.png",
                date_programen=date_value,
            )
            if path_rute_image:
                with open(path_rute_image, "rb") as photo:
                    await update.message.reply_photo(
                        photo=InputFile(photo),
                        caption=f"📋 Rutas programadas para hoy ({date_value})",
                    )
            else:
                await update.message.reply_text(
                    "⚠️ No se pudo generar el reporte en imagen."
                )

        else:
            await update.message.reply_text(
                "🚫 No tienes permiso para usar este comando. Usa /start para solicitar acceso."
            )

    async def ruta_despachados(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user_id = update.effective_user.id
        if self.auth_store.is_authorized(user_id):
            mode = os.getenv("DEBUG")
            date_value = "2025-01-02" if mode == "True" else date.today()
            # date_value = date.today()
            documento_query_service = DocumentoQueryService(
                db_connection=self.db_connection
            )  # Aquí deberías pasar la conexión real
            data_analysis_service = DataAnalysisService()

            df = documento_query_service.get_programados_del_dia(date_value)
            if df.empty:
                await update.message.reply_text("📭 No hay rutas despachadas para hoy.")
                return

            path_rute_image = data_analysis_service.generar_reporte_imagen(
                df=df,
                ruta_salida="reporte_despachados_hoy.png",
                date_programen=date_value,
            )
            if path_rute_image:
                with open(path_rute_image, "rb") as photo:
                    await update.message.reply_photo(
                        photo=InputFile(photo),
                        caption=f"📋 Rutas despachadas para hoy ({date_value})",
                    )
            else:
                await update.message.reply_text(
                    "⚠️ No se pudo generar el reporte en imagen."
                )

        else:
            await update.message.reply_text(
                "🚫 No tienes permiso para usar este comando. Usa /start para solicitar acceso."
            )
