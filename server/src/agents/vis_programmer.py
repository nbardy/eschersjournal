import os
import json
import time
import openai
import subprocess
from queue import Queue
import os
import json
import time

from agents.types import Agent


class VisProgrammerAgent(Agent):
    def __init__(self):
        self.preliminary_results_path = "Escher"
        self.final_results_path = "FinalResults"

        # Create directories if they don't exist
        os.makedirs(self.preliminary_results_path, exist_ok=True)
        os.makedirs(self.final_results_path, exist_ok=True)

    def save_visualization(self, code, summary, image, is_final):
        timestamp = int(time.time())

        # Choose the appropriate directory
        target_dir = self.final_results_path if is_final else self.preliminary_results_path

        # Save code files
        with open(f"{target_dir}/{timestamp}_code.html", "w") as f:
            f.write(code["html"])

        with open(f"{target_dir}/{timestamp}_code.js", "w") as f:
            f.write(code["js"])

        with open(f"{target_dir}/{timestamp}_code.css", "w") as f:
            f.write(code["css"])

        # Save summary file
        with open(f"{target_dir}/{timestamp}_summary.json", "w") as f:
            json.dump(summary, f)

        # Save image file
        with open(f"{target_dir}/{timestamp}_image.png", "wb") as f:
            f.write(image)

        # Update the index file
        self.update_index_file(target_dir, timestamp, summary)

    # ...

    def launch(self):
        vis_requests = Queue()

        # Populate the vis_requests queue with example requests
        # Replace this with your actual method of receiving requests
        vis_requests.put({"topic": "Sample Visualization",
                         "type": "bar_chart", "data": [1, 2, 3]})

        while not vis_requests.empty():
            vis_request = vis_requests.get()
            self.process_vis_request(vis_request)

    def process_vis_request(self, vis_request):
        openai.api_key = "your_openai_api_key"

        prompt = f"Create a three.js program that draws a mathematical scene related to {vis_request['topic']} on a canvas."
        code = self.generate_code_with_openai(prompt)

        error = self.execute_code(code)

        while error:
            prompt = f"The following error occurred while executing the code: {error}. Please provide an updated version of the code."
            code = self.generate_code_with_openai(prompt)
            error = self.execute_code(code)

        # Save the visualization when error-free
        # ...

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
