from app.models.agentsetting import AgentSetting
from app.models.enums import AgentType, ForSection

agent_types = (
    AgentType.transmission,
    AgentType.substation,
    AgentType.distribute,
    # AgentType.assistant,
)

agent_type_names = (
    "输电",
    "变电",
    "配电",  # '智能助手'
)

agent_review_sections = (
    ForSection.one,
    ForSection.two,
    ForSection.three,
    ForSection.four,
    ForSection.five,
    ForSection.six,
    ForSection.sevenone,
    ForSection.seventwo,
    ForSection.seventhree,
    ForSection.sevenfour,
    ForSection.eight,
    ForSection.nine,
    ForSection.ten,
    # ForSection.assistant,
)

agent_review_section_names = (
    "第一节",
    "第二节",
    "第三节",
    "第四节",
    "第五节",
    "第六节",
    "第七节(一)",
    "第七节(二)",
    "第七节(三)",
    "第七节(四)",
    "第八节",
    "第九节",
    "第十节",
)

# 本地通用配置
agent_setting_local_config = {
    "protocol": "http",
    "host": "localhost",
    "port": 8002,
    "app_key": "jm77cyhyp4isp095skx85q1mcjs0rsf6",
    "agent_code": "agent1",
    "agent_version": "agent_verion1",
}

agent_settings_local = []

for agent_type_index, agent_type in enumerate(agent_types):
    agent_type_name = agent_type_names[agent_type_index]
    for agent_section_index, agent_section in enumerate(agent_review_sections):
        section_name = agent_review_section_names[agent_section_index]
        agent_settings_local.append(
            AgentSetting(
                protocol=agent_setting_local_config["protocol"],
                host=agent_setting_local_config["host"],
                port=agent_setting_local_config["port"],
                app_key=agent_setting_local_config["app_key"],
                agent_code=agent_setting_local_config["agent_code"],
                agent_version=agent_setting_local_config["agent_version"],
                session_id=None,
                agent_type=agent_type,
                section=agent_section,
                desc=f"用于审查【{agent_type_name}】专业的{section_name}的智能体",
            )
        )

# 添加智能助手
agent_settings_local.append(
    AgentSetting(
        protocol=agent_setting_local_config["protocol"],
        host=agent_setting_local_config["host"],
        port=agent_setting_local_config["port"],
        app_key=agent_setting_local_config["app_key"],
        agent_code=agent_setting_local_config["agent_code"],
        agent_version=agent_setting_local_config["agent_version"],
        session_id=None,
        agent_type=AgentType.assistant,
        section=ForSection.assistant,
        desc="用于智能助手页面的对话式聊天",
    )
)

# ----------- 测试/内网环境的 初始化配置 -------------------

# 测试通用配置
agent_setting_test_config = {
    "protocol": "http",
    "host": "25.78.182.238",
    "port": 80,
    "app_key": "vnTq9SjIFMAMnYgd4rldzBz5xnJYpBnZ",
    "agent_code": "a1f0234d-5b84-4bec-9696-8fa9f5785047",
    "agent_version": "1752023293754",
}

agent_settings_test = []

for agent_type_index, agent_type in enumerate(agent_types):
    agent_type_name = agent_type_names[agent_type_index]
    for agent_section_index, agent_section in enumerate(agent_review_sections):
        section_name = agent_review_section_names[agent_section_index]
        agent_settings_test.append(
            AgentSetting(
                protocol=agent_setting_test_config["protocol"],
                host=agent_setting_test_config["host"],
                port=agent_setting_test_config["port"],
                app_key=agent_setting_test_config["app_key"],
                agent_code=agent_setting_test_config["agent_code"],
                agent_version=agent_setting_test_config["agent_version"],
                session_id=None,
                agent_type=agent_type,
                section=agent_section,
                desc=f"用于审查【{agent_type_name}】专业的{section_name}的智能体",
            )
        )

# 添加智能助手
agent_settings_test.append(
    AgentSetting(
        protocol=agent_setting_test_config["protocol"],
        host=agent_setting_test_config["host"],
        port=agent_setting_test_config["port"],
        app_key="vnTq9SjlFMAMnYgd4rldzBz5xnJYpBnZ",  # app key
        agent_code="a1f0234d-5b84-4bec-9696-8fa9f5785047",  # 智能体编码
        agent_version="1752023293754",  # 智能体版本
        session_id=None,
        agent_type=AgentType.assistant,
        section=ForSection.assistant,
        desc="用于智能助手页面的对话式聊天",
    )
)
