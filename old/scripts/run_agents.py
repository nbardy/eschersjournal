from agents.researcher import ResearcherAgent
from agents.vis_programmer import VisProgrammerAgent
from agents.vis_critic_agent import VisualizationCriticAgent

# Holds count and max api calls
config = {
    "researcher": {
        "count": 2,
        "max_api_calls": 200,
    },
    "vis_programmer": {
        "count": 5,
        "max_api_calls": 200,
    },
    "vis_critic": {
        "count": 2,
        "max_api_calls": 200,
    },
}

# Create all agents
agents = []
for agent_type, agent_config in config.items():
    for i in range(agent_config["count"]):
        if agent_type == "researcher":
            agents.append(ResearcherAgent(
                agent_type, i, agent_config["max_api_calls"]))
        elif agent_type == "vis_programmer":
            agents.append(VisProgrammerAgent(
                agent_type, i, agent_config["max_api_calls"]))
        elif agent_type == "vis_critic":
            agents.append(VisualizationCriticAgent(
                agent_type, i, agent_config["max_api_calls"]))
