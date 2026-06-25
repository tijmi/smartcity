debug_settings = {
    "HANDLER_DEBUG": True,
    "OUTPUT_DEBUG": True,
    "TILE_DATA_DEBUG": True,
    "EVENT_START": True,
    "STEP_DECISION": True,
    "NO_FLAG": False,
    "PROGRAM_STARTUP": True,
    "PLAYER_DEBUG": True
}


class Color:
    START = "\033[1;33m"
    END = "\033[1;36m"
    NO_FLAG = "\033[3;37m"
    RESET = "\033[0m"


def debug(msg, flag="NO_FLAG"):
    if debug_settings.get(flag):
        if flag == "EVENT_START":
            print(f"{Color.START}EVENT START{Color.RESET}")
            print(msg)
        elif flag == "OUTPUT_DEBUG":
            print(f"{Color.END}EVENT END{Color.RESET}")
            print(msg)
        elif flag == "NO_FLAG":
            print(f"{Color.NO_FLAG}{msg}{Color.RESET}")
        else:
            print(msg)


