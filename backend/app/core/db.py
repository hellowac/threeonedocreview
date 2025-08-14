from loguru import logger
from sqlmodel import Session, create_engine, func, select

from app.core.config import settings
from app.core.dbsettings import agent_settings_local, agent_settings_test
from app.models.agentsetting import AgentSetting

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28

# 在初始化数据库之前，请确保已导入所有 SQLModel 模型 （app.models），
# 否则，SQLModel 可能无法正确初始化关系，
# 了解更多详细信息：https://github.com/fastapi/full-stack-fastapi-template/issues/28

def init_db() -> None:
    """ 初始化数据库 """

    logger.info("初始化数据库数据...")

    # 初始化agent设置
    with Session(bind=engine) as session:
        count = session.exec(select(func.count()).select_from(AgentSetting)).one()

        if not count:
            if settings.ENVIRONMENT == 'local':
                session.add_all(agent_settings_local)
            elif settings.ENVIRONMENT == 'test':
                session.add_all(agent_settings_test)
            else:
                session.add_all(agent_settings_test)
            session.commit()
            logger.info("初始化agent设置成功....")

    logger.info("初始化数据库数据 done")
