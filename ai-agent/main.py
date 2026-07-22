"""
Main entry point for the Gherkin Test Case Generation Agent.
Accepts Swagger/OpenAPI files and generates positive/negative test cases.
"""

from functools import cached_property
import os
import json
import yaml
from pathlib import Path

# Flag set to True when optional LLM libraries are present.
LLM_AVAILABLE = False

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.genai import Client
from google.adk.tools import agent_tool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import url_context


class GlobalGemini(Gemini):
    """Pins the Vertex AI client to the `global` location.
    
    gemini-3 series models are only served from `global`; the default ADK
    `Gemini` integration constructs a `google.genai.Client` whose location
    defaults to the AgentEngine instance's region (e.g. `us-central1`) and
    fails with model-not-found for these models. Subclassing per the override
    pattern documented on `google.adk.models.google_llm.Gemini` lets the agent
    keep running in its regional AgentEngine instance while routing the model
    request to the global endpoint.
    """

    @cached_property
    def api_client(self) -> Client:
        return Client(vertexai=True, location="global")


# Support agent for Google search
spec_reader_google_search_agent = LlmAgent(
    name='SpecReader_google_search_agent',
    model=GlobalGemini(model='gemini-3.5-flash'),
    description='Agent specialized in performing Google searches.',
    sub_agents=[],
    instruction='Use the GoogleSearchTool to find information on the web.',
    tools=[
        GoogleSearchTool()
    ],
)

# Support agent for URL content retrieval
spec_reader_url_context_agent = LlmAgent(
    name='SpecReader_url_context_agent',
    model=GlobalGemini(model='gemini-3.5-flash'),
    description='Agent specialized in fetching content from URLs.',
    sub_agents=[],
    instruction='Use the UrlContextTool to retrieve content from provided URLs.',
    tools=[
        url_context
    ],
)

# Main root agent for generating Gherkin test cases
spec_reader_agent = LlmAgent(
    name='SpecReaderGherkinAgent',
    model=GlobalGemini(model='gemini-3.5-flash'),
    description=(
        'Agent specialized in reading Swagger/OpenAPI specifications and generating '
        'positive and negative Gherkin/Cucumber test cases.'
    ),
    sub_agents=[],
    instruction=(
        'You are a QA automation expert. Your job is to:\n'
        '1. Read and parse the provided Swagger/OpenAPI specification file\n'
        '2. Analyze all endpoints, request/response schemas, and validation rules\n'
        '3. Generate comprehensive Gherkin/Cucumber test cases covering:\n'
        '   - POSITIVE TESTS: Valid requests with expected successful responses\n'
        '   - NEGATIVE TESTS: Invalid inputs, boundary cases, error scenarios\n'
        '4. Format output as valid Gherkin syntax with Feature, Scenario, Given, When, Then steps\n'
        '5. Include test cases for:\n'
        '   - Happy path scenarios\n'
        '   - Input validation errors (required fields, data types)\n'
        '   - Authentication/authorization failures\n'
        '   - Rate limiting and performance boundaries\n'
        '   - Edge cases and boundary values\n'
    ),
    tools=[
        agent_tool.AgentTool(agent=spec_reader_google_search_agent),
        agent_tool.AgentTool(agent=spec_reader_url_context_agent)
    ],
)


def load_swagger_file(file_path: str) -> dict:
    """Load and parse a Swagger/OpenAPI file (JSON or YAML)."""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        if file_path.endswith('.json'):
            return json.load(f)
        elif file_path.endswith(('.yaml', '.yml')):
            return yaml.safe_load(f)
        else:
            raise ValueError("File must be JSON or YAML format")


def generate_test_cases(swagger_file_path: str) -> str:
    """
    Main function to generate Gherkin test cases from a Swagger/OpenAPI file.
    
    Args:
        swagger_file_path: Path to the Swagger/OpenAPI file
        
    Returns:
        Generated Gherkin test cases as a string
    """
    # Load the Swagger/OpenAPI file
    spec = load_swagger_file(swagger_file_path)

    # Prepare the specification content for the agent
    spec_content = json.dumps(spec, indent=2)
    
    # Get the API title and version for context
    api_info = spec.get('info', {})
    api_title = api_info.get('title', 'API')
    api_version = api_info.get('version', '1.0')
    
    prompt = f"""
Please analyze the following {api_title} (v{api_version}) specification and generate comprehensive Gherkin test cases.

SWAGGER/OPENAPI SPECIFICATION:
{spec_content}

Generate test cases in the following format:
- Use Feature blocks for each endpoint or logical grouping
- Include both POSITIVE and NEGATIVE test scenarios
- Use standard Gherkin syntax (Given, When, Then)
- Ensure coverage of all HTTP methods and status codes documented
- Include validation, edge cases, and error handling scenarios

Output only the Gherkin feature files. No additional explanation needed.
"""
    
    # Call the agent to generate test cases
    # Special-case the ADK LlmAgent which exposes run(ctx=..., node_input=...)
    if spec_reader_agent is None:
        raise RuntimeError("LLM agent is not configured.")

    import inspect

    last_exc = None
    agent_type = type(spec_reader_agent).__name__

    # If this is the ADK LlmAgent, try the ADK run signature first
    if agent_type == 'LlmAgent' and hasattr(spec_reader_agent, 'run'):
        try:
            # Try common node_input shapes
            try:
                return spec_reader_agent.run(ctx={}, node_input={'messages': [{'role': 'user', 'content': prompt}]})
            except TypeError:
                pass
            try:
                return spec_reader_agent.run(ctx={}, node_input={'input': prompt})
            except TypeError:
                pass
            try:
                # Some ADK variants accept node_input as raw string
                return spec_reader_agent.run(ctx={}, node_input=prompt)
            except TypeError as e:
                last_exc = e
        except Exception as e:
            last_exc = e

    # Generic fallback: try a variety of common method names and call patterns
    for method in ('generate', 'run', 'execute', 'call', 'respond', 'predict', 'chat'):
        fn = getattr(spec_reader_agent, method, None)
        if not callable(fn):
            continue
        try:
            sig = inspect.signature(fn)
            params = sig.parameters
            # Prefer calling with a single positional prompt if the callable accepts >=1 positional arg
            positional_params = [p for p in params.values()
                                 if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)]

            # If the function expects no arguments, call without args
            if len(positional_params) == 0:
                result = fn()
                return result

            # If it accepts at least one positional, call with prompt
            if len(positional_params) >= 1:
                try:
                    result = fn(prompt)
                    return result
                except TypeError:
                    # positional call failed; try keyword variants below
                    pass

            # Try common keyword names
            kw_variants = ('prompt', 'input', 'text', 'instruction', 'messages')
            kw = {}
            for name in kw_variants:
                if name in params:
                    if name == 'messages':
                        kw[name] = [prompt]
                    else:
                        kw[name] = prompt
                    break

            if kw:
                result = fn(**kw)
                return result

            # As a last resort, try calling with a single-element list (some SDKs expect messages)
            try:
                result = fn([prompt])
                return result
            except TypeError as e:
                last_exc = e
                continue

        except Exception as e:
            last_exc = e
            continue

    # If we reach here, no invocation succeeded
    if last_exc:
        try:
            agent_methods = [n for n in dir(spec_reader_agent) if not n.startswith('_')]
        except Exception:
            agent_methods = []
        raise RuntimeError(
            f"Failed to invoke LLM agent; last error: {last_exc!r}; agent_type: {agent_type}; agent_methods: {agent_methods}"
        ) from last_exc
    raise RuntimeError("LLM agent object doesn't expose a known generation method.")


def generate_test_cases_from_text(swagger_yaml_text: str) -> str:
    """
    Generate test cases directly from Swagger/OpenAPI content as text.
    
    Args:
        swagger_yaml_text: Swagger/OpenAPI specification as string (YAML or JSON)
        
    Returns:
        Generated Gherkin test cases as a string
    """
    prompt = f"""
Please analyze the following Swagger/OpenAPI specification and generate comprehensive Gherkin test cases.

SWAGGER/OPENAPI SPECIFICATION:
{swagger_yaml_text}

Generate test cases in the following format:
- Use Feature blocks for each endpoint or logical grouping
- Include both POSITIVE and NEGATIVE test scenarios
- Use standard Gherkin syntax (Given, When, Then)
- Ensure coverage of all HTTP methods and status codes documented
- Include validation, edge cases, and error handling scenarios

Output only the Gherkin feature files. No additional explanation needed.
"""
    
    # Support multiple possible ADK/LLM SDK method names
    if spec_reader_agent is None:
        raise RuntimeError("LLM agent is not configured.")
    for method in ('generate', 'run', 'execute', 'call', 'respond', 'predict', 'chat'):
        fn = getattr(spec_reader_agent, method, None)
        if callable(fn):
            result = fn(prompt)
            break
    else:
        raise RuntimeError("LLM agent object doesn't expose a known generation method.")
    return result


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <swagger_file_path>")
        print("Example: python main.py ./swagger.yaml")
        sys.exit(1)
    
    swagger_file = sys.argv[1]
    
    print(f"Generating Gherkin test cases from: {swagger_file}")
    print("-" * 60)
    
    test_cases = generate_test_cases(swagger_file)
    
    print(test_cases)
    
    # Optionally save to file
    output_file = Path(swagger_file).stem + "_tests.feature"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(test_cases)
    
    print("-" * 60)
    print(f"Test cases saved to: {output_file}")
