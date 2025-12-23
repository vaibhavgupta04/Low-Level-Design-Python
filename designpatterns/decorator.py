from abc import ABC, abstractmethod

# Component
class Coffee(ABC):
    @abstractmethod
    def cost(self) -> int:
        raise NotImplementedError

# Concrete Component
class BasicCoffee(Coffee):
    def cost(self) -> int:
        return 50

# Decorator Base
class CoffeeDecorator(Coffee):
    def __init__(self, coffee: Coffee):
        self.coffee = coffee

    def cost(self) -> int:
        return self.coffee.cost()

# Concrete Decorators
class MilkDecorator(CoffeeDecorator):
    def cost(self) -> int:
        return self.coffee.cost() + 20

class SugarDecorator(CoffeeDecorator):
    def cost(self) -> int:
        return self.coffee.cost() + 10


# ---------- Usage ----------
if __name__ == "__main__":
    coffee = BasicCoffee()
    print("Basic Coffee:", coffee.cost())

    coffee = MilkDecorator(coffee)
    print("With Milk:", coffee.cost())

    coffee = SugarDecorator(coffee)
    print("With Milk + Sugar:", coffee.cost())
