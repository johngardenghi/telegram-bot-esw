from pathlib import Path
import json
import os
from threading import Lock

class ConfigManager:
    project_dir = Path(__file__).resolve().parent.parent
    config_file = project_dir / "config.json"
    _lock = Lock()

    @classmethod
    def _load_config(cls) -> dict:
        if not cls.config_file.exists():
            return {}

        with cls.config_file.open("r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def _save_config(cls, data: dict) -> None:
        cls.config_file.parent.mkdir(parents=True, exist_ok=True)

        tmp_file = cls.config_file.with_suffix(".tmp")

        with tmp_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        tmp_file.replace(cls.config_file)

    @classmethod
    def get_raio(cls) -> int:
        with cls._lock:
            data = cls._load_config()
            return int(data.get("raio", os.getenv("ESWBOT_RAIO", 4)))

    @classmethod
    def set_raio(cls, novo_raio: int) -> None:
        novo_raio = int(novo_raio)

        if novo_raio <= 0:
            raise ValueError("O raio precisa ser maior que zero.")

        with cls._lock:
            data = cls._load_config()
            data["raio"] = novo_raio
            cls._save_config(data)
