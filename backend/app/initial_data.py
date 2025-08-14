from loguru import logger

from app.core.db import init_db


def main() -> None:
    logger.info("创建初始化数据")
    init_db()
    logger.info("初始化数据已创建")


if __name__ == "__main__":
    main()
