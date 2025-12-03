from abc import ABC, abstractmethod

# Strategy Interface
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

# Concrete Strategies
class CreditCardPayment(PaymentStrategy):
    def pay(self, amount):
        return f"Paid {amount} using Credit Card"

class PayPalPayment(PaymentStrategy):
    def pay(self, amount):
        return f"Paid {amount} using PayPal"

class WalletPayment(PaymentStrategy):
    def pay(self, amount):
        return f"Paid {amount} using Wallet"

# Context
class PaymentProcessor:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: PaymentStrategy):
        self.strategy = strategy

    def pay(self, amount):
        return self.strategy.pay(amount)


# ---------- Usage ----------
if __name__ == "__main__":
    processor = PaymentProcessor(CreditCardPayment())
    print(processor.pay(100))

    processor.set_strategy(PayPalPayment())
    print(processor.pay(200))


