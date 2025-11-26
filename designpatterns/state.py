from abc import ABC, abstractmethod

# State Interface
class FanState(ABC):
    @abstractmethod
    def next_state(self, fan):
        pass

    @abstractmethod
    def get_state(self):
        pass

# Concrete States
class FanOff(FanState):
    def next_state(self, fan):
        fan.state = FanLow()

    def get_state(self):
        return "Fan is OFF"

class FanLow(FanState):
    def next_state(self, fan):
        fan.state = FanHigh()

    def get_state(self):
        return "Fan speed: LOW"

class FanHigh(FanState):
    def next_state(self, fan):
        fan.state = FanOff()

    def get_state(self):
        return "Fan speed: HIGH"

# Context
class Fan:
    def __init__(self):
        self.state = FanOff()

    def press_button(self):
        self.state.next_state(self)

    def status(self):
        return self.state.get_state()


# ---------- Usage ----------
if __name__ == "__main__":
    fan = Fan()

    print(fan.status())
    fan.press_button()

    print(fan.status())
    fan.press_button()

    print(fan.status())
    fan.press_button()

    print(fan.status())
