# FinancialResearcher Crew

Welcome to the FinancialResearcher Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/financial_researcher/config/agents.yaml` to define your agents
- Modify `src/financial_researcher/config/tasks.yaml` to define your tasks
- Modify `src/financial_researcher/crew.py` to add your own logic, tools and specific args
- Modify `src/financial_researcher/main.py` to add custom inputs for your agents and tasks

## Running the Project

### Web Interface (Recommended)

The easiest way to use the Financial Researcher is through the web interface:

```bash
$ uv run web
```

This will start the web server at `http://127.0.0.1:5000`. Open this URL in your browser to:
1. Enter a company name in the form
2. Watch real-time progress as AI agents research the company
3. View the final report rendered as HTML

#### Enhanced Agent Dashboard

The web interface now features an **enhanced agent activity dashboard** that showcases the agentic workflow in action:

- **Agent Cards**: Visual representation of the Researcher and Analyst agents with real-time status updates
- **Task Timeline**: Progress visualization showing the research and analysis tasks
- **Tool Usage**: See which tools (like SerperDevTool) are being used by each agent
- **Categorized Logs**: Color-coded activity logs with icons for different event types:
  - 🔧 Tool usage
  - 💭 Agent thinking/reasoning
  - 👤 Agent transitions
  - 📋 Task starts/completions

The interface updates in real-time, giving you full visibility into how the AI agents collaborate to research and analyze companies.

### Command Line Interface

To run research from the command line, use:

```bash
$ crewai run
```

This command initializes the financial_researcher Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The financial_researcher Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the FinancialResearcher Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
