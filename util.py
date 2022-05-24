from platform import uname


def in_wsl() -> bool:
    return "microsoft-standard" in uname().release


def convert_wsl_to_windows_path(path: str) -> str:
    return path.replace("/mnt/c/", "C:\\")
