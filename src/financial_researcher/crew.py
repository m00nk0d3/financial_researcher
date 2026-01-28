from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool


@CrewBase
class FinancialResearcher():
    """FinancialResearcher crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'


    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            tools=[SerperDevTool()],
            verbose=True
        )

    @agent
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['analyst'], # type: ignore[index]
            verbose=True
        )

    @task
    def research(self) -> Task:
        return Task(
            config=self.tasks_config['research'], # type: ignore[index]
        )

    @task
    def analysis(self) -> Task:
        return Task(
            config=self.tasks_config['analysis'], # type: ignore[index]
            output_file='output/report_{company}.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the FinancialResearcher crew"""
        
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
