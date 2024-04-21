from collections import namedtuple


CommandResponse = namedtuple("CommandResponse", ["text", "kwargs", "markup"])
MessageResponse = namedtuple("MessageResponse", ["text", "image_url"])
