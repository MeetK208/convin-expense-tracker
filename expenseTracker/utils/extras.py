import re
from .logger import setup_console_logger

logger = setup_console_logger()
def is_valid_email(email):
    """Check if the email is in a valid format."""
    # Regular expression for validating an Email
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    # If the string matches the regex, it is a valid email
    if re.match(regex, email):
        logger.info(f"E-mail is Valid {email}.")
        return True
    else:
        logger.WARNING(f"E-mail is Not-Valid Please Check E-mail {email}.")
        return False
