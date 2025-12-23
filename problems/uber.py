import uuid
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional
import math
import threading

# --- Enums and Constants ---

class RideStatus(Enum):
    REQUESTED = "REQUESTED"
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

# --- Basic Models ---

class Location:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance_to(self, other: 'Location') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def __str__(self):
        return f"({self.x}, {self.y})"

# --- Observer Interface (For Notifications) ---

class User(ABC):
    def __init__(self, name: str, location: Location):
        self.id = str(uuid.uuid4())
        self.name = name
        self.location = location
        self.rating = 5.0

    @abstractmethod
    def update(self, message: str):
        pass

class Rider(User):
    def update(self, message: str):
        print(f"[Notification to Rider {self.name}]: {message}")

class Driver(User):
    def __init__(self, name: str, location: Location, available: bool = True):
        super().__init__(name, location)
        self.available = available

    def update(self, message: str):
        print(f"[Notification to Driver {self.name}]: {message}")

# --- Strategy Pattern: Pricing ---

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_fare(self, distance: float, time_min: float) -> float:
        pass

class StandardPricingStrategy(PricingStrategy):
    BASE_FARE = 50.0
    PER_KM_RATE = 10.0
    PER_MIN_RATE = 2.0

    def calculate_fare(self, distance: float, time_min: float) -> float:
        return self.BASE_FARE + (self.PER_KM_RATE * distance) + (self.PER_MIN_RATE * time_min)

class SurgePricingStrategy(PricingStrategy):
    SURGE_MULTIPLIER = 2.0
    BASE_FARE = 50.0
    PER_KM_RATE = 10.0
    PER_MIN_RATE = 2.0

    def calculate_fare(self, distance: float, time_min: float) -> float:
        base = self.BASE_FARE + (self.PER_KM_RATE * distance) + (self.PER_MIN_RATE * time_min)
        return base * self.SURGE_MULTIPLIER

# --- Strategy Pattern: Driver Matching ---

class DriverMatchingStrategy(ABC):
    @abstractmethod
    def find_driver(self, rider: Rider, drivers: List[Driver]) -> Optional[Driver]:
        pass

class NearestDriverMatchingStrategy(DriverMatchingStrategy):
    def find_driver(self, rider: Rider, drivers: List[Driver]) -> Optional[Driver]:
        if not drivers:
            return None
        
        # Simple algorithm: Find available driver with minimum distance
        nearest_driver = None
        min_dist = float('inf')

        for driver in drivers:
            if driver.available:
                dist = rider.location.distance_to(driver.location)
                if dist < min_dist:
                    min_dist = dist
                    nearest_driver = driver
        
        return nearest_driver

# --- Core Entity: Ride ---

class Ride:
    def __init__(self, rider: Rider, pickup: Location, dropoff: Location, pricing_strategy: PricingStrategy):
        self.id = str(uuid.uuid4())
        self.rider = rider
        self.driver: Optional[Driver] = None
        self.pickup = pickup
        self.dropoff = dropoff
        self.status = RideStatus.REQUESTED
        self.fare = 0.0
        self.pricing_strategy = pricing_strategy

    def assign_driver(self, driver: Driver):
        self.driver = driver
        self.status = RideStatus.ACCEPTED
        driver.available = False
        self.notify_all(f"Ride matched! Driver {driver.name} is on the way.")

    def start_ride(self):
        if self.status == RideStatus.ACCEPTED:
            self.status = RideStatus.IN_PROGRESS
            self.notify_all("Ride Started.")
        else:
            print("Cannot start ride. Status is not ACCEPTED.")

    def end_ride(self, duration_min: float):
        if self.status == RideStatus.IN_PROGRESS:
            self.status = RideStatus.COMPLETED
            if self.driver:
                self.driver.available = True
                self.driver.location = self.dropoff # Update driver location
            
            distance = self.pickup.distance_to(self.dropoff)
            self.fare = self.pricing_strategy.calculate_fare(distance, duration_min)
            
            self.notify_all(f"Ride Completed. Fare is ${self.fare:.2f}")
        else:
            print("Cannot end ride. Status is not IN_PROGRESS.")

    def notify_all(self, message: str):
        # Observer Pattern implementation
        self.rider.update(message)
        if self.driver:
            self.driver.update(message)



# --- System Controller: RideManager (Singleton Pattern) ---

class RideManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        if RideManager._instance is not None:
            raise Exception("This class is a singleton!")
        self.drivers: List[Driver] = []
        self.riders: List[Rider] = []
        # Injecting strategies
        self.matching_strategy = NearestDriverMatchingStrategy()
        self.pricing_strategy = StandardPricingStrategy()

    @staticmethod
    def get_instance():
        if RideManager._instance is None:
            with RideManager._lock:
                if RideManager._instance is None:
                    RideManager._instance = RideManager()
        return RideManager._instance

    def add_driver(self, driver: Driver):
        self.drivers.append(driver)

    def add_rider(self, rider: Rider):
        self.riders.append(rider)

    def set_pricing_strategy(self, strategy: PricingStrategy):
        self.pricing_strategy = strategy

    def set_matching_strategy(self, strategy: DriverMatchingStrategy):
        self.matching_strategy = strategy

    def request_ride(self, rider: Rider, pickup: Location, dropoff: Location) -> Optional[Ride]:
        print(f"\n--- Processing Ride Request for {rider.name} ---")
        
        # 1. Create the Ride object
        ride = Ride(rider, pickup, dropoff, self.pricing_strategy)
        
        # 2. Find a driver using the Strategy
        driver = self.matching_strategy.find_driver(rider, self.drivers)
        
        if driver:
            ride.assign_driver(driver)
            return ride
        else:
            print("No drivers available.")
            return None

# --- Main Execution Block ---

class UberDemo:
    @staticmethod
    def main():
        # 1. Initialize the System (get singleton instance)
        uber = RideManager.get_instance()

        # 2. Create Riders and Drivers
        # Grid locations (0,0) to (100,100)
        print("\n--- Setting up Drivers and Riders ---")
        driver1 = Driver("Alice", Location(10, 10))
        driver2 = Driver("Bob", Location(50, 50)) # Far away
        rider1 = Rider("John", Location(12, 12))  # Close to Alice
        rider2 = Rider("Sarah", Location(45, 45))  # Close to Bob

        uber.add_driver(driver1)
        uber.add_driver(driver2)
        uber.add_rider(rider1)
        uber.add_rider(rider2)

        # 3. First ride request
        # Going from (12,12) to (20,20)
        print("\n--- Ride Request 1: John's Ride ---")
        ride1 = uber.request_ride(rider1, rider1.location, Location(20, 20))

        if ride1:
            # 4. Simulate the ride lifecycle
            print(f"Ride Status: {ride1.status.value}")
            
            # Start the ride
            ride1.start_ride()
            
            # End the ride (simulating it took 15 minutes)
            ride1.end_ride(duration_min=15)
            
            print(f"Final Ride Status: {ride1.status.value}")

        # 5. Second ride request (with surge pricing)
        print("\n--- Ride Request 2: Sarah's Ride (with Surge Pricing) ---")
        uber.set_pricing_strategy(SurgePricingStrategy())
        
        ride2 = uber.request_ride(rider2, rider2.location, Location(60, 60))

        if ride2:
            print(f"Ride Status: {ride2.status.value}")
            ride2.start_ride()
            ride2.end_ride(duration_min=20)
            print(f"Final Ride Status: {ride2.status.value}")


if __name__ == "__main__":
    UberDemo.main()