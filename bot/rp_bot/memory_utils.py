from ..models.handlers_input import Context, Person


def get_participant_key(person: Person) -> str:
    return f"telegram:{person.telegram_id}"


def get_display_name(person: Person) -> str:
    if person.user_handle:
        return person.user_handle
    full_name = " ".join(
        [name for name in [person.first_name, person.last_name] if name]
    ).strip()
    return full_name or get_participant_key(person)


def get_thread_key(context: Context) -> str:
    return str(context.thread_id) if context.thread_id is not None else "main"


def build_scope_key(
    context: Context,
    mode_id: str = "default",
) -> str:
    return f"chat:{context.chat_id}:thread:{get_thread_key(context)}:mode:{mode_id}"
