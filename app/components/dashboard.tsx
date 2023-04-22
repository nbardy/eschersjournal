"use client";

import { useRef } from "react";

interface DashboardProps {
  repo: string;
}

interface RepoData {
  agents: AgentData[];
  resultData: ResultData[];
}

interface AgentData {
  name: string;
  status: string;
  lastSeen: string;
  results: string[];
}

interface ResultData {
  name: string;
  file: string;
}

export async function Dashboard(dashboardProps: DashboardProps) {
  const data = fakeRepoData();
  const textareaRefName = useRef<HTMLTextAreaElement>(null);
  const textareaRefTopic = useRef<HTMLTextAreaElement>(null);

  return (
    <div>
      <h1>Dashboard</h1>
      <h2>Actions</h2>
      <div>
        <div>
          <label>Name</label>
          <textarea
            className="textarea-input text-input-name"
            ref={textareaRefName}
          ></textarea>
          <label>Topic</label>
          <textarea
            className="textarea-input text-input-topic"
            ref={textareaRefTopic}
          ></textarea>
          <button
            onClick={() =>
              textareaRefName.current?.value != null &&
              textareaRefTopic.current?.value != null &&
              spawnWorkers(
                textareaRefName.current.value,
                textareaRefTopic.current.value
              )
            }
          >
            Launch new workers for new repo
          </button>
        </div>
      </div>
      <h2>Agents</h2>
      <div className="agents">
        {data.agents.map((agent, i) => (
          <div className="agent" key={i}>
            <div className="info">
              <div>
                {agent.name}
                {/* if status == "online" do a green emoji or red otherwise and print status */}
                <span>
                  {agent.status === "online" ? (
                    <span role="img" aria-label="online">
                      ✅
                    </span>
                  ) : (
                    <span role="img" aria-label="offline">
                      ❌
                    </span>
                  )}
                </span>
              </div>
              <div>{agent.lastSeen}</div>
            </div>
            <h3>Results</h3>
            {agent.results
              ?.map((resultName, i) => {
                return getResultByName(resultName, data);
              })
              .filter((result): result is ResultData => !!result)
              .map((result) => {
                return (
                  <div className="result" key={i}>
                    <div>{result.name}</div>
                    <div>{result.file}</div>
                  </div>
                );
              })}
          </div>
        ))}
      </div>
    </div>
  );
}

export const fakeRepoData = (): RepoData => {
  return {
    agents: [
      {
        name: "agent1",
        status: "online",
        lastSeen: "2021-01-01",
        results: ["result1", "result2"],
      },
      {
        name: "agent2",
        status: "online",
        lastSeen: "2021-01-01",
        results: [],
      },
    ],
    resultData: [
      {
        name: "result1",
        file: "file1",
      },
      {
        name: "result2",
        file: "file2",
      },
    ],
  };
};
const getResultByName = (resultName: string, repo: RepoData) => {
  const data = repo.resultData;
  return data.find((result) => result.name === resultName);
};

// Sends a request to the backend to spawn worekrs for a new repo
const spawnWorkers = (name: string, topic: string) => {
  const url = "http://localhost:9002/repo/spawn";
  const data = { name, topic };
  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Success:", data);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
};
