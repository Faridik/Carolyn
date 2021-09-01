from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def build_menu_of_subjects(subjects: list) -> InlineKeyboardMarkup:
    button_list = []
    for subject in subjects:
        button_list.append(
            InlineKeyboardButton(subject, callback_data=f"subject#{subject}")
        )
    end_button = [InlineKeyboardButton("Отмена", callback_data="cancel#")]
    return InlineKeyboardMarkup(build_menu(button_list, n_cols=2, 
                                        footer_buttons=end_button))


def build_menu_of_assignments(
    assignments: dict, pressed_name: str = None, has_back_button: bool = False
) -> InlineKeyboardMarkup:
    button_list = []
    for assignment in assignments:
        if not assignment['allow_to_display']:
            continue
        if pressed_name and assignment["name"] == pressed_name:
            title = f'💁‍♀️ {assignment["name"]}'
        else:
            title = assignment["name"]
        button_list.append(
            InlineKeyboardButton(
                title,
                callback_data=f'assignment#{assignment["name"]}'
                + f'#{assignment["subject"]}',
            )
        )
    if has_back_button:
        button_list.append(
            InlineKeyboardButton("Назад", callback_data=f"assignment#$back$")
        )
    end_button = [InlineKeyboardButton("Отмена", callback_data="cancel#")]
    return InlineKeyboardMarkup(build_menu(button_list, n_cols=3, 
                                        footer_buttons=end_button))


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i : i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu
