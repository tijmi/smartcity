debug_settings = {
    "PROGRAM_STARTUP": True,
    "ERROR": True,
    "STEP_DECISION": True,
    "NO_FLAG": True,

    "EVENT_START": True,
    "EVENT_END": True,

    "HANDLER_DEBUG": True,
    "OUTPUT_DEBUG": True,
    "TILE_DATA_DEBUG": True,
    "PLAYER_DEBUG": True,
}


class Color:
    START = "\033[1;33m"
    END = "\033[1;36m"
    NO_FLAG = "\033[3;37m"
    RESET = "\033[0m"
    ERROR = "\033[31m"


def debug(msg, flag="NO_FLAG"):
    if debug_settings.get(flag):
        if flag == "EVENT_START":
            print(f"{Color.START}EVENT START{Color.RESET}")
            print(msg)
        elif flag == "EVENT_END":
            print(f"{Color.END}EVENT END{Color.RESET}")
            print(msg)
        elif flag == "NO_FLAG":
            print(f"{Color.NO_FLAG}{msg}{Color.RESET}")
        elif flag == "ERROR":
            print(f"{Color.ERROR}{msg}{Color.RESET}")
        else:
            print(msg)


