import subprocess
import os


class CommandExecutor:

    def __init__(self):

        self.apps = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            # CHANGED: support Brave across common install locations and command fallback.
            "brave": [
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
                "brave",
            ],
            "vscode": "code",
            "notepad": "notepad"
        }

    def execute(self, intent, value):

        if intent == "open_app":

            if value in self.apps:

                print("Opening", value)

                app_target = self.apps[value]  # CHANGED: handle single command/path or multi-candidate list.

                # CHANGED: pick first valid Brave executable path, then fallback to command.
                if isinstance(app_target, list):
                    for candidate in app_target:
                        if os.path.exists(candidate):
                            subprocess.Popen(candidate)
                            return
                    if os.system('start "" brave') == 0:
                        return
                    print("App not found")
                    return

                # CHANGED: keep normal open behavior for non-list apps.
                try:
                    subprocess.Popen(app_target)
                except FileNotFoundError:
                    print("App not found")

            else:
                print("App not found")

        elif intent == "shutdown":

            print("Shutting down")

            os.system("shutdown /s /t 1")

        else:

            print("Unknown command")
