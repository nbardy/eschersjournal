"use client";

import { useRef, useState } from "react";
import { REPL_MODE_SLOPPY } from "repl";
import { spawnOnRepo, RepoCreate, createRepo } from "../api/model_server";

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

// helper functions
const createAndSpawn = async (
  name: string | null | undefined,
  topic: string | null | undefined
) => {
  if (name == null || topic == null) {
    return;
  }

  const repoData: RepoCreate = {
    name: name,
    topic: topic,
  };
  const response = await createRepo(repoData);
  console.log(response);

  await spawnOnRepo({
    repo_id: name,
  });

  return response;
};

export async function Dashboard(dashboardProps: DashboardProps) {
  const textareaRefName = useRef<HTMLTextAreaElement>(null);
  const textareaRefTopic = useRef<HTMLTextAreaElement>(null);

  const [currentRepoName, setCurrentRepoName] = useState("fakeRepo");

  const currentRepo = data.repos[currentRepoName];

  return (
    <div>
      <h1>Dashboard</h1>
      <div>
        <h2>Repos</h2>
        {Object.keys(data.repos).map((repoName, i) => {
          return (
            <div key={i}>
              {repoName}
              {/* set current on click */}
              <button onClick={() => setCurrentRepoName(repoName)}>
                Make Active
              </button>
            </div>
          );
        })}
        <h4>New Repo</h4>
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
                createAndSpawn(
                  textareaRefName.current?.value,
                  textareaRefTopic.current?.value
                )
              }
            >
              Create Repo
            </button>
          </div>
        </div>
      </div>
      <h2>Current Repo: {currentRepoName}</h2>
      <h2>Agents</h2>
      <button
        onClick={() => {
          spawnOnRepo({ repo_id: currentRepoName });
        }}
      >
        Spawn
      </button>
      <div className="agents">
        {currentRepo.agents.map((agent, i) => (
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
                return getResultByName(resultName, currentRepo);
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

// const data = {
//   repos: {
//     fakeRepo:  fakeRepoData(),
//   },
// };

// with string index signature
const data = {
  repos: {
    fakeRepo: fakeRepoData(),
  },
} as { repos: { [key: string]: RepoData } };

const getResultByName = (resultName: string, repo: RepoData) => {
  const data = repo.resultData;
  return data.find((result) => result.name === resultName);
};
