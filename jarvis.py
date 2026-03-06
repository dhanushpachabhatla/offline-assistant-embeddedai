import sys
from assistant.parser import CommandParser
from assistant.executor import CommandExecutor
from assistant.cli import CLIInterface


def main():

    parser = CommandParser()
    executor = CommandExecutor()

    # If arguments provided → direct command
    if len(sys.argv) > 1:

        command = " ".join(sys.argv[1:])
        intent, value = parser.parse(command)

        executor.execute(intent, value)

    # Otherwise open interactive CLI
    else:

        cli = CLIInterface()
        cli.start()


if __name__ == "__main__":
    main()