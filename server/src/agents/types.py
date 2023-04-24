import time
import os
from .. import storage

import abc


import logging


class Agent(abc.ABC):
    def __init__(self, agent_id=None, repo_id=None):
        if agent_id is None:
            raise ("Agent ID must be provided")
        if repo_id is None:
            raise ("Repo ID must be provided")
        self.agent_id = agent_id
        self.repo_id = repo_id
        self.loop = True

        self.configure_logging()

    def configure_logging(self):
        log_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s')
        # make folder
        log_folder = storage.create_log_folder_for_agent(
            self.repo_id, self.agent_id)

        print("log_folder: ", log_folder)
        log_file = os.path.join(log_folder, "agent.log")
        # touch file if it doesn't exist
        if not os.path.exists(log_file):
            with open(log_file, "w"):
                pass

            # Configure the file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(log_formatter)

        # Configure the console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)

        # Configure the logger
        self.logger = logging.getLogger(f"agent_{self.agent_id}")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    # Factor out launch into start_loop and launch
    def start_loop(self):
        self.logger.info("Starting agent loop")
        while self.loop:
            self.logger.info("Getting next job")
            job = self.get_next_job()
            self.logger.info(f"Got job {job}")

            if job is not None:

                self.logger.info(f"Processing job {job}")
                new_jobs, new_files = self.process_job(job)
                self.logger.info(f"Processed job {job}")
                self.process_job_fn_result(job, new_jobs, new_files)
                self.logger.info(f"Processed job {job} result")
            else:
                self.logger.info("No jobs found, sleeping, 5 sec")
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
        self.logger.info("Updating agent results index")
        storage.update_repo_results_index(self.repo_id)

    def stop(self):
        self.loop = False

    def add_job(self, job):
        self.logger.info(f"Adding job {job}")
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
