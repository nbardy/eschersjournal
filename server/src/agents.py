import abc
import time
import storage
import pickle
import uuid
import subprocess

import os


class AllAgentsStore():
    def __init__(self, file_path='agents_store.pkl'):
        self.agents = {}
        self.file_path = file_path

        if os.path.exists(self.file_path):
            self.load_agents()

    def add_agent(self, repo_id: str, agent_id: str):
        if repo_id not in self.agents:
            self.agents[repo_id] = {}
        self.agents[repo_id][agent_id] = {}
        self.save_agents()

    def get_agents(self, repo_id: str):
        if repo_id not in self.agents:
            return {}
        return self.agents[repo_id]

    def save_agents(self):
        with open(self.file_path, 'wb') as file:
            pickle.dump(self.agents, file)

    def load_agents(self):
        with open(self.file_path, 'rb') as file:
            self.agents = pickle.load(file)


all_agents_store = AllAgentsStore()

agent_executors = {
    "vis_critic_agent": "python3 -m agents.vis_critic_agent",
    "research_agent": "python3 -m agents.research_agent",
    "vis_programmer": "python3 -m agents.vis_programmer",
}


all_types = list(agent_executors.keys())


def spawn_agent(repo_id: str, agent_type: str):
    # spawn a subprocess for each agent
    # each new agents gets a new uuid
    # and creats a dir to track results
    # and a file to stream logs

    # add the agent to the store
    agent_id = str(uuid.uuid4())

    all_agents_store.add_agent(repo_id, agent_id)

    # spawn the agent
    cmd = agent_executors[agent_type]
    cmd = cmd + " --repo_id " + repo_id + " --agent_id " + agent_id

    # run subprocess
    subprocess.Popen(cmd, shell=True)

    # return the agent id
    return (repo_id, agent_id)


def spawn_agents(repo_id: str, types: list):
    for type in types:
        spawn_agent(repo_id, type)


def get_agents(repo_id: str):
    return all_agents_store.get_agents(repo_id)
