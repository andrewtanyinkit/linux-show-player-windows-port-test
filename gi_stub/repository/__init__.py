import types as _types


def _stub(name):
    m = _types.ModuleType(name)
    return m


class _Meta(type):
    def __getattr__(cls, item):
        return None


class _Stub(metaclass=_Meta):
    pass


class GLib(_Stub):
    MAXINT64 = 2 ** 63 - 1

    class MainLoop:
        def run(self):
            pass

        def quit(self):
            pass


class GObject(_Stub):
    pass


class Gio(_Stub):
    pass


class GModule(_Stub):
    pass


class Gst(_Stub):
    STATE_NULL = 1
    STATE_READY = 2
    STATE_PAUSED = 3
    STATE_PLAYING = 4
    FORMAT_TIME = 3
    FORMAT_BYTES = 2
    SEEK_FLAG_FLUSH = 1
    SEEK_FLAG_ACCURATE = 2
    SEEK_TYPE_SET = 1
    CLOCK_TIME_NONE = 2 ** 64 - 1

    class MessageType:
        ERROR = 0
        EOS = 1
        STATE_CHANGED = 2
        DURATION_CHANGED = 3
        ASYNC_DONE = 4

    class PadDirection:
        SRC = 0
        SINK = 1

    class PadPresence:
        ALWAYS = 0
        SOMETIMES = 1

    class TagMergeMode:
        REPLACE_ALL = 0

    @staticmethod
    def init(args):
        pass

    @staticmethod
    def parse_launch(s):
        return None

    @staticmethod
    def version_string():
        return "stub"


class GstController(_Stub):
    pass


class GstPbutils(_Stub):
    class Discoverer:
        def __init__(self, *a):
            pass


class GstApp(_Stub):
    pass


class GstBase(_Stub):
    pass


class GstAudio(_Stub):
    pass


class GstVideo(_Stub):
    pass


class GstTag(_Stub):
    pass
