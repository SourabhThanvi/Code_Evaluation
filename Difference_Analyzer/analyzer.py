# ast_analyzer.py - Corrected version for your Diff_analysis folder
import ast
import json
import os
from datetime import datetime
from typing import TypedDict, Dict, List, Optional, Any, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from Agent.client import Client
    from Agent.custom_prompt import REPORT_BUILDER_SYSTEM_PROMPT
    google_llm = Client().load_google_llm()
except ImportError as e:
    print(f"Warning: Could not import Agent modules: {e}")
    google_llm = None


# State definition for AST analysis workflow
class ASTAnalysisState(TypedDict):
    original_code: str
    modified_code: str
    original_ast: Optional[Dict]
    modified_ast: Optional[Dict]
    structural_changes: Dict
    pattern_insights: Dict
    learning_summary: Dict
    analysis_history: Annotated[List[Dict], add_messages]
    final_report: Optional[str]  # Changed from Dict to str

# Pydantic models for structured analysis
class StructuralChange(BaseModel):
    change_type: str = Field(..., description="Type of structural change detected")
    location: str = Field(..., description="Where in the code the change occurred")
    severity: str = Field(..., description="Impact level: low, medium, high")
    description: str = Field(..., description="Human-readable description of the change")

class PatternInsight(BaseModel):
    pattern_type: str = Field(..., description="Type of coding pattern identified")
    frequency: int = Field(..., description="How often this pattern appears")
    recommendation: str = Field(..., description="Suggestion for improvement")
    confidence: float = Field(..., description="Confidence score 0-1")

class ReportOutput(BaseModel):
    change_summary: str = Field(
        ..., 
        description="High-level bullet or paragraph summarizing what changed between versions."
    )
    developer_insights: str = Field(
        ..., 
        description="Concise notes on the developers style or behavior (e.g. 'prefers brevity', 'stripped validation')."
    )
    learning_observations: str = Field(
        ..., 
        description="What the developer can learn next (e.g. 'reinforce edge-case handling', 'add docstrings')."
    )
    suggestions: List[str] = Field(
        ..., 
        description="Actionable recommendations (1-3 bullets) to improve code or process."
    )

# Strucutred_Output_LLm
structured_llm = google_llm.with_structured_output(ReportOutput)


class ASTAnalyzer:
    def __init__(self, patterns_file: str = "Generated/ast_patterns.json"):
        self.patterns_file = patterns_file
        self.stored_patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict:
        """Load existing AST patterns from JSON file"""
        if os.path.exists(self.patterns_file):
            try:
                with open(self.patterns_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"analysis_count": 0, "patterns": [], "learned_insights": {}}
        return {"analysis_count": 0, "patterns": [], "learned_insights": {}}
    
    def _save_patterns(self):
        """Save patterns to JSON file"""
        os.makedirs(os.path.dirname(self.patterns_file), exist_ok=True)
        with open(self.patterns_file, 'w') as f:
            json.dump(self.stored_patterns, f, indent=2)

# Node 1: AST Parser
def ast_parser_node(state: ASTAnalysisState) -> Dict:
    """Parse both code versions into AST representations"""
    
    def safe_parse(code: str, filename: str) -> Optional[Dict]:
        try:
            tree = ast.parse(code)
            
            # Fixed import extraction logic
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}" if module else alias.name)
            
            return {
                'functions': [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)],
                'classes': [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)],
                'imports': imports,
                'variables': [node.id for node in ast.walk(tree) 
                             if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)],
                'complexity_metrics': {
                    'total_nodes': len(list(ast.walk(tree))),
                    'function_count': len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                    'class_count': len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                    'if_statements': len([n for n in ast.walk(tree) if isinstance(n, ast.If)]),
                    'loops': len([n for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While))]),
                }
            }
        except SyntaxError as e:
            return {'error': f'Syntax error in {filename}: {str(e)}'}
        except Exception as e:
            return {'error': f'Parse error in {filename}: {str(e)}'}
    
    original_ast = safe_parse(state['original_code'], 'original.py')
    modified_ast = safe_parse(state['modified_code'], 'modified.py')
    
    return {
        'original_ast': original_ast,
        'modified_ast': modified_ast,
        'analysis_history': [{'role': 'system', 'content': f'AST parsing completed at {datetime.now().isoformat()}'}]
    }

# Node 2: Structure Analyzer
def structure_analyzer_node(state: ASTAnalysisState) -> Dict:
    """Analyze structural differences between ASTs"""
    
    original = state['original_ast']
    modified = state['modified_ast']
    
    if not original or not modified or 'error' in original or 'error' in modified:
        return {
            'structural_changes': {'error': 'Could not analyze due to parsing errors'},
            'analysis_history': [{'role': 'system', 'content': 'Structure analysis failed due to parsing errors'}]
        }
    
    changes = {
        'functions': {
            'added': list(set(modified['functions']) - set(original['functions'])),
            'removed': list(set(original['functions']) - set(modified['functions'])),
            'common': list(set(original['functions']) & set(modified['functions']))
        },
        'classes': {
            'added': list(set(modified['classes']) - set(original['classes'])),
            'removed': list(set(original['classes']) - set(modified['classes'])),
            'common': list(set(original['classes']) & set(modified['classes']))
        },
        'imports': {
            'added': list(set(modified['imports']) - set(original['imports'])),
            'removed': list(set(original['imports']) - set(modified['imports'])),
            'common': list(set(original['imports']) & set(modified['imports']))
        },
        'complexity_delta': {
            metric: modified['complexity_metrics'][metric] - original['complexity_metrics'][metric]
            for metric in original['complexity_metrics']
            if metric in modified['complexity_metrics']
        }
    }
    
    changes_detected = sum(len(v.get('added', [])) + len(v.get('removed', [])) 
                          for k, v in changes.items() if isinstance(v, dict) and 'added' in v)
    return {
        'structural_changes': changes,
        'analysis_history': [{'role': 'system', 'content': f'Structure analysis completed at {datetime.now().isoformat()}. Changes detected: {changes_detected}'}]
    }

# Node 3: Pattern Extractor
def pattern_extractor_node(state: ASTAnalysisState) -> Dict:
    """Extract coding patterns and user preferences"""
    
    changes = state['structural_changes']
    
    # Added safety checks for missing keys
    functions_added = len(changes.get('functions', {}).get('added', []))
    classes_added = len(changes.get('classes', {}).get('added', []))
    functions_removed = len(changes.get('functions', {}).get('removed', []))
    
    complexity_delta = changes.get('complexity_delta', {})
    total_nodes_delta = complexity_delta.get('total_nodes', 0)
    if_statements_delta = complexity_delta.get('if_statements', 0)
    loops_delta = complexity_delta.get('loops', 0)
    
    patterns = {
        'user_preferences': {
            'prefers_functions_over_classes': functions_added > classes_added,
            'adds_complexity': total_nodes_delta > 0,
            'import_behavior': 'conservative' if len(changes.get('imports', {}).get('added', [])) <= 1 else 'expansive',
            'refactoring_style': 'simplifier' if total_nodes_delta < 0 else 'enhancer'
        },
        'common_modifications': {
            'function_additions': functions_added,
            'function_removals': functions_removed,
            'complexity_increase': total_nodes_delta,
            'control_flow_changes': if_statements_delta + loops_delta
        },
        'quality_indicators': {
            'maintains_structure': len(changes.get('functions', {}).get('common', [])) > 0,
            'adds_features': functions_added > 0,
            'cleans_code': functions_removed > 0 and total_nodes_delta < 0
        }
    }
    
    return {
        'pattern_insights': patterns,
        'analysis_history': [{'role': 'system', 'content': f'Pattern extraction completed at {datetime.now().isoformat()}. Patterns found: {len(patterns)}'}]
    }

# Node 4: Learning Insights
def learning_insights_node(state: ASTAnalysisState) -> Dict:
    """Generate insights about user coding behavior"""
    
    patterns = state['pattern_insights']
    
    insights = {
        'coding_style_analysis': {
            'complexity_tendency': 'increases' if patterns['user_preferences']['adds_complexity'] else 'simplifies',
            'structural_preference': 'functional' if patterns['user_preferences']['prefers_functions_over_classes'] else 'object_oriented',
            'modification_approach': patterns['user_preferences']['refactoring_style']
        },
        'learning_recommendations': [],
        'behavioral_patterns': {
            'consistency_score': 0.8,  # Placeholder - would be calculated from historical data
            'improvement_areas': [],
            'strengths': []
        }
    }
    
    # Generate recommendations based on patterns
    if patterns['user_preferences']['adds_complexity']:
        insights['learning_recommendations'].append("Consider code simplification techniques")
    if patterns['common_modifications']['function_additions'] > 2:
        insights['learning_recommendations'].append("Focus on modular design principles")
    
    return {
        'learning_summary': insights,
        'analysis_history': [{'role': 'system', 'content': f'Learning insights generated at {datetime.now().isoformat()}. Recommendations: {len(insights["learning_recommendations"])}'}]
    }

# Node 5: Report Builder
def report_builder_node(state: ASTAnalysisState) -> Dict:
    """Build comprehensive analysis report"""
    
    # Convert analysis_history messages to serializable format
    serializable_history = []
    for msg in state['analysis_history']:
        if hasattr(msg, 'content'):
            serializable_history.append({
                'role': getattr(msg, 'type', 'system'),
                'content': msg.content
            })
        else:
            serializable_history.append(msg)
    
    report_data = {
        'analysis_metadata': {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'AST_structural_analysis',
            'workflow_version': '1.0'
        },
        'structural_summary': state['structural_changes'],
        'pattern_analysis': state['pattern_insights'],
        'learning_insights': state['learning_summary'],
        'recommendations': state['learning_summary']['learning_recommendations'],
        'analysis_chain': serializable_history
    }
    
    # Handle case where google_llm is not available
    if structured_llm:
        try:
            final_prompt = REPORT_BUILDER_SYSTEM_PROMPT + "\n\n" + json.dumps(report_data, indent=2)
            final_report = structured_llm.invoke(final_prompt)
        except Exception as e:
            final_report = f"LLM report generation failed: {str(e)}\n\nRaw analysis data:\n{json.dumps(report_data, indent=2)}"
    else:
        final_report = f"LLM not available. Raw analysis data:\n{json.dumps(report_data, indent=2)}"
    
    return {
        'final_report': final_report,
        'analysis_history': [{'role': 'system', 'content': f'Report building completed at {datetime.now().isoformat()}. Analysis workflow finished.'}]
    }

# Graph Creation
def create_ast_analysis_workflow() -> StateGraph:
    """Create the AST analysis workflow graph"""
    
    graph = StateGraph(ASTAnalysisState)
    
    # Add nodes
    graph.add_node('parse_ast', ast_parser_node)
    graph.add_node('analyze_structure', structure_analyzer_node)
    graph.add_node('extract_patterns', pattern_extractor_node)
    graph.add_node('generate_insights', learning_insights_node)
    graph.add_node('build_report', report_builder_node)
    
    # Define edges
    graph.add_edge(START, 'parse_ast')
    graph.add_edge('parse_ast', 'analyze_structure')
    graph.add_edge('analyze_structure', 'extract_patterns')
    graph.add_edge('extract_patterns', 'generate_insights')
    graph.add_edge('generate_insights', 'build_report')
    graph.add_edge('build_report', END)
    
    return graph.compile()

# CLI Integration Function
def analyze_with_ast_workflow(original_file: str, modified_file: str) -> str:
    """
    Analyze code differences using AST-based LangGraph workflow
    To be integrated into your agent.py analyze command
    """
    
    try:
        # # Check if files exist
        if not os.path.exists(original_file):
            return f"Error: Original file '{original_file}' does not exist."
        if not os.path.exists(modified_file):
            return f"Error: Modified file '{modified_file}' does not exist."
        
        # Load files
        with open(original_file, 'r', encoding='utf-8') as f:
            original_code = f.read()
        with open(modified_file, 'r', encoding='utf-8') as f:
            modified_code = f.read()
        
        # Initialize workflow
        workflow = create_ast_analysis_workflow()
        
        # Create initial state
        initial_state = ASTAnalysisState(
            original_code=original_code,
            modified_code=modified_code,
            original_ast=None,
            modified_ast=None,
            structural_changes={},
            pattern_insights={},
            learning_summary={},
            analysis_history=[],
            final_report=None
        )
        
        # Run workflow
        result = workflow.invoke(initial_state)
        
        return result['final_report']
        
    except Exception as e:
        return f'Analysis workflow failed: {str(e)}'


