import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Установка пути для логов
log_directory = Path(str(os.getenv("LOG_FILES_DIR")))
log_directory.mkdir(exist_ok=True)  # Создаём директорию, если её нет
log_file = log_directory / "moneyscope.log"

# Создаём логгер
logger = logging.getLogger("main_logger")
logger.propagate = False  # Отключаем передачу логов родительским логгерам

# Проверяем, добавлены ли уже обработчики
if not any(isinstance(handler, RotatingFileHandler) for handler in logger.handlers):
    rotating_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=5)

    # Настройка уровня логирования и форматирования
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - [%(module)s:%(funcName)s] - %(message)s")

    rotating_handler.setFormatter(formatter)

    # Добавляем только rotating handler
    logger.setLevel(logging.INFO)
    logger.addHandler(rotating_handler)
