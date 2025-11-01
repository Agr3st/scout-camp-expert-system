import logging
import os
from src.utils.config import load_config, get_project_root


def setup_logger() -> logging.Logger:
    config = load_config()
    log_settings = config.get("logging", {})

    log_level = log_settings.get("level", "INFO").upper()
    log_file = log_settings.get("file", "logs/app.log")

    project_root = get_project_root()
    log_path = os.path.join(project_root, log_file)

    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logger = logging.getLogger("ScoutCampLogger")

    if not logger.handlers:
        logger.setLevel(log_level)

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
