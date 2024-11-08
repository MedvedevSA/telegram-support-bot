import json
import logging
import logging.config

def file_config(fname: str):
    with open(fname) as f:
        config = json.loads(f.read())
        logging.config.dictConfig(config)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
