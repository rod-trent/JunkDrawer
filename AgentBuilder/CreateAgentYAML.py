import argparse
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def generate_agent_yaml(prompt, output_file):
    # Initialize the xAI Grok API client (OpenAI-compatible)
    client = OpenAI(
        api_key=os.getenv("XAI_API_KEY"),
        base_url="https://api.x.ai/v1",
    )
    
    if not client.api_key:
        raise ValueError("XAI_API_KEY environment variable not set. Please set it to use the Grok API.")
    
    # System prompt to guide Grok in generating CrewAI-compatible agent YAML
    system_prompt = """
    You are an expert in creating AI agent configurations for CrewAI.
    Based on the user's description, generate a valid YAML file for a single agent.
    Include at least: role, goal, backstory.
    Optionally include: tools (as a list), llm (e.g., 'grok-3'), verbose (true/false), allow_delegation (true/false), etc.
    Use placeholders like {topic} if needed for dynamic values.
    Output ONLY the YAML content, nothing else. Do not include ```yaml or any wrappers.
    Example structure:
    my_agent:
      role: > 
        Senior Researcher
      goal: > 
        Uncover insights on {topic}
      backstory: > 
        You are an expert in researching {topic}...
      verbose: true
      tools:
        - SerperDevTool
    """
    
    # User message with the prompt
    user_message = f"Generate CrewAI agent YAML for: {prompt}"
    
    # Call Grok API to generate the YAML
    response = client.chat.completions.create(
        model="grok-3",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=1000,
        temperature=0.5,  # Balanced creativity and structure
    )
    
    generated_yaml = response.choices[0].message.content.strip()
    
    # Write to output file
    with open(output_file, 'w') as f:
        f.write(generated_yaml)
    
    print(f"Agent YAML generated and saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an AI Agent YAML from a prompt using Grok API.")
    parser.add_argument("--prompt", required=True, help="The prompt describing the agent (e.g., 'Create a researcher agent for AI news').")
    parser.add_argument("--output", default="agent.yaml", help="Output YAML file path (default: agent.yaml).")
    
    args = parser.parse_args()
    generate_agent_yaml(args.prompt, args.output)
