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

    # run subprocess
    subprocess.Popen(cmd, shell=True)

    # return the agent id
    return (repo_id, agent_id)


def spawn_agents(repo_id: str, types: list):
    for type in types:
        spawn_agent(repo_id, type)


def get_agents(repo_id: str):
    return all_agents_store.get_agents(repo_id)


class Agent(abc.ABC):
    def __init__(self, agent_id=None, repo_id=None):
        self.agent_id = agent_id
        self.repo_id = repo_id
        self.loop = True

    # Factor out launch into start_loop and launch
    def start_loop(self):
        while self.loop:
            job = self.get_next_job()

            if job is not None:
                new_jobs, new_files = self.process_job(job)
                self.process_job_fn_result(job, new_jobs, new_files)
            else:
                time.sleep(5)

    def launch(self):
        self.start_loop()

    def process_job_fn_result(self, job_id, new_jobs, new_files):
        # Saving and uploading new files
        for file_name, content in new_files.items():
            storage.save_and_upload_agent_result(
                self.id, job_id, content, file_name)

        # Queueing new jobs
        for job in new_jobs:
            self.add_job(job)

        # Update the agent results index
        storage.update_repo_results_index(self.repo_id, job.id)

    def stop(self):
        self.loop = False

    def add_job(self, job):
        storage.save_pending_job(self.repo_id, job)

    # get next job gets the jobs form storage and then lets the agent decide
    # which job to process next
    def get_next_job(self):
        jobs = storage.get_pending_jobs(self.repo_id)
        return self.decide_next_job(jobs)

    # abstract methods

    @abc.abstractmethod
    def decide_next_job(self):
        # Implement your job retrieval logic here
        pass

    @abc.abstractmethod
    def process_job(self, job):
        # Implement your job processing logic here
        pass
