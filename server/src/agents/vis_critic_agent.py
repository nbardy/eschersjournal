from .. import storage

import uuid
import openai
from transformers import pipeline
from transformers import Blip2Processor, Blip2Model
import torch
from PIL import Image
import requests
from transformers import Blip2Processor, Blip2Model
import torch
from .types import Agent


from typing import Dict
from dataclasses import dataclass

# VisualizationContext


@dataclass
class VisualizationContext:
    visualization_goal: str
    equations: Dict[str, str]
    data: str
    context_data: str


class VisualizationCriticAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.blip_pipeline = blip_pipeline()

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
            print("Error in VisualizationCriticAgent: Unknown job type")
            raise Exception(f"Unknown job type: {job_type}")

    ##
    # Helpers Below
    #
    def read_visualization(self, image_path, program, vis_goal):
        # Step 3: Use Hugging Face's blip model to read the image with 9-10 questions
        questions = self.generate_questions()
        blip_results = self.ask_blip_questions(image_path, questions)

        # Step 4: Pass the results, questions, and the program to OpenAI along with the visualization goal
        openai_results = self.pass_to_openai(
            blip_results, questions, program, vis_goal)

        # Step 5: Ask OpenAI if the visualization is correct and what size the error is
        action = self.decide_action(openai_results)

        return action

    def generate_questions(self):
        # Generate 9-10 questions for the visualization using the Chat API
        openai.api_key = "your_openai_api_key"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Generate 10 questions to critique a visualization related to a mathematical scene:"}
            ]
        )

        questions = response.choices[0].text.strip().split("\n")
        return questions

    def pass_to_openai(self, blip_results, questions, program, vis_goal):
        openai.api_key = "your_openai_api_key"

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",
                "content": f"Blip model results: {blip_results}\nQuestions: {questions}\nProgram: {program}\nVisualization goal: {vis_goal}\nEvaluate the visualization and decide if it is correct or needs improvement. If it needs improvement, please suggest the size of the error and the action required (elaborate, fix, or leave alone):"}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        openai_results = response.choices[0].text.strip()
        return openai_results

    def ask_blip_questions(self, image_path, questions):
        # Implement this method to ask the blip model questions about the visualization
        results = []
        for question in questions:
            answer = self.blip_pipeline(
                {"image_path": image_path, "question": question})
            results.append(answer)
        return results


def main(agent_id=None, repo_id=None):
    if agent_id is None:
        agent_id = str(uuid.uuid4())
    if repo_id is None:
        repo_id = str(uuid.uuid4())

    agent = VisualizationCriticAgent(agent_id=agent_id, repo_id=repo_id)
    agent.launch()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_id", type=str, default=None)
    parser.add_argument("--repo_id", type=str, default=None)
