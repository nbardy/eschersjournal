if __name__ == "__main__":
    vis_programmer = VisProgrammerAgent()
    researcher = ResearcherAgent()

    # Example visualization code
    code = {
        "html": "<div id='visualization'></div>",
        "js": "console.log('Hello, World!');",
        "css": "#visualization { width: 100%; height: 100%; }"
    }

    # Example visualization summary
    summary = {
        "title": "Sample Visualization",
        "description": "A simple example of a visualization."
    }

    # Example visualization image (placeholder)
    image = b""

    # Save the visualization
    vis_programmer.save_visualization(code, summary, image, is_final=True)

    # Example research artifacts
    notes = "These are some example notes from the researcher."
    facts = {"fact1": "The Earth is round.", "fact2": "Water boils at 100°C at sea level."}
    key_points = {"key_point1": "Einstein's theory of relativity.", "key_point2": "Newton's laws of motion."}
    vis_request = {"topic": "Sample Visualization", "type": "bar_chart", "data": [1, 2, 3]}

    # Save the research artifacts
    researcher.save_research_artifact("notes", notes, is_final=True)
    researcher.save_research_artifact("facts", facts, is_final=True)
    researcher.save_research_artifact("key_points", key_points, is_final=True)
    researcher.save_research_artifact("requests_for_visualizations", vis_request, is_final=True)

