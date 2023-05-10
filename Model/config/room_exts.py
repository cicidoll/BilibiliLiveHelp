from plugin.Files import JsonFile
from pathlib import Path

file_path: Path = Path.cwd() / "config" / "room.json"

class RoomConfig:

    def __init__(self) -> None:
        # 直播间号
        self.roomid: int = JsonFile.load_json(file_path)["roomid"]