class Person:
    def __init__(self, user_id, user_handle, first_name, last_name, is_group_admin, is_group_owner):
        self.user_id = user_id
        self.user_handle = user_handle
        self.first_name = first_name
        self.last_name = last_name
        self.is_group_admin = is_group_admin
        self.is_group_owner = is_group_owner


class Context:
    def __init__(self, chat_id, thread_id, is_group, is_bot_mentioned):
        self.chat_id = chat_id
        self.thread_id = thread_id
        self.is_group = is_group
        self.is_bot_mentioned = is_bot_mentioned


class Message:
    def __init__(self, message_text, in_file_image, in_file_audio):
        self.message_text = message_text
        self.in_file_image = in_file_image
        self.in_file_audio = in_file_audio


class TranscribedMessage:
    def __init__(self, message_text, image_description, voice_description):
        self.message_text = message_text
        self.image_description = image_description
        self.voice_description = voice_description
