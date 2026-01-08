"""
ConversationHandler для заполнения отчёта о топливе
"""
from datetime import datetime, date
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from bot.states import ReportStates
from bot.keyboards import (
    get_captain_keyboard,
    get_boat_keyboard,
    get_program_keyboard,
    get_private_program_keyboard,
    get_pier_keyboard,
    get_date_keyboard,
    get_skip_keyboard,
    get_photo_keyboard,
    get_confirm_keyboard,
    get_navigation_keyboard,
    get_main_menu_keyboard
)
from services.report_service import ReportData, report_service
from services.user_service import user_service


# ============== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==============

def get_report_data(context: ContextTypes.DEFAULT_TYPE) -> ReportData:
    """Получить данные отчёта из контекста"""
    if 'report' not in context.user_data:
        context.user_data['report'] = ReportData(telegram_user_id=0)
    return context.user_data['report']


def parse_date(text: str) -> date:
    """Парсинг даты из текста"""
    formats = ['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d']
    for fmt in formats:
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Неверный формат даты: {text}")


async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка кнопки 'Назад'"""
    query = update.callback_query
    await query.answer()
    
    # Получаем историю состояний
    history = context.user_data.get('state_history', [])
    
    if len(history) > 1:
        history.pop()  # Убираем текущее состояние
        prev_state = history[-1]
        context.user_data['state_history'] = history
        
        # Возвращаемся к предыдущему шагу
        return await goto_state(query, context, prev_state)
    
    return await cancel(update, context)


async def goto_state(query, context: ContextTypes.DEFAULT_TYPE, state: int) -> int:
    """Перейти к конкретному состоянию"""
    if state == ReportStates.CAPTAIN:
        await query.edit_message_text(
            "👨‍✈️ *Select captain:*",
            reply_markup=get_captain_keyboard(),
            parse_mode='Markdown'
        )
    elif state == ReportStates.BOAT:
        await query.edit_message_text(
            "🚤 *Select boat:*",
            reply_markup=get_boat_keyboard(),
            parse_mode='Markdown'
        )
    elif state == ReportStates.PROGRAM:
        await query.edit_message_text(
            "🏝 *Select program:*",
            reply_markup=get_program_keyboard(),
            parse_mode='Markdown'
        )
    elif state == ReportStates.PRIVATE_PROGRAM:
        await query.edit_message_text(
            "🏝 *Select private tour route:*",
            reply_markup=get_private_program_keyboard(),
            parse_mode='Markdown'
        )
    elif state == ReportStates.PIER:
        await query.edit_message_text(
            "⚓ *Select pier:*",
            reply_markup=get_pier_keyboard(),
            parse_mode='Markdown'
        )
    elif state == ReportStates.DEPARTURE_DATE:
        await query.edit_message_text(
            "📅 *Departure date:*\n\nEnter date (DD.MM.YYYY) or select a date:",
            reply_markup=get_date_keyboard("departure"),
            parse_mode='Markdown'
        )
    elif state == ReportStates.RETURN_DATE:
        await query.edit_message_text(
            "📅 *Return date:*\n\nEnter date (DD.MM.YYYY) or select a date:",
            reply_markup=get_date_keyboard("return"),
            parse_mode='Markdown'
        )
    elif state == ReportStates.REFILL_DATE:
        await query.edit_message_text(
            "📅 *Refill date:*\n\nEnter date (DD.MM.YYYY) or select a date:",
            reply_markup=get_date_keyboard("refill"),
            parse_mode='Markdown'
        )
    
    return state


def save_state(context: ContextTypes.DEFAULT_TYPE, state: int) -> None:
    """Сохранить состояние в историю"""
    if 'state_history' not in context.user_data:
        context.user_data['state_history'] = []
    context.user_data['state_history'].append(state)


# ============== ОБРАБОТЧИКИ СОСТОЯНИЙ ==============

async def start_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начать заполнение отчёта"""
    user = update.effective_user
    
    # Проверка доступа
    if not user_service.is_allowed(user.id):
        await update.message.reply_text("⛔ You don't have access to this bot.")
        return ConversationHandler.END
    
    # Инициализация данных
    context.user_data['report'] = ReportData(telegram_user_id=user.id)
    context.user_data['state_history'] = [ReportStates.CAPTAIN]
    
    await update.message.reply_text(
        "📝 *New Fuel Report*\n\n"
        "👨‍✈️ *Select captain:*",
        reply_markup=get_captain_keyboard(),
        parse_mode='Markdown'
    )
    return ReportStates.CAPTAIN


async def captain_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора капитана"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "back":
        return await cancel(update, context)
    if query.data == "cancel":
        return await cancel(update, context)
    
    captain = query.data.split(':')[1]
    get_report_data(context).captain_name = captain
    save_state(context, ReportStates.BOAT)
    
    await query.edit_message_text(
        f"✅ Captain: *{captain}*\n\n"
        "🚤 *Select boat:*",
        reply_markup=get_boat_keyboard(),
        parse_mode='Markdown'
    )
    return ReportStates.BOAT


async def boat_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора лодки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "back":
        return await handle_back(update, context)
    if query.data == "cancel":
        return await cancel(update, context)
    
    boat = query.data.split(':')[1]
    get_report_data(context).boat_name = boat
    save_state(context, ReportStates.PROGRAM)
    
    await query.edit_message_text(
        f"✅ Boat: *{boat}*\n\n"
        "🏝 *Select program:*",
        reply_markup=get_program_keyboard(),
        parse_mode='Markdown'
    )
    return ReportStates.PROGRAM


async def program_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора программы"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "back":
        return await handle_back(update, context)
    if query.data == "cancel":
        return await cancel(update, context)
    
    program = query.data.split(':')[1]
    get_report_data(context).program_name = program
    
    # Если выбрана N/A - это приватный тур, спрашиваем маршрут
    if program == "N/A":
        save_state(context, ReportStates.PRIVATE_PROGRAM)
        await query.edit_message_text(
            "✅ Program: *N/A (Private tour)*\n\n"
            "🏝 *Select private tour route:*",
            reply_markup=get_private_program_keyboard(),
            parse_mode='Markdown'
        )
        return ReportStates.PRIVATE_PROGRAM
    
    save_state(context, ReportStates.PIER)
    await query.edit_message_text(
        f"✅ Program: *{program}*\n\n"
        "⚓ *Select pier:*",
        reply_markup=get_pier_keyboard(),
        parse_mode='Markdown'
    )
    return ReportStates.PIER


async def private_program_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора маршрута приватного тура"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "back":
        return await handle_back(update, context)
    if query.data == "cancel":
        return await cancel(update, context)
    
    private_program = query.data.split(':')[1]
    get_report_data(context).private_program = private_program
    save_state(context, ReportStates.PIER)
    
    await query.edit_message_text(
        f"✅ Private tour: *{private_program}*\n\n"
        "⚓ *Select pier:*",
        reply_markup=get_pier_keyboard(),
        parse_mode='Markdown'
    )
    return ReportStates.PIER


async def pier_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора пирса"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "back":
        return await handle_back(update, context)
    if query.data == "cancel":
        return await cancel(update, context)
    
    pier = query.data.split(':')[1]
    get_report_data(context).departure_pier = pier
    save_state(context, ReportStates.DEPARTURE_DATE)
    
    await query.edit_message_text(
        f"✅ Pier: *{pier}*\n\n"
        "📅 *Departure date:*\n\n"
        "Enter date (DD.MM.YYYY) or select a date:",
        reply_markup=get_date_keyboard("departure"),
        parse_mode='Markdown'
    )
    return ReportStates.DEPARTURE_DATE


async def departure_date_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка даты отправления"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        if query.data == "back":
            return await handle_back(update, context)
        if query.data == "cancel":
            return await cancel(update, context)
        
        # Парсим дату из callback_data (формат: departure:2026-01-08)
        try:
            date_str = query.data.split(":")[1]
            departure = date.fromisoformat(date_str)
        except (IndexError, ValueError):
            return ReportStates.DEPARTURE_DATE
        
        get_report_data(context).departure_date = departure
        save_state(context, ReportStates.RETURN_DATE)
        
        await query.edit_message_text(
            f"✅ Departure: *{departure.strftime('%d.%m.%Y')}*\n\n"
            "📅 *Return date:*\n\n"
            "Enter date (DD.MM.YYYY) or select a date:",
            reply_markup=get_date_keyboard("return"),
            parse_mode='Markdown'
        )
    else:
        try:
            departure = parse_date(update.message.text)
            get_report_data(context).departure_date = departure
            save_state(context, ReportStates.RETURN_DATE)
            
            await update.message.reply_text(
                f"✅ Departure: *{departure.strftime('%d.%m.%Y')}*\n\n"
                "📅 *Return date:*\n\n"
                "Enter date (DD.MM.YYYY) or select a date:",
                reply_markup=get_date_keyboard("return"),
                parse_mode='Markdown'
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid date format. Use DD.MM.YYYY",
                reply_markup=get_date_keyboard("departure")
            )
            return ReportStates.DEPARTURE_DATE
    
    return ReportStates.RETURN_DATE


async def return_date_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка даты возвращения"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        if query.data == "back":
            return await handle_back(update, context)
        if query.data == "cancel":
            return await cancel(update, context)
        
        # Парсим дату из callback_data (формат: return:2026-01-08)
        try:
            date_str = query.data.split(":")[1]
            return_d = date.fromisoformat(date_str)
        except (IndexError, ValueError):
            return ReportStates.RETURN_DATE
        
        get_report_data(context).return_date = return_d
        save_state(context, ReportStates.REFILL_DATE)
        
        await query.edit_message_text(
            f"✅ Return: *{return_d.strftime('%d.%m.%Y')}*\n\n"
            "📅 *Refill date:*\n\n"
            "Enter date (DD.MM.YYYY) or select a date:",
            reply_markup=get_date_keyboard("refill"),
            parse_mode='Markdown'
        )
    else:
        try:
            return_d = parse_date(update.message.text)
            get_report_data(context).return_date = return_d
            save_state(context, ReportStates.REFILL_DATE)
            
            await update.message.reply_text(
                f"✅ Return: *{return_d.strftime('%d.%m.%Y')}*\n\n"
                "📅 *Refill date:*\n\n"
                "Enter date (DD.MM.YYYY) or select a date:",
                reply_markup=get_date_keyboard("refill"),
                parse_mode='Markdown'
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid date format. Use DD.MM.YYYY",
                reply_markup=get_date_keyboard("return")
            )
            return ReportStates.RETURN_DATE
    
    return ReportStates.REFILL_DATE


async def refill_date_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка даты заправки"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        if query.data == "back":
            return await handle_back(update, context)
        if query.data == "cancel":
            return await cancel(update, context)
        
        # Парсим дату из callback_data (формат: refill:2026-01-08)
        try:
            date_str = query.data.split(":")[1]
            refill = date.fromisoformat(date_str)
        except (IndexError, ValueError):
            return ReportStates.REFILL_DATE
        
        get_report_data(context).refill_date = refill
        save_state(context, ReportStates.MAX_SPEED)
        
        await query.edit_message_text(
            f"✅ Refill: *{refill.strftime('%d.%m.%Y')}*\n\n"
            "⚡ *Max speed:*\n\n"
            "Enter a number:",
            reply_markup=get_navigation_keyboard(),
            parse_mode='Markdown'
        )
    else:
        try:
            refill = parse_date(update.message.text)
            get_report_data(context).refill_date = refill
            save_state(context, ReportStates.MAX_SPEED)
            
            await update.message.reply_text(
                f"✅ Refill: *{refill.strftime('%d.%m.%Y')}*\n\n"
                "⚡ *Max speed:*\n\n"
                "Enter a number:",
                reply_markup=get_navigation_keyboard(),
                parse_mode='Markdown'
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid date format. Use DD.MM.YYYY",
                reply_markup=get_date_keyboard("refill")
            )
            return ReportStates.REFILL_DATE
    
    return ReportStates.MAX_SPEED


async def max_speed_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка ввода скорости"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        if query.data == "back":
            return await handle_back(update, context)
        if query.data == "cancel":
            return await cancel(update, context)
    
    try:
        speed = int(update.message.text.strip())
        get_report_data(context).max_speed = speed
        save_state(context, ReportStates.GASOLINE_REFUEL)
        
        await update.message.reply_text(
            f"✅ Speed: *{speed}*\n\n"
            "⛽ *Fuel refilled:*\n\n"
            "Enter liters:",
            reply_markup=get_navigation_keyboard(),
            parse_mode='Markdown'
        )
        return ReportStates.GASOLINE_REFUEL
    except ValueError:
        await update.message.reply_text(
            "❌ Enter a whole number",
            reply_markup=get_navigation_keyboard()
        )
        return ReportStates.MAX_SPEED


async def gasoline_refuel_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка ввода заправленного топлива"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        if query.data == "back":
            return await handle_back(update, context)
        if query.data == "cancel":
            return await cancel(update, context)
    
    try:
        refuel = float(update.message.text.strip().replace(',', '.'))
        get_report_data(context).gasoline_refuel = refuel
        save_state(context, ReportStates.TOTAL_GASOLINE)
        
        await update.message.reply_text(
            f"✅ Refueled: *{refuel}* L\n\n"
            "⛽ *Total fuel on boat:*\n\n"
            "Enter liters:",
            reply_markup=get_navigation_keyboard(),
            parse_mode='Markdown'
        )
        return ReportStates.TOTAL_GASOLINE
    except ValueError:
        await update.message.reply_text(
            "❌ Enter a number",
            reply_markup=get_navigation_keyboard()
        )
        return ReportStates.GASOLINE_REFUEL


async def total_gasoline_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка ввода общего топлива"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        if query.data == "back":
            return await handle_back(update, context)
        if query.data == "cancel":
            return await cancel(update, context)
    
    try:
        total = float(update.message.text.strip().replace(',', '.'))
        get_report_data(context).total_gasoline = total
        save_state(context, ReportStates.GASOLINE_USED)
        
        await update.message.reply_text(
            f"✅ Total: *{total}* L\n\n"
            "⛽ *Fuel used:*\n\n"
            "Enter liters:",
            reply_markup=get_navigation_keyboard(),
            parse_mode='Markdown'
        )
        return ReportStates.GASOLINE_USED
    except ValueError:
        await update.message.reply_text(
            "❌ Enter a number",
            reply_markup=get_navigation_keyboard()
        )
        return ReportStates.TOTAL_GASOLINE


async def gasoline_used_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка ввода использованного топлива"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        if query.data == "back":
            return await handle_back(update, context)
        if query.data == "cancel":
            return await cancel(update, context)
    
    try:
        used = float(update.message.text.strip().replace(',', '.'))
        report_data = get_report_data(context)
        report_data.gasoline_used = used
        
        # Автоматический расчёт остатка
        report_data.calculate_gasoline_left()
        save_state(context, ReportStates.MILEAGE)
        
        await update.message.reply_text(
            f"✅ Used: *{used}* L\n"
            f"📊 Remaining: *{report_data.gasoline_left}* L (calculated automatically)\n\n"
            "🛣 *Mileage (optional):*\n\n"
            "Enter mileage or press 'Skip':",
            reply_markup=get_skip_keyboard("mileage"),
            parse_mode='Markdown'
        )
        return ReportStates.MILEAGE
    except ValueError:
        await update.message.reply_text(
            "❌ Enter a number",
            reply_markup=get_navigation_keyboard()
        )
        return ReportStates.GASOLINE_USED


async def mileage_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка ввода пробега"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        if query.data == "back":
            return await handle_back(update, context)
        if query.data == "cancel":
            return await cancel(update, context)
        if "skip" in query.data:
            get_report_data(context).mileage_ride = None
            save_state(context, ReportStates.MILEAGE_PHOTO)
            
            await query.edit_message_text(
                "⏭ Mileage: *skipped*\n\n"
                "📷 *Odometer photo (optional):*\n\n"
                "Send photo or press 'No photo':",
                reply_markup=get_photo_keyboard("mileage_photo"),
                parse_mode='Markdown'
            )
            return ReportStates.MILEAGE_PHOTO
    
    try:
        mileage = float(update.message.text.strip().replace(',', '.'))
        get_report_data(context).mileage_ride = mileage
        save_state(context, ReportStates.MILEAGE_PHOTO)
        
        await update.message.reply_text(
            f"✅ Mileage: *{mileage}*\n\n"
            "📷 *Odometer photo (optional):*\n\n"
            "Send photo or press 'No photo':",
            reply_markup=get_photo_keyboard("mileage_photo"),
            parse_mode='Markdown'
        )
        return ReportStates.MILEAGE_PHOTO
    except ValueError:
        await update.message.reply_text(
            "❌ Enter a number or press 'Skip'",
            reply_markup=get_skip_keyboard("mileage")
        )
        return ReportStates.MILEAGE


async def mileage_photo_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка фото одометра"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        if query.data == "back":
            return await handle_back(update, context)
        if query.data == "cancel":
            return await cancel(update, context)
        if "skip" in query.data:
            get_report_data(context).mileage_photo_id = None
            save_state(context, ReportStates.BILL_PHOTO)
            
            await query.edit_message_text(
                "⏭ Odometer photo: *skipped*\n\n"
                "📷 *Receipt photo (optional):*\n\n"
                "Send photo or press 'No photo':",
                reply_markup=get_photo_keyboard("bill_photo"),
                parse_mode='Markdown'
            )
            return ReportStates.BILL_PHOTO
    
    if update.message and update.message.photo:
        photo = update.message.photo[-1]
        get_report_data(context).mileage_photo_id = photo.file_id
        save_state(context, ReportStates.BILL_PHOTO)
        
        await update.message.reply_text(
            "✅ Odometer photo: *uploaded*\n\n"
            "📷 *Receipt photo (optional):*\n\n"
            "Send photo or press 'No photo':",
            reply_markup=get_photo_keyboard("bill_photo"),
            parse_mode='Markdown'
        )
        return ReportStates.BILL_PHOTO
    
    await update.message.reply_text(
        "❌ Send photo or press 'No photo'",
        reply_markup=get_photo_keyboard("mileage_photo")
    )
    return ReportStates.MILEAGE_PHOTO


async def bill_photo_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка фото чека"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        if query.data == "back":
            return await handle_back(update, context)
        if query.data == "cancel":
            return await cancel(update, context)
        if "skip" in query.data:
            get_report_data(context).bill_photo_id = None
    elif update.message and update.message.photo:
        photo = update.message.photo[-1]
        get_report_data(context).bill_photo_id = photo.file_id
    else:
        await update.message.reply_text(
            "❌ Send photo or press 'No photo'",
            reply_markup=get_photo_keyboard("bill_photo")
        )
        return ReportStates.BILL_PHOTO
    
    # Показываем сводку
    report_data = get_report_data(context)
    summary = report_service.format_report_summary(report_data)
    
    save_state(context, ReportStates.CONFIRM)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            summary + "\n\n*Confirm submission?*",
            reply_markup=get_confirm_keyboard(),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            summary + "\n\n*Confirm submission?*",
            reply_markup=get_confirm_keyboard(),
            parse_mode='Markdown'
        )
    
    return ReportStates.CONFIRM


async def confirm_submission(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Подтверждение отправки отчёта"""
    query = update.callback_query
    await query.answer()
    
    action = query.data.split(':')[1]
    
    if action == "yes":
        try:
            report_data = get_report_data(context)
            await report_service.create_report(report_data)
            
            await query.edit_message_text(
                "✅ *Report saved successfully!*\n\n"
                "Thank you for filling out.",
                parse_mode='Markdown'
            )
            
            # Очищаем данные
            context.user_data.clear()
            
        except Exception as e:
            await query.edit_message_text(
                f"❌ *Save error:*\n{str(e)}",
                parse_mode='Markdown'
            )
        
        return ConversationHandler.END
    
    elif action == "no":
        return await cancel(update, context)
    
    elif action == "edit":
        # Возвращаемся к началу
        context.user_data['state_history'] = [ReportStates.CAPTAIN]
        
        await query.edit_message_text(
            "✏️ *Edit report*\n\n"
            "👨‍✈️ *Select captain:*",
            reply_markup=get_captain_keyboard(),
            parse_mode='Markdown'
        )
        return ReportStates.CAPTAIN
    
    return ReportStates.CONFIRM


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена заполнения"""
    context.user_data.clear()
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            "❌ *Filling cancelled*\n\n"
            "Use the menu to start a new report.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ *Filling cancelled*\n\n"
            "Use the menu to start a new report.",
            reply_markup=get_main_menu_keyboard(),
            parse_mode='Markdown'
        )
    
    return ConversationHandler.END


# ============== СОЗДАНИЕ CONVERSATION HANDLER ==============

def get_report_conversation_handler() -> ConversationHandler:
    """Создать ConversationHandler для заполнения отчёта"""
    
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex(r'^📝'), start_report),
            CommandHandler('report', start_report)
        ],
        states={
            ReportStates.CAPTAIN: [
                CallbackQueryHandler(captain_selected)
            ],
            ReportStates.BOAT: [
                CallbackQueryHandler(boat_selected)
            ],
            ReportStates.PROGRAM: [
                CallbackQueryHandler(program_selected)
            ],
            ReportStates.PRIVATE_PROGRAM: [
                CallbackQueryHandler(private_program_selected)
            ],
            ReportStates.PIER: [
                CallbackQueryHandler(pier_selected)
            ],
            ReportStates.DEPARTURE_DATE: [
                CallbackQueryHandler(departure_date_input),
                MessageHandler(filters.TEXT & ~filters.COMMAND, departure_date_input)
            ],
            ReportStates.RETURN_DATE: [
                CallbackQueryHandler(return_date_input),
                MessageHandler(filters.TEXT & ~filters.COMMAND, return_date_input)
            ],
            ReportStates.REFILL_DATE: [
                CallbackQueryHandler(refill_date_input),
                MessageHandler(filters.TEXT & ~filters.COMMAND, refill_date_input)
            ],
            ReportStates.MAX_SPEED: [
                CallbackQueryHandler(max_speed_input),
                MessageHandler(filters.TEXT & ~filters.COMMAND, max_speed_input)
            ],
            ReportStates.GASOLINE_REFUEL: [
                CallbackQueryHandler(gasoline_refuel_input),
                MessageHandler(filters.TEXT & ~filters.COMMAND, gasoline_refuel_input)
            ],
            ReportStates.TOTAL_GASOLINE: [
                CallbackQueryHandler(total_gasoline_input),
                MessageHandler(filters.TEXT & ~filters.COMMAND, total_gasoline_input)
            ],
            ReportStates.GASOLINE_USED: [
                CallbackQueryHandler(gasoline_used_input),
                MessageHandler(filters.TEXT & ~filters.COMMAND, gasoline_used_input)
            ],
            ReportStates.MILEAGE: [
                CallbackQueryHandler(mileage_input),
                MessageHandler(filters.TEXT & ~filters.COMMAND, mileage_input)
            ],
            ReportStates.MILEAGE_PHOTO: [
                CallbackQueryHandler(mileage_photo_input),
                MessageHandler(filters.PHOTO, mileage_photo_input)
            ],
            ReportStates.BILL_PHOTO: [
                CallbackQueryHandler(bill_photo_input),
                MessageHandler(filters.PHOTO, bill_photo_input)
            ],
            ReportStates.CONFIRM: [
                CallbackQueryHandler(confirm_submission)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('start', cancel)
        ],
        allow_reentry=True
    )
