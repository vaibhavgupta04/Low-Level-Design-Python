from enum import Enum
from abc import ABC, abstractmethod
import threading
from typing import Dict, List, Optional
import uuid
import time


# =============================
# ENUMS
# =============================

class FoodType(Enum):
    VEG = "VEG"
    NONVEG = "NONVEG"


class OrderStatus(Enum):
    CREATED = "CREATED"
    ACCEPTED = "ACCEPTED"
    COOKING = "COOKING"
    READY = "READY"
    PICKED = "PICKED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


# =============================
# ENTITIES
# =============================

class FoodItem:
    def __init__(self, item_id: str, name: str, price: float, food_type: FoodType):
        self.item_id = item_id
        self.name = name
        self.price = price
        self.food_type = food_type


class Restaurant:
    def __init__(self, restaurant_id: str, name: str):
        self.restaurant_id = restaurant_id
        self.name = name
        self.menu: Dict[str, FoodItem] = {}

    def add_food_item(self, food: FoodItem):
        self.menu[food.item_id] = food

    def get_item(self, item_id: str) -> Optional[FoodItem]:
        return self.menu.get(item_id)


class Order:
    def __init__(self, user_id: str, restaurant: Restaurant, items: Dict[str, int]):
        self.order_id = str(uuid.uuid4())
        self.user_id = user_id
        self.restaurant = restaurant
        self.items = items  # item_id -> quantity
        self.status = OrderStatus.CREATED
        self.total_price = 0
        self.timestamp = int(time.time() * 1000)

    def calculate_total(self):
        total = 0
        for item_id, qty in self.items.items():
            food = self.restaurant.get_item(item_id)
            if food:
                total += food.price * qty
        self.total_price = total
        return total


# =============================
# PAYMENT STRATEGY
# =============================

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float):
        pass


class WalletPayment(PaymentStrategy):
    def pay(self, amount: float):
        print(f"[PAYMENT] Paid ₹{amount:.2f} using Wallet.")


class CardPayment(PaymentStrategy):
    def pay(self, amount: float):
        print(f"[PAYMENT] Charged card for ₹{amount:.2f}.")


class PaymentFactory:
    @staticmethod
    def get_payment(method: str) -> PaymentStrategy:
        method = method.upper()
        if method == "WALLET":
            return WalletPayment()
        elif method == "CARD":
            return CardPayment()
        else:
            raise Exception("Unsupported payment method")


# =============================
# DELIVERY STRATEGIES
# =============================

class DeliveryStrategy(ABC):
    @abstractmethod
    def assign_delivery_person(self, order: Order) -> str:
        pass


class FastestDelivery(DeliveryStrategy):
    def assign_delivery_person(self, order: Order) -> str:
        boy_id = f"FAST-{uuid.uuid4().hex[:6]}"
        print(f"[DELIVERY] Fastest delivery assigned: {boy_id}")
        return boy_id


class CheapestDelivery(DeliveryStrategy):
    def assign_delivery_person(self, order: Order) -> str:
        boy_id = f"CHEAP-{uuid.uuid4().hex[:6]}"
        print(f"[DELIVERY] Cheapest delivery assigned: {boy_id}")
        return boy_id


# =============================
# DELIVERY SYSTEM (SINGLETON)
# =============================

class DeliverySystem:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        if DeliverySystem._instance is not None:
            raise Exception("Singleton class!")
        self.restaurants: Dict[str, Restaurant] = {}
        self.orders: Dict[str, Order] = {}
        self.delivery_strategy: DeliveryStrategy = FastestDelivery()
        self._main_lock = threading.Lock()

    @staticmethod
    def get_instance():
        if DeliverySystem._instance is None:
            with DeliverySystem._lock:
                if DeliverySystem._instance is None:
                    DeliverySystem._instance = DeliverySystem()
        return DeliverySystem._instance

    def add_restaurant(self, restaurant: Restaurant):
        self.restaurants[restaurant.restaurant_id] = restaurant

    def set_delivery_strategy(self, strategy: DeliveryStrategy):
        self.delivery_strategy = strategy

    def place_order(self, user_id: str, restaurant_id: str, items: Dict[str, int], payment_method: str):
        with self._main_lock:
            restaurant = self.restaurants.get(restaurant_id)
            if not restaurant:
                print("[ERROR] Restaurant not found.")
                return None

            order = Order(user_id, restaurant, items)
            total_price = order.calculate_total()

            print(f"[ORDER] Order {order.order_id} created. Amount: ₹{total_price:.2f}")

            # Payment
            payment_obj = PaymentFactory.get_payment(payment_method)
            payment_obj.pay(total_price)

            order.status = OrderStatus.ACCEPTED
            print(f"[ORDER] Accepted by restaurant {restaurant.name}")

            time.sleep(0.2)
            order.status = OrderStatus.COOKING
            print("[ORDER] Cooking started...")

            time.sleep(0.2)
            order.status = OrderStatus.READY
            print("[ORDER] Food ready for pickup!")

            # Assign delivery
            delivery_person = self.delivery_strategy.assign_delivery_person(order)
            order.status = OrderStatus.PICKED
            print(f"[ORDER] Picked by {delivery_person}")

            time.sleep(0.2)
            order.status = OrderStatus.DELIVERED
            print("[ORDER] Delivered successfully!")

            self.orders[order.order_id] = order
            return order

    def cancel_order(self, order_id: str):
        with self._main_lock:
            order = self.orders.get(order_id)

            if not order:
                print("[ERROR] Invalid order id")
                return

            if order.status in (OrderStatus.DELIVERED, OrderStatus.CANCELLED):
                print("[ERROR] Cannot cancel (already delivered or cancelled)")
                return

            order.status = OrderStatus.CANCELLED
            print(f"[ORDER] Order {order_id} has been cancelled!")


# =============================
# DEMO
# =============================

class FoodDeliveryDemo:
    @staticmethod
    def main():
        system = DeliverySystem.get_instance()

        # Create Restaurants
        r1 = Restaurant("R1", "Dominos")
        r1.add_food_item(FoodItem("P1", "Pizza", 250, FoodType.VEG))
        r1.add_food_item(FoodItem("P2", "Chicken Pizza", 350, FoodType.NONVEG))

        r2 = Restaurant("R2", "KFC")
        r2.add_food_item(FoodItem("K1", "Zinger", 180, FoodType.NONVEG))
        r2.add_food_item(FoodItem("K2", "Fries", 80, FoodType.VEG))

        system.add_restaurant(r1)
        system.add_restaurant(r2)

        # Set delivery strategy
        system.set_delivery_strategy(CheapestDelivery())

        print("\n--- ORDER 1 ---")
        order1 = system.place_order(
            user_id="U1",
            restaurant_id="R1",
            items={"P1": 2, "P2": 1},
            payment_method="WALLET"
        )

        print("\n--- ORDER 2 ---")
        order2 = system.place_order(
            user_id="U2",
            restaurant_id="R2",
            items={"K1": 1},
            payment_method="CARD"
        )

        # Cancel attempt
        print("\n--- CANCEL ORDER TEST ---")
        system.cancel_order(order1.order_id)


if __name__ == "__main__":
    FoodDeliveryDemo.main()