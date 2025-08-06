import os
import sys
import subprocess
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime
from fastapi.responses import JSONResponse
import uuid

# Add the project root to the path
sys.path.append(os.path.abspath('.'))

# Import after path setup
from Agent.generator import workflow, CodeGenerationState
from Difference_Analyzer.analyzer import analyze_with_ast_workflow

# FastAPI app
app = FastAPI(title="Code Generation & Analysis API", version="1.0.0")

# Create a dedicated directory for generated files
GENERATED_FILES_DIR = "generated_files"
os.makedirs(GENERATED_FILES_DIR, exist_ok=True)

class UserInput(BaseModel):
    query: Annotated[str, Field(..., description='What you want to generate?')]
    session_id: Annotated[str, Field(default_factory=lambda: str(uuid.uuid4()), description='Unique session identifier')]

class ReportRequest(BaseModel):
    original_file: str = Field(..., description='Path to the original generated code file')
    updated_file: str = Field(..., description='Path to the updated code file')

class CodeUploadRequest(BaseModel):
    session_id: str = Field(..., description='Session ID from code generation')
    updated_code: str = Field(..., description='Updated code content')

@app.post("/GenerateCode")
def generate_code(Query: UserInput):
    """Generate Python code based on user query"""
    initial_state = CodeGenerationState(
        user_query=Query.query,
        generated_code='',
        complexity_status='complex', # Start as complex to ensure initial check
        feedback='',
        loop_count=0,
        conversation_history=[],
        final_code=None
    )
    try:
        response = workflow.invoke(initial_state)
        final_code = response.get('final_code')
        
        if final_code:
            # Generate a consistent filename using session ID
            generated_filename = f"generated_code_{Query.session_id}.py"
            output_file = os.path.join(GENERATED_FILES_DIR, generated_filename)
            
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(final_code)
            except IOError as e:
                raise HTTPException(status_code=500, detail=f"Error saving file '{output_file}': {e}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"An unexpected error occurred during file saving: {e}")
            
            return {
                "session_id": Query.session_id,
                "file_path": output_file,
                "code": final_code,
                "message": f"Code generated successfully and saved to {output_file}"
            }
        else:
            return JSONResponse(status_code=200, content={
                "session_id": Query.session_id,
                "message": "Code generation completed, but no final code was produced. This might indicate an issue with the workflow.",
                "conversation_history": [
                    {"type": getattr(msg, 'type', 'unknown'), "content": getattr(msg, 'content', str(msg))} 
                    for msg in response.get('conversation_history', [])
                ]
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during code generation workflow: {e}")

@app.post("/UploadUpdatedCode")
def upload_updated_code(request: CodeUploadRequest):
    """Upload updated code for a specific session"""
    try:
        # Check if original generated file exists
        original_file = os.path.join(GENERATED_FILES_DIR, f"generated_code_{request.session_id}.py")
        if not os.path.exists(original_file):
            raise HTTPException(status_code=404, detail=f"Original generated file not found for session {request.session_id}")
        
        # Save updated code
        updated_filename = f"updated_code_{request.session_id}.py"
        updated_file = os.path.join(GENERATED_FILES_DIR, updated_filename)
        
        with open(updated_file, 'w', encoding='utf-8') as f:
            f.write(request.updated_code)
        
        return {
            "session_id": request.session_id,
            "updated_file_path": updated_file,
            "original_file_path": original_file,
            "message": "Updated code saved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving updated code: {e}")

@app.post("/GenerateReport")
def generate_report_by_session(session_id: str):
    """Generate analysis report for a specific session"""
    try:
        # Construct file paths based on session ID
        original_file = os.path.join(GENERATED_FILES_DIR, f"generated_code_{session_id}.py")
        updated_file = os.path.join(GENERATED_FILES_DIR, f"updated_code_{session_id}.py")
        
        # Check if files exist
        if not os.path.exists(original_file):
            raise HTTPException(status_code=404, detail=f"Original generated file not found for session {session_id}")
        if not os.path.exists(updated_file):
            raise HTTPException(status_code=404, detail=f"Updated file not found for session {session_id}")
        
        # Generate report
        report = analyze_with_ast_workflow(original_file, updated_file)
        
        return {
            "session_id": session_id,
            "report": report,
            "original_file": original_file,
            "updated_file": updated_file,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while generating report: {e}")

@app.post("/ReportCreation")
def report_creation(request: ReportRequest):
    """Generate analysis report comparing original and updated code (legacy endpoint)"""
    try:
        # Check if files exist
        if not os.path.exists(request.original_file):
            raise HTTPException(status_code=404, detail=f"Original file '{request.original_file}' not found")
        if not os.path.exists(request.updated_file):
            raise HTTPException(status_code=404, detail=f"Updated file '{request.updated_file}' not found")
        
        # Generate report
        report = analyze_with_ast_workflow(request.original_file, request.updated_file)
        
        return {
            "report": report,
            "original_file": request.original_file,
            "updated_file": request.updated_file,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while generating report: {e}")

@app.get("/session/{session_id}/files")
def get_session_files(session_id: str):
    """Get information about files for a specific session"""
    original_file = os.path.join(GENERATED_FILES_DIR, f"generated_code_{session_id}.py")
    updated_file = os.path.join(GENERATED_FILES_DIR, f"updated_code_{session_id}.py")
    
    return {
        "session_id": session_id,
        "files": {
            "original": {
                "path": original_file,
                "exists": os.path.exists(original_file)
            },
            "updated": {
                "path": updated_file,
                "exists": os.path.exists(updated_file)
            }
        }
    }

@app.delete("/session/{session_id}")
def cleanup_session(session_id: str):
    """Clean up files for a specific session"""
    original_file = os.path.join(GENERATED_FILES_DIR, f"generated_code_{session_id}.py")
    updated_file = os.path.join(GENERATED_FILES_DIR, f"updated_code_{session_id}.py")
    
    removed_files = []
    
    try:
        if os.path.exists(original_file):
            os.remove(original_file)
            removed_files.append(original_file)
        if os.path.exists(updated_file):
            os.remove(updated_file)
            removed_files.append(updated_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up session files: {e}")
    
    return {
        "session_id": session_id,
        "removed_files": removed_files,
        "message": f"Cleaned up {len(removed_files)} files"
    }

@app.get("/")
def root():
    """API root endpoint"""
    return {
        "message": "Code Generation & Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "generate_code": "/GenerateCode",
            "upload_updated_code": "/UploadUpdatedCode",
            "generate_report_by_session": "/GenerateReport/{session_id}",
            "create_report": "/ReportCreation",
            "get_session_files": "/session/{session_id}/files",
            "cleanup_session": "/session/{session_id}"
        }
    }

# Launcher functions (rest remains the same)
def run_streamlit_app():
    """Run the Streamlit application"""
    try:
        # Check if app.py exists
        if not os.path.exists('app.py'):
            print("❌ Error: app.py not found!")
            return
        
        print("🚀 Starting Code Generation & Analysis Tool...")
        print("📱 Opening Streamlit UI in your browser...")
        print("🔗 The app will be available at: http://localhost:8501")
        print("\n" + "="*50)
        
        # Run streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running Streamlit app: {e}")

def run_fastapi_server():
    """Run the FastAPI server"""
    try:
        print("🚀 Starting FastAPI server...")
        print("🔗 API will be available at: http://localhost:8000")
        print("📚 API documentation at: http://localhost:8000/docs")
        print("\n" + "="*50)
        
        subprocess.run([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error running FastAPI server: {e}")

def show_help():
    """Show help information"""
    print("🚀 Code Generation & Analysis Tool")
    print("="*50)
    print("\nUsage:")
    print("  python main.py --mode ui     # Run Streamlit UI (default)")
    print("  python main.py --mode api    # Run FastAPI server")
    print("  python main.py --help        # Show this help")
    print("\nModes:")
    print("  ui   - Interactive web interface using Streamlit")
    print("  api  - REST API server using FastAPI")
    print("\nExamples:")
    print("  python main.py               # Start Streamlit UI")
    print("  python main.py --mode api    # Start API server")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Code Generation & Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py               # Start Streamlit UI
  python main.py --mode api    # Start API server
        """
    )
    parser.add_argument(
        "--mode", 
        choices=["ui", "api"], 
        default="ui",
        help="Choose mode: 'ui' for Streamlit interface, 'api' for FastAPI server"
    )
    
    args = parser.parse_args()
    
    if args.mode == "ui":
        run_streamlit_app()
    elif args.mode == "api":
        run_fastapi_server()
    else:
        print("❌ Invalid mode. Use 'ui' or 'api'")
        show_help()

