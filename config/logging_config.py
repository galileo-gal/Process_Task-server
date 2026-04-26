# config/logging_config.py
import logging
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler
import os


def setup_logging(experiment_id=None):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    log_file = f"{log_dir}/experiment_{experiment_id}.log" if experiment_id else f"{log_dir}/app.log"

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers = []

    handler = RotatingFileHandler(log_file, maxBytes=50 * 1024 * 1024, backupCount=5)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        timestamp=True
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger