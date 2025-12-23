from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict
import uuid
import threading

# --- 1. ENUMS & CONSTANTS ---
class OrderStatus(Enum):
    CREATED = "CREATED"
    PENDING_PAYMENT = "PENDING_PAYMENT"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"

# --- 2. CORE ENTITIES ---
class Product:
    def __init__(self, name: str, price: float, category: str):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.price = price
        self.category = category

    def __repr__(self):
        return f"{self.name} (${self.price})"

class User:
    def __init__(self, name: str, email: str):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.email = email

# --- 3. SINGLETON PATTERN: INVENTORY MANAGEMENT ---
# Why? We need one single source of truth for stock levels across the system.
class Inventory:
    _instance = None
    _lock = threading.Lock()
    products: Dict[str, int] = {}

    def __init__(self):
        if Inventory._instance is not None:
            raise Exception("This class is a singleton!")
        self.products = {}

    @staticmethod
    def get_instance():
        if Inventory._instance is None:
            with Inventory._lock:
                if Inventory._instance is None:
                    Inventory._instance = Inventory()
        return Inventory._instance

    def add_stock(self, product: Product, quantity: int):
        if product.id in self.products:
            self.products[product.id] += quantity
        else:
            self.products[product.id] = quantity
        print(f"[Inventory] Added {quantity} of {product.name}. Total: {self.products[product.id]}")

    def check_stock(self, product_id: str, quantity: int) -> bool:
        return self.products.get(product_id, 0) >= quantity

    def reduce_stock(self, product_id: str, quantity: int):
        if self.check_stock(product_id, quantity):
            self.products[product_id] -= quantity
            return True
        return False

# --- 4. STRATEGY PATTERN: DISCOUNTS ---
# Why? We want to swap discount logic (Flat rate, Percentage, Seasonal) easily.
class DiscountStrategy(ABC):
    @abstractmethod
    def apply_discount(self, total_amount: float) -> float:
        pass

class NoDiscount(DiscountStrategy):
    def apply_discount(self, total_amount: float) -> float:
        return total_amount

class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage: float):
        self.percentage = percentage

    def apply_discount(self, total_amount: float) -> float:
        return total_amount - (total_amount * (self.percentage / 100))

# --- 5. FACTORY PATTERN: PAYMENTS ---
# Why? Decouple payment processing logic from the order flow.
class PaymentProcessor(ABC):
    @abstractmethod
    def pay(self, amount: float):
        pass

class CreditCardPayment(PaymentProcessor):
    def pay(self, amount: float):
        print(f"Processing Credit Card payment of ${amount:.2f}...")
        return True

class PayPalPayment(PaymentProcessor):
    def pay(self, amount: float):
        print(f"Redirecting to PayPal for payment of ${amount:.2f}...")
        return True

class PaymentFactory:
    @staticmethod
    def get_payment_method(method_type: str) -> PaymentProcessor:
        if method_type == "CREDIT_CARD":
            return CreditCardPayment()
        elif method_type == "PAYPAL":
            return PayPalPayment()
        raise ValueError("Unknown payment method")

# --- 6. OBSERVER PATTERN: NOTIFICATIONS ---
# Why? Automatically notify user when Order state changes.
class Observer(ABC):
    @abstractmethod
    def update(self, order):
        pass

class EmailNotificationService(Observer):
    def update(self, order):
        print(f"--- [Email Alert] Sending email to {order.user.email}: Order {order.id} is now {order.status.value} ---")

class SMSNotificationService(Observer):
    def update(self, order):
        print(f"--- [SMS Alert] Sending SMS to {order.user.name}: Order status {order.status.value} ---")

# --- 7. COMPLEX ENTITY: SHOPPING CART & ORDER ---
class CartItem:
    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = quantity

class ShoppingCart:
    def __init__(self):
        self.items: List[CartItem] = []

    def add_item(self, product: Product, quantity: int):
        self.items.append(CartItem(product, quantity))

    def calculate_total(self) -> float:
        return sum(item.product.price * item.quantity for item in self.items)

class Order:
    def __init__(self, user: User, cart: ShoppingCart, discount_strategy: DiscountStrategy = NoDiscount()):
        self.id = str(uuid.uuid4())[:8]
        self.user = user
        self.items = cart.items
        self.status = OrderStatus.CREATED
        self.discount_strategy = discount_strategy
        self.observers: List[Observer] = []
        
        # Calculate pricing immediately
        raw_total = cart.calculate_total()
        self.final_amount = self.discount_strategy.apply_discount(raw_total)

    # Observer Management
    def attach(self, observer: Observer):
        self.observers.append(observer)

    def set_status(self, new_status: OrderStatus):
        self.status = new_status
        self.notify_observers()

    def notify_observers(self):
        for observer in self.observers:
            observer.update(self)

    def process_order(self, payment_method_str: str):
        inventory = Inventory.get_instance() # Get Singleton instance
        
        # 1. Validate Stock
        print(f"\nProcessing Order {self.id} for {self.user.name}...")
        for item in self.items:
            if not inventory.check_stock(item.product.id, item.quantity):
                print(f"Error: Out of stock for {item.product.name}")
                return False
        
        # 2. Reduce Stock
        for item in self.items:
            inventory.reduce_stock(item.product.id, item.quantity)
            
        self.set_status(OrderStatus.PENDING_PAYMENT)
        
        # 3. Process Payment
        payment_processor = PaymentFactory.get_payment_method(payment_method_str)
        if payment_processor.pay(self.final_amount):
            self.set_status(OrderStatus.PAID)
            print("Payment Successful.")
            
            # Simulate shipping
            self.set_status(OrderStatus.SHIPPED)
        else:
            print("Payment Failed.")

# --- 8. DEMO CLASS (RUNNING THE SYSTEM) ---
class ECommerceDemo:
    @staticmethod
    def main():
        # A. Setup Inventory
        inventory = Inventory.get_instance()
        laptop = Product("MacBook Pro", 2000.0, "Electronics")
        mouse = Product("Logitech Mouse", 50.0, "Electronics")
        
        inventory.add_stock(laptop, 10)
        inventory.add_stock(mouse, 50)
        
        # B. User interacts
        print("\n--- User 1: Alice ---")
        user1 = User("Alice", "alice@example.com")
        cart1 = ShoppingCart()
        cart1.add_item(laptop, 1) # Buy 1 Laptop
        cart1.add_item(mouse, 2)  # Buy 2 Mice
        
        # C. Create Order with a Strategy (10% Discount)
        # Applying Black Friday Deal
        discount_strategy = PercentageDiscount(10.0) 
        order1 = Order(user1, cart1, discount_strategy)
        
        # D. Attach Observers (Notification Services)
        email_service = EmailNotificationService()
        sms_service = SMSNotificationService()
        order1.attach(email_service)
        order1.attach(sms_service)
        
        # E. Process the Order
        print(f"Total Amount to Pay (after 10% discount): ${order1.final_amount:.2f}")
        
        # User chooses Credit Card
        order1.process_order("CREDIT_CARD")
        
        # F. Second order without discount
        print("\n--- User 2: Bob ---")
        user2 = User("Bob", "bob@example.com")
        cart2 = ShoppingCart()
        cart2.add_item(mouse, 1)
        
        order2 = Order(user2, cart2, NoDiscount())
        order2.attach(email_service)
        print(f"Total Amount to Pay (no discount): ${order2.final_amount:.2f}")
        order2.process_order("PAYPAL")


if __name__ == "__main__":
    ECommerceDemo.main()