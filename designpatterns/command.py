from abc import ABC, abstractmethod

# Command Interface
class Command(ABC):
    @abstractmethod
    def execute(self): pass

    @abstractmethod
    def undo(self): pass

# Receiver
class Light:
    def on(self):
        print("Light turned ON")

    def off(self):
        print("Light turned OFF")

# Concrete Commands
class LightOnCommand(Command):
    def __init__(self, light):
        self.light = light

    def execute(self):
        self.light.on()

    def undo(self):
        self.light.off()

class LightOffCommand(Command):
    def __init__(self, light):
        self.light = light

    def execute(self):
        self.light.off()

    def undo(self):
        self.light.on()

# Invoker
class RemoteControl:
    def __init__(self):
        self.history = []

    def submit(self, command: Command):
        command.execute()
        self.history.append(command)

    def undo(self):
        if self.history:
            command = self.history.pop()
            command.undo()


# ---------- Usage ----------
if __name__ == "__main__":
    remote = RemoteControl()
    light = Light()

    on_cmd = LightOnCommand(light)
    off_cmd = LightOffCommand(light)

    remote.submit(on_cmd)
    remote.submit(off_cmd)

    print("Undo last action:")
    remote.undo()
