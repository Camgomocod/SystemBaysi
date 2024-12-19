from dotenv import load_dotenv
import os

load_dotenv()


class InternalData:
    def __init__(self) -> None:
        pass

    def set_ip(self, key: str, value: str) -> None:
        os.environ[key] = value
        try:
            with open("/asssets/.env", "r") as file:
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
        return os.getenv("IP_ADDRESS", "0.0.0.0")

    def get_port(self) -> int:
        return int(os.getenv("PORT", "9999"))
    
    def get_counter(self) -> int:
        return int(os.getenv("COUNTER", "0"))