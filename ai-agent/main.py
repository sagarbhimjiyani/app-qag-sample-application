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


def generate_test_cases_from_spec(spec: dict) -> str:
    """Generate Gherkin test cases from a parsed OpenAPI/Swagger spec dict.

    Tries ADK agent first, falls back to google.genai Client, then to a simple
    deterministic converter if remote SDKs or credentials are unavailable.
    """
    # Prepare prompt and context
    spec_content = json.dumps(spec, indent=2)
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

    # Try ADK agent first (if available) using a Runner-backed invocation
    adk_error = None
    if LLM_AVAILABLE and 'spec_reader_agent' in globals() and spec_reader_agent is not None:
        try:
            # Use an in-memory session service and Runner to build a proper InvocationContext
            from google.adk.runners import Runner
            from google.adk.sessions.in_memory_session_service import InMemorySessionService
            from google.genai import types as genai_types

            session_svc = InMemorySessionService()
            runner = Runner(session_service=session_svc, app_name='gherkin-agent', agent=spec_reader_agent)

            # Build a Content with a single Part containing the prompt
            user_content = genai_types.Content(parts=[genai_types.Part(text=prompt)])

            # Runner.run yields Events; collect textual parts from event.content.parts
            events = runner.run(user_id='user', session_id='local', new_message=user_content)
            parts = []
            for event in events:
                content = getattr(event, 'content', None)
                if not content:
                    continue
                for p in getattr(content, 'parts', []) or []:
                    text = getattr(p, 'text', None)
                    if text:
                        parts.append(str(text))

            try:
                runner.close()
            except Exception:
                pass

            if parts:
                return '\n'.join(parts)
            # If ADK produced no textual parts, fall through to genai fallback
        except Exception as e:
            adk_error = e
    else:
        adk_error = RuntimeError('ADK/LLM agent unavailable')

    # Next fallback: try google.genai Client directly (requires ADC)
    genai_exc = None
    try:
        from google.genai import Client
        client = Client(vertexai=True, location='global')
        # Prefer chats API if available
        if hasattr(client, 'chats') and getattr(client, 'chats') is not None:
            try:
                resp = client.chats.create(model='gemini-3.5-chat', messages=[{'author': 'user', 'content': prompt}])
                # Try common response shapes
                if hasattr(resp, 'last'):
                    return str(getattr(resp, 'last'))
                if hasattr(resp, 'output'):
                    return str(resp.output)
                return str(resp)
            except Exception as e:
                genai_exc = e
        # Fallback to models.generate if present
        if hasattr(client, 'models') and getattr(client, 'models') is not None and hasattr(client.models, 'generate'):
            try:
                gen = client.models.generate(model='text-bison-001', input=prompt)
                if hasattr(gen, 'text'):
                    return str(gen.text)
                if hasattr(gen, 'output'):
                    return str(gen.output)
                return str(gen)
            except Exception as e:
                genai_exc = e
    except Exception as e:
        genai_exc = e

    # Final fallback: deterministic generator from spec to Gherkin
    def simple_spec_to_gherkin(spec: dict) -> str:
        title = api_title
        parts = [f'Feature: {title}']
        paths = spec.get('paths', {}) or {}
        if not paths:
            parts.append('\n# No paths found in spec; returning a minimal template')
            parts.append('\nScenario: Minimal check')
            parts.append('  Given the API exists')
            parts.append('  When I send a GET request to /')
            parts.append('  Then I should receive a response')
            return '\n'.join(parts)
        for path, methods in paths.items():
            if not isinstance(methods, dict):
                continue
            for method, info in methods.items():
                summary = info.get('summary') if isinstance(info, dict) else None
                parts.append(f"\n# {summary or ''}")
                parts.append(f"Scenario: {method.upper()} {path}")
                parts.append(f"  Given the API is available")
                parts.append(f"  When I send a {method.upper()} request to {path}")
                parts.append(f"  Then I should receive a 200 response (or appropriate status)")
        return '\n'.join(parts)

    fallback = simple_spec_to_gherkin(spec)
    diagnostic = f"\n\n# Fallback used. ADK error: {getattr(adk_error, 'args', adk_error)}; genai error: {getattr(genai_exc, 'args', genai_exc)}"
    return fallback + diagnostic


def generate_test_cases(swagger_file_path: str) -> str:
    """
    Main function to generate Gherkin test cases from a Swagger/OpenAPI file.
    
    Args:
        swagger_file_path: Path to the Swagger/OpenAPI file
        
    Returns:
        Generated Gherkin test cases as a string
    """
    spec = load_swagger_file(swagger_file_path)
    return generate_test_cases_from_spec(spec)


def generate_test_cases_from_text(swagger_yaml_text: str) -> str:
    """Generate test cases directly from Swagger/OpenAPI content as text.

    Tries to parse the text as JSON or YAML and then delegates to
    generate_test_cases_from_spec.
    """
    # Try parse as JSON then YAML
    try:
        spec = json.loads(swagger_yaml_text)
    except Exception:
        try:
            spec = yaml.safe_load(swagger_yaml_text)
        except Exception:
            raise ValueError('Provided specification text is not valid JSON or YAML')
    if not isinstance(spec, dict):
        raise ValueError('Parsed specification is not an object')
    return generate_test_cases_from_spec(spec)


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
