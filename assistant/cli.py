from assistant.parser import CommandParser
from assistant.executor import CommandExecutor


class CLIInterface:

    def __init__(self):

        self.parser = CommandParser()
        self.executor = CommandExecutor()

    def start(self):

        print("Jarvis CLI Assistant")
        print("Type 'exit' to quit\n")

        while True:

            command = input("jarvis> ")

            if command == "exit":
                print("Goodbye")
                break

            intent, value = self.parser.parse(command)

            self.executor.execute(intent, value)