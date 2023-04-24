
import re
import os
import json
import time
import openai
from queue import Queue
import sympy
from googlesearch import search
import wikipediaapi
import wolframalpha


class ResearcherAgent:
    def __init__(self):
        self.preliminary_results_path = "Escher"
        self.final_results_path = "FinalResults"

        # Create directories if they don't exist
        os.makedirs(self.preliminary_results_path, exist_ok=True)
        os.makedirs(self.final_results_path, exist_ok=True)

    def save_research_artifact(self, artifact_type, content, is_final):
        timestamp = int(time.time())

        # Choose the appropriate directory
        target_dir = self.final_results_path if is_final else self.preliminary_results_path

        # Save the artifact file
        if artifact_type == "notes":
            with open(f"{target_dir}/{timestamp}_notes.txt", "w") as f:
                f.write(content)
        else:
            with open(f"{target_dir}/{timestamp}_{artifact_type}.json", "w") as f:
                json.dump(content, f)

        # Update the index file
        self.update_index_file(target_dir, timestamp, {"type": artifact_type})

    def update_index_file(self, target_dir, timestamp, metadata):
        index_file_path = f"{target_dir}/index.json"

        # Load or create the index file content
        if os.path.exists(index_file_path):
            with open(index_file_path, "r") as f:
                index_content = json.load(f)
        else:
            index_content = []

        # Add the new entry
        index_content.append({"timestamp": timestamp, **metadata})

        # Save the updated index file
        with open(index_file_path, "w") as f:
            json.dump(index_content, f)

    def launch(self):
        research_requests = Queue()

        # Populate the research_requests queue with example requests
        # Replace this with your actual method of receiving requests
        research_requests.put(
            {"type": "more_information", "topic": "Einstein's theory of relativity"})
        research_requests.put(
            {"type": "clarity", "topic": "Quantum mechanics"})

        while not research_requests.empty():
            research_request = research_requests.get()
            self.process_research_request(research_request)

        # Idle behavior
        self.idle_behavior()

    def process_research_request(self, research_request):
        openai.api_key = "your_openai_api_key"

        if research_request["type"] == "more_information":
            prompt = f"Provide more information about {research_request['topic']}."
        elif research_request["type"] == "clarity":
            prompt = f"Explain {research_request['topic']} in a clear and simple way."
        elif research_request["type"] == "latex_to_python":
            result = self.latex_to_python_and_execute(
                research_request["latex_code"])
            self.save_research_artifact("result", result, is_final=True)
            return
        elif research_request["type"] == "search_web":
            result = self.search_web(research_request["query"])
            self.save_research_artifact(
                "search_results", result, is_final=True)
            return
        elif research_request["type"] == "search_wikipedia":
            result = self.search_wikipedia(research_request["query"])
            self.save_research_artifact(
                "wikipedia_summary", result, is_final=True)
            return
        elif research_request["type"] == "search_wolfram_alpha":
            result = self.search_wolfram_alpha(research_request["query"])
            self.save_research_artifact(
                "wolfram_result", result, is_final=True)
            return
        elif research_request["type"] == "get_notes":
            summary_and_key_points, embeddings, followup_questions = self.get_notes(
                research_request["topic"])
            self.save_research_artifact(
                "summary_and_key_points", summary_and_key_points, is_final=True)
            self.save_research_artifact(
                "embeddings", embeddings, is_final=True)
            self.save_research_artifact(
                "followup_questions", followup_questions, is_final=True)
            return

        response_text = self.generate_response_with_openai(prompt)

        # Save the response as a research artifact
        artifact_type = "notes" if research_request["type"] == "more_information" else "key_points"
        self.save_research_artifact(
            artifact_type, response_text, is_final=True)

    def generate_response_with_openai(self, prompt):
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5,
        )

        response_text = response.choices[0].text.strip()
        return response_text

    # Should summarize the current research ask for future direction and add
    # two new followup jobs to further explore
    def on_idle(self):
        # TODO
        pass

    def latex_to_python_and_execute(self, latex_code):
        python_code = sympy.sympify(latex_code)
        result = python_code.evalf()
        return result

    def search_web(self, query, num_results=10):
        search_results = search(query, num_results=num_results)
        return search_results

    def search_wikipedia(self, query, language='en'):
        wiki = wikipediaapi.Wikipedia(language)
        page = wiki.page(query)
        if not page.exists():
            return None

        summary = page.summary
        return summary

    def search_wolfram_alpha(self, query, app_id='your_app_id'):
        client = wolframalpha.Client(app_id)
        res = client.query(query)
        result = next(res.results).text
        return result

    def get_notes(self, topic):
        # Step 2: Ask the LLM to generate the best 3 queries for each platform
        query_prompt = f"Generate 3 different queries each for Wikipedia, Wolfram Alpha, and Google about the topic: {topic}. For each add a header then a newline Wikipedia:\n the group each question"
        queries_response = self.generate_response_with_openai(query_prompt)

        # Parse the response to extract the queries
        wikipedia_queries, wolfram_queries, google_queries = extract_queries_from_response(
            queries_response)

        # Step 3: Perform the searches using the generated queries
        wikipedia_results = [self.search_wikipedia(
            query) for query in wikipedia_queries]
        wolfram_results = [self.search_wolfram_alpha(
            query) for query in wolfram_queries]
        google_results = [self.search_web(query) for query in google_queries]

        # Step 4: Feed the search results back to the LLM to generate a summary and key points
        combined_results = {
            "wikipedia_results": wikipedia_results,
            "wolfram_results": wolfram_results,
            "google_results": google_results
        }
        summary_prompt = f"Given the search results: {combined_results}, summarize the findings and provide key points about the topic: {topic}."
        summary_and_key_points = self.generate_response_with_openai(
            summary_prompt)

        # Step 6: Ask the LLM for three follow-up ideas for clarity and exploration
        followup_prompt = f"Based on the summary and key points: {summary_and_key_points}, provide 3 ideas for follow-up questions for clarity and 3 ideas for follow-up questions for exploration."
        followup_questions = self.generate_response_with_openai(
            followup_prompt)

        return summary_and_key_points, followup_questions

    def get_research_summary(self):
        final_artifacts_dir = "final_artifacts"
        summary = []

        for filename in os.listdir(final_artifacts_dir):
            with open(os.path.join(final_artifacts_dir, filename), 'r') as file:
                artifact = json.load(file)
                summary.append(artifact)

        return summary


def extract_queries_from_response(self, response):
    # Define the regular expressions to match the platform headers and queries
    platform_header_pattern = re.compile(r"(Wikipedia|Wolfram Alpha|Google):")
    query_pattern = re.compile(r"\d\. (.*)")

    # Split the response into lines
    response_lines = response.split("\n")

    # Initialize empty lists for the queries
    wikipedia_queries, wolfram_queries, google_queries = [], [], []

    # Initialize the current platform as None
    current_platform = None

    # Iterate through the lines of the response
    for line in response_lines:
        # Check if the line matches a platform header
        header_match = platform_header_pattern.match(line)
        if header_match:
            current_platform = header_match.group(1)
            continue

        # Check if the line matches a query
        query_match = query_pattern.match(line)
        if query_match:
            query = query_match.group(1)

            # Append the query to the appropriate platform list
            if current_platform == "Wikipedia":
                wikipedia_queries.append(query)
            elif current_platform == "Wolfram Alpha":
                wolfram_queries.append(query)
            elif current_platform == "Google":
                google_queries.append(query)

    return wikipedia_queries, wolfram_queries, google_queries


# Example usage:
if __name__ == "__main__":
    researcher = ResearcherAgent()
    researcher.launch()
