def clean_code_output(code: str) -> str:
    """
    Removes markdown code block markers from the generated code.
    
    Args:
        code (str): Code that may contain markdown code block markers
        
    Returns:
        str: Clean code without markdown markers
    """
    # Remove ```python at the beginning
    if code.startswith('```python'):
        code = code[9:]  # Remove '```python'
    elif code.startswith('```'):
        code = code[3:]   # Remove '```'
    
    # Remove ``` at the end
    if code.endswith('```'):
        code = code[:-3]
    
    # Remove leading/trailing whitespace
    return code.strip() 