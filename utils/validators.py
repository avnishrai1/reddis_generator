def validate_input(text, min_length=10, max_length=5000):

    if not text or not isinstance(text, str):
        return False, "Input must be a non-empty string"
    
    text = text.strip()
    
    if len(text) < min_length:
        return False, f"Input must be at least {min_length} characters"
    
    if len(text) > max_length:
        return False, f"Input must not exceed {max_length} characters"
    
    return True, "Valid"

def sanitize_input(text):

    if not text:
        return ""
    
    # Remove potentially dangerous characters
    text = text.strip()
    # Add more sanitization as needed
    
    return text