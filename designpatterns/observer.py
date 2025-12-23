from abc import ABC, abstractmethod

# Observer Interface
class Observer(ABC):
    @abstractmethod
    def update(self, temperature):
        pass

# Subject
class WeatherStation:
    def __init__(self):
        self.observers = []
        self.temperature = 0

    def add_observer(self, observer: Observer):
        self.observers.append(observer)

    def remove_observer(self, observer: Observer):
        self.observers.remove(observer)

    def set_temperature(self, temp):
        self.temperature = temp
        self.notify_observers()

    def notify_observers(self):
        for obs in self.observers:
            obs.update(self.temperature)

# Concrete Observers
class PhoneDisplay(Observer):
    def update(self, temperature):
        print(f"[Phone] New temperature: {temperature}")

class TVDisplay(Observer):
    def update(self, temperature):
        print(f"[TV] New temperature: {temperature}")


# ---------- Usage ----------
if __name__ == "__main__":
    station = WeatherStation()

    phone = PhoneDisplay()
    tv = TVDisplay()

    station.add_observer(phone)
    station.add_observer(tv)

    station.set_temperature(30)
    station.set_temperature(35)
