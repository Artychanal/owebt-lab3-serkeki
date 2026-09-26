from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.texts import (
    AI_BUTTON,
    CONTACTS_BUTTON,
    STUDENT_BUTTON,
    TECHNOLOGIES_BUTTON,
)


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=STUDENT_BUTTON),
                KeyboardButton(text=TECHNOLOGIES_BUTTON),
            ],
            [
                KeyboardButton(text=CONTACTS_BUTTON),
                KeyboardButton(text=AI_BUTTON),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Оберіть пункт меню",
    )

