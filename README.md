# Escher's Journal
Math visuals that write themselves



![image](https://user-images.githubusercontent.com/1278972/230845767-450cef09-68a0-4e45-97c8-1ae716582cd5.png)

This project is a work in progress

Plan:
- [x] Wireframe Agents
- [ ] Make basic UI to explore artifacts of agents run(in progress)
- [ ] Finish coding agents so that they work(in progress)
- [ ] Make backend that can launch jobs from frontend for some steering(in progress)


## Agents Overview
The project consist of a set of agents that magically do research for you

### Vis Programmer Agent
The Vis Programmer Agent creates interactive visualizations using Three.js, based on user requests. It iteratively generates and tests code until it compiles without errors. After successful compilation, the agent confirms the result using a vision model and saves the visualization along with relevant text.

### Researcher Agent
The Researcher Agent is responsible for researching a given mathematical topic. It searches the internet, poses questions, critiques responses, and gathers contrary evidence. The agent saves research artifacts as notes, facts, key points, and requests for visualizations. It can also kick off the Vis Programmer Agent to create visualizations based on the research.

### Vis Critic Agent
The Vis Critic Agent reads and critiques the final visualizations created by the Vis Programmer Agent. It uses the HuggingFace BLIP-2 model to read the image and asks various questions about the visualization. The agent then provides feedback to the Vis Programmer Agent to fix errors, elaborate on the visualization, or leave it as is, depending on the quality of the visualization.
