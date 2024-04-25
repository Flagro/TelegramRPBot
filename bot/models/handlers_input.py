class Person:
    def __init__(self, user_id, username, first_name, last_name, language_code):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.language_code = language_code


class Context:
    def __init__(self, chat_id, thread_id, is_group):
        self.chat_id = chat_id
        self.thread_id = thread_id
        self.is_group = is_group


class Message:
    def __init__(self, message_text, in_file_image, in_file_audio):
        self.message_text = message_text
        self.in_file_image = in_file_image
        self.in_file_audio = in_file_audio
