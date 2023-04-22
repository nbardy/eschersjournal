import openai
from transformers import pipeline
from transformers import Blip2Processor, Blip2Model
import torch
from PIL import Image
import requests
from transformers import Blip2Processor, Blip2Model
import torch

# VisualizationContext
#
# {
#   "visualization_goal": <string>,
#   // in latex
#   "equations": {
#     "eq1": <string>,
#     "eq2": <string>,
#   },
#   "data": <string>,
#   "context_data": <string>,
# }
# python type using lib
import dataclasses
from typing import List, Optional, Union, Dict, Any
from dataclasses import dataclass

# VisualizationContext


@dataclass
class VisualizationContext:
    visualization_goal: str
    equations: Dict[str, str]
    data: str
    context_data: str


def blip_pipeline():
    device = "cuda" if torch.cuda.is_available() else "cpu"

    processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
    model = Blip2Model.from_pretrained(
        "Salesforce/blip2-opt-2.7b", torch_dtype=torch.float16)
    model.to(device)

    return processor, model


class VisualizationCriticAgent:
    def __init__(self):
        self.blip_pipeline = blip_pipeline()

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

    def generate_questions(self, context: Context):
        # Implement this method to generate 9-10 questions for the visualization
        # ...
        return ["Sample question 1", "Sample question 2", "Sample question 3"]

    def ask_blip_questions(self, image_path, questions):
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"

        processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
        model = Blip2Model.from_pretrained(
            "Salesforce/blip2-opt-2.7b", torch_dtype=torch.float16)
        model.to(device)
        image = Image.open(image_path)

        prompt = "Question: how many cats are there? Answer:"
        inputs = processor(images=image, text=prompt,
                           return_tensors="pt").to(device, torch.float16)

        outputs = model(**inputs)
        # Implement this method to ask the blip model questions about the visualization
        results = []
        for question in questions:
            answer = self.blip_pipeline(
                {"image_path": image_path, "question": question})
            results.append(answer)
        return results

    def pass_to_openai(self, blip_results, questions, program, vis_goal):
        # Implement this method to pass the results, questions, and the program to OpenAI along with the visualization goal
        # ...
        return "Sample OpenAI results"

    def decide_action(self, openai_results):
        # Implement this method to decide the action (elaborate, fix, or leave alone) based on OpenAI's response
        # ...
        return "leave alone"
