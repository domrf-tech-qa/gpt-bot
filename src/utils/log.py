import logging
import yaml

with open("config.yaml", "r", encoding="utf8") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


def logger():
    logging.basicConfig(filename=config['log_path'], level=logging.INFO)
    logger = logging.getLogger()
    return logger
