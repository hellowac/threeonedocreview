import logging

from loguru import logger
from sqlalchemy import Engine, delete
from sqlmodel import Session, func, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.db import engine
from app.models.agentsetting import AgentSetting

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),   # type: ignore
    after=after_log(logger, logging.WARN),   # type: ignore
)
def init(db_engine: Engine) -> None:
    try:
        with Session(db_engine) as session:
            # Try to create session to check if DB is awake
            session.exec(select(1))
    except Exception as e:
        logger.error(e)
        raise e


def delete_agentsettings(engine: Engine) -> None:
    """ 删除 所有设置， 重新初始化 """

    # 初始化agent设置
    with Session(bind=engine) as session:
        count = session.exec(select(func.count()).select_from(AgentSetting)).one()

        if count:
            statement = delete(AgentSetting)

            result = session.exec(statement) # type: ignore
            session.commit()

            logger.info(f"删除{result.rowcount}条agent设置...")

    logger.info("初始化数据库数据 done")


def main() -> None:
    logger.info("Initializing service")
    init(engine)
    delete_agentsettings(engine)
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()


