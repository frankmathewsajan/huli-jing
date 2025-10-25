import secrets
import string

def H(length: int = 10) -> str:
    # Define the character set: hex digits or full alphanumerics
    charset = string.ascii_letters + string.digits  # For full alphanumeric
    # charset = string.hexdigits.lower()  # For hex-style hash
    return ''.join(secrets.choice(charset) for _ in range(length))

# Example usage
print(H(10))