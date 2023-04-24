
from .. import storage
import uuid
import os
import json
import time
import openai
import subprocess
from .types import Agent

max_runs = 10


class VisProgrammerAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.preliminary_results_path = "Escher"
        self.final_results_path = "FinalResults"

    ##
    # Abstract implementations below
    ##
    def decide_next_job(self, jobs):
        if len(jobs) > 0:
            return jobs[0]
        else:
            return None

    def process_job(self, job_id):
        # Download the job_id
        job_json = storage.get_pending_job(job_id)
        job_type = job_json["type"]
        if job_type == "vis_request":
            new_jobs, new_files = self.gen_vis(job_json)
        else:
            print("Error in VisProgrammerAgent: Unknown job type")
            raise Exception(f"Unknown job type: {job_type}")

    ##
    # Helpers Below
    #
    def save_visualization(self, code, summary, image, job_id):
        new_files = {
            f"{self.id}_code.html": code["html"],
            f"{self.id}_code.js": code["js"],
            f"{self.id}_code.css": code["css"],
            f"{self.id}_summary.json": json.dumps(summary),
            f"{self.id}_image.png": image
        }

        for file_name, content in new_files.items():
            storage.save_and_upload_agent_result(
                self.repo_id, self.agent_id, job_id, content, file_name)

    def gen_vis(self, job_json):
        file = self.job_fn(job_json, f"{self.id}_image.png")

        new_jobs = []
        new_files = [file]

        return new_jobs, new_files

    def job_fn(self, job, ):
        job_id = job.job_id
        vis_request = job["vis_request"]

        openai.api_key = "your_openai_api_key"

        # Temp filename png file
        id = str(uuid.uuid4())
        png_file = f"output-{id}.png"

        filename = png_file

        prompt = f"""Create a three.js program that draws a mathematical scene related to topic {vis_request['topic']} , and goal: {vis_request['goal']} canvas it should then save that canvas in {filename}.
                  JS Code: """
        error = self.execute_code(code)

        code = self.generate_code_with_openai(prompt)

        runs = 0
        while error and runs < max_runs:
            runs = runs + 1
            prompt = f"The following error occurred while executing the code.\nError: {error}\nCode:{code}. Please provide an updated version of the code. Updated Code:"
            code = self.generate_code_with_openai(prompt)
            error = self.execute_code(code)

        # Save the visualization when error-free
        summary = {"topic": vis_request["topic"], "type": vis_request["type"]}
        self.save_visualization(code, summary, png_file, job_id)

        return png_file

    def generate_code_with_openai(self, prompt):
        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5,
        )

        code = response.choices[0].text.strip()
        return code

    def execute_code(self, code):
        with open("temp_code.js", "w") as f:
            f.write(code)

        try:
            result = subprocess.run(
                ["node", "temp_code.js"], check=True, capture_output=True)
            return None
        except subprocess.CalledProcessError as e:
            return e.stderr.decode("utf-8").strip()


def main(agent_id=None, repo_id=None):
    if agent_id is None:
        agent_id = str(uuid.uuid4())
    if repo_id is None:
        repo_id = str(uuid.uuid4())

    agent = VisProgrammerAgent(agent_id=agent_id, repo_id=repo_id)
    agent.launch()


if __name__ == "__main__":
    # argparse first argument is repo id
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_id", type=str, default=None)
    parser.add_argument("--repo_id", type=str, default=None)
    args = parser.parse_args()

    main(args.agent_id, args.repo_id)
