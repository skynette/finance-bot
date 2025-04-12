from fastapi import HTTPException

class CommandParser:
    @staticmethod
    def parse_command(text: str) -> dict:
        if not text or not text.startswith("/"):
            raise HTTPException(status_code=400, detail="Invalid command format")

        parts = text.strip().split()
        command = parts[0]
        args = parts[1:]

        return {
            "command": command,
            "args": args
        }
