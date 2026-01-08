"""
Inline keyboard generators for Telegram bot
"""
from datetime import date, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from services.dictionary_service import dictionary_service


def build_selection_keyboard(
    items: list[str], 
    callback_prefix: str, 
    columns: int = 2,
    add_back: bool = True
) -> InlineKeyboardMarkup:
    """
    Build inline keyboard for selection from list
    
    Args:
        items: list of items to select from
        callback_prefix: prefix for callback_data
        columns: number of columns
        add_back: add "Back" button
    """
    keyboard = []
    row = []
    
    for item in items:
        row.append(InlineKeyboardButton(
            text=item,
            callback_data=f"{callback_prefix}:{item}"
        ))
        
        if len(row) == columns:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    if add_back:
        keyboard.append([
            InlineKeyboardButton("⬅️ Back", callback_data="back"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ])
    
    return InlineKeyboardMarkup(keyboard)


def get_captain_keyboard() -> InlineKeyboardMarkup:
    """Captain selection keyboard"""
    return build_selection_keyboard(
        dictionary_service.captains, 
        "captain", 
        columns=2,
        add_back=False
    )


def get_boat_keyboard() -> InlineKeyboardMarkup:
    """Boat selection keyboard"""
    return build_selection_keyboard(
        dictionary_service.boats, 
        "boat", 
        columns=2
    )


def get_program_keyboard() -> InlineKeyboardMarkup:
    """Program selection keyboard"""
    return build_selection_keyboard(
        dictionary_service.programs, 
        "program", 
        columns=2
    )


def get_private_program_keyboard() -> InlineKeyboardMarkup:
    """Private tour route selection keyboard (without N/A)"""
    programs = [p for p in dictionary_service.programs if p != "N/A"]
    return build_selection_keyboard(
        programs, 
        "private_program", 
        columns=2
    )


def get_pier_keyboard() -> InlineKeyboardMarkup:
    """Pier selection keyboard"""
    return build_selection_keyboard(
        dictionary_service.piers, 
        "pier", 
        columns=3
    )


def get_date_keyboard(callback_prefix: str) -> InlineKeyboardMarkup:
    """Date selection keyboard: today ± 5 days"""
    today = date.today()
    keyboard = []
    
    # Generate dates from -5 to +5 days
    dates = [today + timedelta(days=i) for i in range(-5, 6)]
    
    # Split into rows of 3 buttons
    row = []
    for d in dates:
        day_str = d.strftime("%d.%m")
        
        # Highlight today
        if d == today:
            label = f"📅 {day_str}"
        else:
            label = day_str
        
        row.append(InlineKeyboardButton(
            text=label,
            callback_data=f"{callback_prefix}:{d.isoformat()}"
        ))
        
        if len(row) == 3:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    # Navigation
    keyboard.append([
        InlineKeyboardButton("⬅️ Back", callback_data="back"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    ])
    
    return InlineKeyboardMarkup(keyboard)


def get_skip_keyboard(callback_prefix: str) -> InlineKeyboardMarkup:
    """Keyboard with skip button (for optional fields)"""
    keyboard = [
        [InlineKeyboardButton("⏭ Skip", callback_data=f"{callback_prefix}:skip")],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="back"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_photo_keyboard(callback_prefix: str) -> InlineKeyboardMarkup:
    """Keyboard for photo upload (with skip option)"""
    keyboard = [
        [InlineKeyboardButton("⏭ No photo", callback_data=f"{callback_prefix}:skip")],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="back"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Submission confirmation keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Submit", callback_data="confirm:yes"),
            InlineKeyboardButton("❌ Cancel", callback_data="confirm:no")
        ],
        [InlineKeyboardButton("✏️ Edit", callback_data="confirm:edit")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_navigation_keyboard() -> InlineKeyboardMarkup:
    """Basic navigation keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("⬅️ Back", callback_data="back"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Main menu (reply keyboard)"""
    keyboard = [
        [KeyboardButton("📝 New Report")],
        [KeyboardButton("📊 Analytics"), KeyboardButton("📋 History")],
        [KeyboardButton("ℹ️ Help")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
