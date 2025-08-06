# import streamlit as st
# import os
# import sys
# import tempfile
# from datetime import datetime
# import json

# # Add the project root to the path

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from Agent.generator import workflow, CodeGenerationState
# from Difference_Analyzer.analyzer import analyze_with_ast_workflow

# # Page configuration
# st.set_page_config(
#     page_title="Code Generation & Analysis Tool",
#     page_icon="🚀",
#     layout="wide"
# )

# # Initialize session state
# if 'generated_code' not in st.session_state:
#     st.session_state.generated_code = None
# if 'generated_file_path' not in st.session_state:
#     st.session_state.generated_file_path = None
# if 'analysis_report' not in st.session_state:
#     st.session_state.analysis_report = None

# def main():
#     st.title("🚀 Code Generation & Analysis Tool")
#     st.markdown("---")
    
#     # Sidebar for navigation
#     st.sidebar.title("Navigation")
#     page = st.sidebar.radio(
#         "Choose a step:",
#         ["1. Generate Code", "2. Upload Updated Code", "3. View Analysis Report"]
#     )
    
#     if page == "1. Generate Code":
#         generate_code_page()
#     elif page == "2. Upload Updated Code":
#         upload_code_page()
#     elif page == "3. View Analysis Report":
#         view_report_page()

# def generate_code_page():
#     st.header("📝 Step 1: Generate Code")
#     st.markdown("Enter your query to generate Python code.")
    
#     # User input
#     user_query = st.text_area(
#         "What would you like to create?",
#         placeholder="e.g., Create a function to calculate fibonacci numbers",
#         height=100
#     )
    
#     if st.button("🚀 Generate Code", type="primary"):
#         if user_query.strip():
#             with st.spinner("Generating code..."):
#                 try:
#                     # Initialize the workflow state
#                     initial_state = CodeGenerationState(
#                         user_query=user_query,
#                         generated_code='',
#                         complexity_status='complex',
#                         feedback='',
#                         loop_count=0,
#                         conversation_history=[],
#                         final_code=None
#                     )
                    
#                     # Run the workflow
#                     response = workflow.invoke(initial_state)
#                     final_code = response.get('final_code')
                    
#                     if final_code:
#                         # Save to temporary file
#                         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#                         temp_file = f"generated_code_{timestamp}.py"
                        
#                         with open(temp_file, 'w') as f:
#                             f.write(final_code)
                        
#                         # Store in session state
#                         st.session_state.generated_code = final_code
#                         st.session_state.generated_file_path = temp_file
                        
#                         st.success("✅ Code generated successfully!")
                        
#                         # Display the generated code
#                         st.subheader("Generated Code:")
#                         st.code(final_code, language='python')
                        
#                         # Download button
#                         st.download_button(
#                             label="📥 Download Generated Code",
#                             data=final_code,
#                             file_name=temp_file,
#                             mime="text/plain"
#                         )
                        
#                     else:
#                         st.error("❌ Code generation failed. Please try again.")
                        
#                 except Exception as e:
#                     st.error(f"❌ Error during code generation: {str(e)}")
#         else:
#             st.warning("⚠️ Please enter a query to generate code.")

# def upload_code_page():
#     st.header("📤 Step 2: Upload Updated Code")
    
#     if st.session_state.generated_code is None:
#         st.warning("⚠️ Please generate code first in Step 1.")
#         return
    
#     st.markdown("Upload your modified version of the generated code for analysis.")
    
#     # Display original generated code
#     with st.expander("📋 Original Generated Code"):
#         st.code(st.session_state.generated_code, language='python')
    
#     # File upload
#     uploaded_file = st.file_uploader(
#         "Choose your updated Python file",
#         type=['py'],
#         help="Upload your modified version of the generated code"
#     )
    
#     if uploaded_file is not None:
#         # Read uploaded file
#         updated_code = uploaded_file.read().decode('utf-8')
        
#         st.subheader("📝 Your Updated Code:")
#         st.code(updated_code, language='python')
        
#         if st.button("🔍 Analyze Changes", type="primary"):
#             with st.spinner("Analyzing code changes..."):
#                 try:
#                     # Save uploaded code to temporary file
#                     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#                     updated_file_path = f"updated_code_{timestamp}.py"
                    
#                     with open(updated_file_path, 'w') as f:
#                         f.write(updated_code)
                    
#                     # Run analysis
#                     report = analyze_with_ast_workflow(
#                         st.session_state.generated_file_path,
#                         updated_file_path
#                     )
                    
#                     # Store report in session state
#                     st.session_state.analysis_report = report
                    
#                     st.success("✅ Analysis completed!")
#                     st.info("📊 Check the 'View Analysis Report' tab to see the results.")
                    
#                     # Clean up temporary files
#                     try:
#                         os.remove(updated_file_path)
#                     except:
#                         pass
                        
#                 except Exception as e:
#                     st.error(f"❌ Error during analysis: {str(e)}")

# def view_report_page():
#     st.header("📊 Step 3: Analysis Report")
    
#     if st.session_state.analysis_report is None:
#         st.info("ℹ️ No analysis report available. Please complete Steps 1 and 2 first.")
#         return
    
#     st.markdown("### 🔍 Code Analysis Results")
    
#     # Display the report
#     st.text_area(
#         "Analysis Report",
#         value=st.session_state.analysis_report,
#         height=400,
#         disabled=True
#     )
    
#     # Download report
#     st.download_button(
#         label="📥 Download Analysis Report",
#         data=st.session_state.analysis_report,
#         file_name=f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
#         mime="text/plain"
#     )
    
#     # Reset button
#     if st.button("🔄 Start New Analysis"):
#         st.session_state.generated_code = None
#         st.session_state.generated_file_path = None
#         st.session_state.analysis_report = None
#         st.rerun()

# # Cleanup function to remove temporary files
# def cleanup_temp_files():
#     """Clean up temporary files on app shutdown"""
#     try:
#         if st.session_state.generated_file_path and os.path.exists(st.session_state.generated_file_path):
#             os.remove(st.session_state.generated_file_path)
#     except:
#         pass

# # Main execution
# if __name__ == "__main__":
#     try:
#         main()
#     finally:
#         cleanup_temp_files()



import streamlit as st
import os
import sys
import tempfile
from datetime import datetime
import json

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Agent.generator import workflow, CodeGenerationState
from Difference_Analyzer.analyzer import analyze_with_ast_workflow

# Page configuration
st.set_page_config(
    page_title="Code Generation & Analysis Tool",
    page_icon="🚀",
    layout="wide"
)

# Create a dedicated directory for generated files
GENERATED_FILES_DIR = "generated_files"
os.makedirs(GENERATED_FILES_DIR, exist_ok=True)

# Initialize session state with better file management
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = None
if 'generated_file_path' not in st.session_state:
    st.session_state.generated_file_path = None
if 'updated_file_path' not in st.session_state:
    st.session_state.updated_file_path = None
if 'analysis_report' not in st.session_state:
    st.session_state.analysis_report = None
if 'session_id' not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

def main():
    st.title("🚀 Code Generation & Analysis Tool")
    st.markdown("---")
    
    # Display current session info
    st.sidebar.title("Navigation")
    st.sidebar.info(f"Session ID: {st.session_state.session_id}")
    
    # Show file status
    if st.session_state.generated_file_path:
        st.sidebar.success("✅ Generated code ready")
    if st.session_state.updated_file_path:
        st.sidebar.success("✅ Updated code ready")
    if st.session_state.analysis_report:
        st.sidebar.success("✅ Report ready")
    
    page = st.sidebar.radio(
        "Choose a step:",
        ["1. Generate Code", "2. Upload Updated Code", "3. View Analysis Report"]
    )
    
    if page == "1. Generate Code":
        generate_code_page()
    elif page == "2. Upload Updated Code":
        upload_code_page()
    elif page == "3. View Analysis Report":
        view_report_page()

def generate_code_page():
    st.header("📝 Step 1: Generate Code")
    st.markdown("Enter your query to generate Python code.")
    
    # User input
    user_query = st.text_area(
        "What would you like to create?",
        placeholder="e.g., Create a function to calculate fibonacci numbers",
        height=100
    )
    
    if st.button("🚀 Generate Code", type="primary"):
        if user_query.strip():
            with st.spinner("Generating code..."):
                try:
                    # Initialize the workflow state
                    initial_state = CodeGenerationState(
                        user_query=user_query,
                        generated_code='',
                        complexity_status='complex',
                        feedback='',
                        loop_count=0,
                        conversation_history=[],
                        final_code=None
                    )
                    
                    # Run the workflow
                    response = workflow.invoke(initial_state)
                    final_code = response.get('final_code')
                    
                    if final_code:
                        # Create a persistent file path using session ID
                        generated_filename = f"generated_code_{st.session_state.session_id}.py"
                        generated_file_path = os.path.join(GENERATED_FILES_DIR, generated_filename)
                        
                        # Save the generated code
                        with open(generated_file_path, 'w', encoding='utf-8') as f:
                            f.write(final_code)
                        
                        # Store in session state
                        st.session_state.generated_code = final_code
                        st.session_state.generated_file_path = generated_file_path
                        
                        st.success(f"✅ Code generated successfully!")
                        st.info(f"📁 Saved to: {generated_file_path}")
                        
                        # Display the generated code
                        st.subheader("Generated Code:")
                        st.code(final_code, language='python')
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Generated Code",
                            data=final_code,
                            file_name=generated_filename,
                            mime="text/plain"
                        )
                        
                    else:
                        st.error("❌ Code generation failed. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error during code generation: {str(e)}")
                    st.write("Debug info:", str(e))
        else:
            st.warning("⚠️ Please enter a query to generate code.")

def upload_code_page():
    st.header("📤 Step 2: Upload Updated Code")
    
    if st.session_state.generated_code is None:
        st.warning("⚠️ Please generate code first in Step 1.")
        return
    
    st.markdown("Upload your modified version of the generated code for analysis.")
    
    # Display current file status
    if st.session_state.generated_file_path:
        if os.path.exists(st.session_state.generated_file_path):
            st.success(f"✅ Original generated file: {st.session_state.generated_file_path}")
        else:
            st.error(f"❌ Original file not found: {st.session_state.generated_file_path}")
    
    # Display original generated code
    with st.expander("📋 Original Generated Code"):
        st.code(st.session_state.generated_code, language='python')
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose your updated Python file",
        type=['py'],
        help="Upload your modified version of the generated code"
    )
    
    if uploaded_file is not None:
        # Read uploaded file
        updated_code = uploaded_file.read().decode('utf-8')
        
        st.subheader("📝 Your Updated Code:")
        st.code(updated_code, language='python')
        
        # Save updated code immediately when uploaded
        updated_filename = f"updated_code_{st.session_state.session_id}.py"
        updated_file_path = os.path.join(GENERATED_FILES_DIR, updated_filename)
        
        with open(updated_file_path, 'w', encoding='utf-8') as f:
            f.write(updated_code)
        
        st.session_state.updated_file_path = updated_file_path
        st.info(f"📁 Updated code saved to: {updated_file_path}")
        
        if st.button("🔍 Analyze Changes", type="primary"):
            with st.spinner("Analyzing code changes..."):
                try:
                    # Verify both files exist
                    if not os.path.exists(st.session_state.generated_file_path):
                        st.error(f"❌ Generated file not found: {st.session_state.generated_file_path}")
                        return
                    
                    if not os.path.exists(updated_file_path):
                        st.error(f"❌ Updated file not found: {updated_file_path}")
                        return
                    
                    # Run analysis
                    report = analyze_with_ast_workflow(
                        st.session_state.generated_file_path,
                        updated_file_path
                    )
                    
                    # Store report in session state
                    st.session_state.analysis_report = report
                    
                    st.success("✅ Analysis completed!")
                    st.info("📊 Check the 'View Analysis Report' tab to see the results.")
                        
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                    st.write("Debug info:")
                    st.write(f"Generated file: {st.session_state.generated_file_path}")
                    st.write(f"Updated file: {updated_file_path}")
                    st.write(f"Error: {str(e)}")

def view_report_page():
    st.header("📊 Step 3: Analysis Report")
    
    if st.session_state.analysis_report is None:
        st.info("ℹ️ No analysis report available. Please complete Steps 1 and 2 first.")
        return
    
    st.markdown("### 🔍 Code Analysis Results")
    
    # Display file paths used in analysis
    st.info(f"📁 Generated file: {st.session_state.generated_file_path}")
    st.info(f"📁 Updated file: {st.session_state.updated_file_path}")
    
    # Display the report
    st.text_area(
        "Analysis Report",
        value=st.session_state.analysis_report,
        height=400,
        disabled=True
    )
    
    # Download report
    report_filename = f"analysis_report_{st.session_state.session_id}.txt"
    st.download_button(
        label="📥 Download Analysis Report",
        data=st.session_state.analysis_report,
        file_name=report_filename,
        mime="text/plain"
    )
    
    # Reset button
    if st.button("🔄 Start New Analysis"):
        # Clean up old files
        cleanup_session_files()
        # Reset session state
        st.session_state.generated_code = None
        st.session_state.generated_file_path = None
        st.session_state.updated_file_path = None
        st.session_state.analysis_report = None
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.rerun()

def cleanup_session_files():
    """Clean up files from current session"""
    try:
        if st.session_state.generated_file_path and os.path.exists(st.session_state.generated_file_path):
            os.remove(st.session_state.generated_file_path)
        if st.session_state.updated_file_path and os.path.exists(st.session_state.updated_file_path):
            os.remove(st.session_state.updated_file_path)
    except Exception as e:
        st.warning(f"Could not clean up some files: {e}")

# Main execution
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {e}")
        st.write("Debug info:", str(e))