class CommandParser:

    def __init__(self):

        self.commands = [
            "open",
            "shutdown",
            "close",
            "search"
        ]


    def parse(self, text):

        parts = text.split()

        if len(parts) == 0:
            return ("none", None)

        # CHANGED: accept natural command words from STT ("open ..."), while keeping "open_app" compatibility.
        if parts[0] in ("open", "open_app") and len(parts) > 1:
            return ("open_app", parts[1])

        if parts[0] == "shutdown":
            return ("shutdown", None)

        return ("unknown", text)
