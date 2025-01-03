from dotenv import load_dotenv
import os

load_dotenv()

class InternalData:
    """Class to handle internal data using environment variables."""

    def __init__(self) -> None:
        pass

    def set_ip(self, key: str, value: str) -> None:
        """Set IP address in environment variables and .env file.

        Args:
            key (str): The environment variable key.
            value (str): The IP address value to set.
        """
        os.environ[key] = value
        try:
            with open("assets/.env", "r") as file:
                lines = file.readlines()

            with open("assets/.env", "w") as file:
                for line in lines:
                    if line.startswith(f"{key}="):
                        file.write(f"{key}={value}\n")
                    else:
                        file.write(line)
        except Exception as e:
            print(f"Exception {e}")

    def get_host(self) -> str:
        """Get IP address from environment variables.

        Returns:
            str: The IP address.
        """
        return os.getenv("IP_ADDRESS", "0.0.0.0")

    def get_port(self) -> int:
        """Get port number from environment variables.

        Returns:
            int: The port number.
        """
        return int(os.getenv("PORT", "9999"))
    
    def get_counter(self) -> int:
        """Get counter value from environment variables.

        Returns:
            int: The counter value.
        """
        return int(os.getenv("COUNTER", "0"))
