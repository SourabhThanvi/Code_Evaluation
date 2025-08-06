from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
LANGGRAPH_AVAILABLE = True
import sys
import os
from pydantic import BaseModel, Field
from typing import TypedDict, Literal, Optional
try:
    from typing import Annotated
except ImportError:
    # For Python 3.8 compatibility
    from typing_extensions import Annotated
from langchain_core.messages import BaseMessage, HumanMessage


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Agent.client import Client
from Agent.custom_prompt import SYSTEM_PROMPT, COMPLEXITY_SYSTEM_PROMPT
from Agent.markdown_remover import clean_code_output

# Initialize the LLM client
google_llm = Client().load_google_llm()

# Define the state for the code generation workflow
class CodeGenerationState(TypedDict):
    user_query: str
    generated_code: str
    complexity_status: Literal["simple", "complex"]
    feedback: str
    loop_count: int
    # conversation_history will accumulate messages from the LLM interactions
    conversation_history: Annotated[list[HumanMessage], add_messages]
    final_code: Optional[str] # This will hold the final, simplified code string

# Pydantic model for structured output from the complexity checker LLM
class CodeEvaluation(BaseModel):
    complexity_status: Literal["simple", "complex"] = Field(
        ..., description='Classification of code complexity: "simple" or "complex".'
    )
    feedback: str = Field(
        ..., description='Detailed feedback for simplification if the code is complex, or an empty string if simple.'
    )

# Configure the LLM to return structured output based on CodeEvaluation
structured_google_llm = google_llm.with_structured_output(CodeEvaluation)

# Node: Code Generation
def code_creation(state: CodeGenerationState) -> dict:
    """
    Generates initial code or refines existing code based on user query and feedback.
    """
    query = state['user_query']
    current_loop = state.get('loop_count', 0)

    # Build prompt based on whether it's the first attempt or a refinement
    if current_loop > 0 and state.get('feedback'):
        prompt = f"""
{SYSTEM_PROMPT}

User Request: {query}
Previous Attempt Feedback: {state['feedback']}

Please generate improved, simpler code based on the feedback. Focus on reducing complexity for a fresher, while maintaining full functionality and correctness.
"""
    else:
        prompt = f"""
{SYSTEM_PROMPT}

User Request: {query}

Generate clean, simple Python code for this request, suitable for a programming fresher.
"""

    # Invoke the LLM to generate code
    response = google_llm.invoke([HumanMessage(content=prompt)])

    # Clean the generated code to remove markdown markers
    cleaned_code = clean_code_output(response.content)

    # Return updated state
    return {
        'generated_code': cleaned_code,
        'conversation_history': [HumanMessage(content=f"Generated Code (Loop {current_loop + 1}):\n{cleaned_code}")],
        'loop_count': current_loop + 1
    }

# Node: Complexity Checker
def complexity_checker(state: CodeGenerationState) -> dict:
    """
    Evaluates the generated code for complexity and provides feedback.
    """
    code = state['generated_code']

    prompt = f"""
{COMPLEXITY_SYSTEM_PROMPT}

Code to evaluate:

{code}


Is this code simple enough for a programming fresher?
"""

    # Invoke the structured LLM for complexity evaluation
    response = structured_google_llm.invoke([HumanMessage(content=prompt)])

    # Return updated state with complexity status and feedback
    return {
        'complexity_status': response.complexity_status,
        'feedback': response.feedback,
        'conversation_history': [HumanMessage(content=f"Complexity Check: {response.complexity_status}. Feedback: {response.feedback}")]
    }

# Conditional Edge: Route based on complexity and loop count
def route_eval(state: CodeGenerationState) -> str:
    """
    Determines the next step in the workflow: end, or refine.
    """
    # Check if we've hit the maximum number of refinement loops
    if state.get('loop_count', 0) >= 5:
        return 'end'

    # Check the complexity status
    if state.get('complexity_status') == 'simple':
        return 'end'
    else:
        # If complex and within loop limit, refine the code
        return 'refine'

# Node: Finalize Code
def finalize_code(state: CodeGenerationState) -> dict:
    """
    Sets the final generated code into the state.
    """
    return {
        'final_code': state['generated_code'],
        'conversation_history': [HumanMessage(content="Code generation workflow completed.")]
    }

# Graph Creation
graph = StateGraph(CodeGenerationState)

# Add nodes to the graph
graph.add_node('generate', code_creation)
graph.add_node('check', complexity_checker)
graph.add_node('finalize', finalize_code)

# Define the workflow edges
graph.add_edge(START, 'generate')
graph.add_edge('generate', 'check')

# Conditional routing from the 'check' node
graph.add_conditional_edges(
    'check',
    route_eval,
    {
        'end': 'finalize',   # If simple or max loops reached, finalize
        'refine': 'generate' # If complex and within loop limit, go back to generate
    }
)
graph.add_edge('finalize', END) # End the workflow after finalizing

# Compile the workflow for execution
workflow = graph.compile()

# initial_state = {
#         'user_query':'create a fibbonacci series upto 5 places.',
#         'generated_code':'',
#         'complexity_status':'complex', # Start as complex to ensure initial check
#         'feedback':'',
#         'loop_count':0,
#         'conversation_history':[],
#         'final_code':None
# }
# res = workflow.invoke(initial_state) 
# print(res['generated_code'])



