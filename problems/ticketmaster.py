from __future__ import annotations
from enum import Enum
from threading import Lock
from abc import ABC, abstractmethod
from datetime import datetime
import uuid
from typing import List, Dict, Optional


class BookingStatus(Enum):
    PENDING = 1
    CONFIRMED = 2
    CANCELLED = 3



class User:
    def __init__(self, user_id: str, name: str, email: str):
        self.id = user_id
        self.name = name
        self.email = email
        
        
class SeatType(Enum):
    REGULAR = 1
    PREMIUM = 2
    VIP = 3

class SeatStatus(Enum):
    AVAILABLE = 1
    BOOKED = 2
    RESERVED = 3

class SeatNotAvailableException(Exception):
    pass

class Seat:
    def __init__(self, id: str, seat_number: str, seat_type: SeatType, price: float):
        self.id = id
        self.seat_number = seat_number
        self.seat_type = seat_type
        self.price = price
        self.status = SeatStatus.AVAILABLE
        self._lock = Lock()

    def book(self):
        with self._lock:
            if self.status == SeatStatus.AVAILABLE:
                self.status = SeatStatus.BOOKED
            else:
                raise SeatNotAvailableException("Seat is already booked or reserved.")

    def release(self):
        with self._lock:
            if self.status == SeatStatus.BOOKED:
                self.status = SeatStatus.AVAILABLE


# Observer interfaces for booking notifications
class BookingObserver(ABC):
    @abstractmethod
    def update(self, event_type: str, booking: "Booking") -> None:
        pass


class EmailNotifier(BookingObserver):
    def update(self, event_type: str, booking: "Booking") -> None:
        if event_type == "BOOKING_CONFIRMED":
            print(f"[Email] To {booking.user.email}: Your booking {booking.id} is confirmed for {booking.concert.artist}.")
        elif event_type == "BOOKING_CANCELLED":
            print(f"[Email] To {booking.user.email}: Your booking {booking.id} has been cancelled.")


class SMSNotifier(BookingObserver):
    def update(self, event_type: str, booking: "Booking") -> None:
        if event_type == "BOOKING_CONFIRMED":
            print(f"[SMS] To {booking.user.name}: Booking {booking.id} confirmed.")
        elif event_type == "BOOKING_CANCELLED":
            print(f"[SMS] To {booking.user.name}: Booking {booking.id} cancelled.")
                
                
class Concert:
    def __init__(self, concert_id: str, artist: str, venue: str, date_time: datetime, seats: List['Seat']):
        self.id = concert_id
        self.artist = artist
        self.venue = venue
        self.date_time = date_time
        self.seats = seats
        


class ConcertTicketBookingSystem:
    _instance: Optional["ConcertTicketBookingSystem"] = None
    concerts: Dict[str, "Concert"]
    bookings: Dict[str, "Booking"]
    _lock: Lock
    observers: List["BookingObserver"]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.concerts = {}
            cls._instance.bookings = {}
            cls._instance._lock = Lock()
            cls._instance.observers = []
        return cls._instance

    # Observer registration
    def register_observer(self, observer: "BookingObserver"):
        self.observers.append(observer)

    def unregister_observer(self, observer: "BookingObserver"):
        if observer in self.observers:
            self.observers.remove(observer)

    def notify_observers(self, event_type: str, booking: "Booking"):
        for obs in list(self.observers):
            try:
                obs.update(event_type, booking)
            except Exception:
                # keep notifications best-effort; ignore observer errors
                pass

    def add_concert(self, concert: Concert):
        self.concerts[concert.id] = concert

    def get_concert(self, concert_id: str) -> Optional[Concert]:
        return self.concerts.get(concert_id)

    def search_concerts(self, artist: str, venue: str, date_time: datetime) -> List[Concert]:
        return [
            concert for concert in self.concerts.values()
            if concert.artist.lower() == artist.lower() and
               concert.venue.lower() == venue.lower() and
               concert.date_time == date_time
        ]

    def book_tickets(self, user: User, concert: Concert, seats: List[Seat]) -> Booking:
        with self._lock:
            # Check seat availability and book seats
            for seat in seats:
                if seat.status != SeatStatus.AVAILABLE:
                    raise SeatNotAvailableException(f"Seat {seat.seat_number} is not available.")
            for seat in seats:
                seat.book()

            # Create booking
            booking_id = self._generate_booking_id()
            booking = Booking(booking_id, user, concert, seats)
            self.bookings[booking_id] = booking

            # Process payment
            self._process_payment(booking)

            # Confirm booking
            confirmed = booking.confirm_booking()
            if confirmed:
                # notify observers about confirmation
                self.notify_observers("BOOKING_CONFIRMED", booking)

            print(f"Booking {booking.id} - {len(booking.seats)} seats booked")

            return booking

    def cancel_booking(self, booking_id: str):
        booking = self.bookings.get(booking_id)
        if booking:
            cancelled = booking.cancel_booking()
            if cancelled:
                # notify observers about cancellation
                self.notify_observers("BOOKING_CANCELLED", booking)
            del self.bookings[booking_id]

    def _process_payment(self, booking: Booking):
        # Process payment for the booking
        # ...
        pass

    def _generate_booking_id(self) -> str:
        return f"BKG{uuid.uuid4()}"
        

class Booking:
    def __init__(self, id: str, user: User, concert: Concert, seats: List[Seat]):
        self.id = id
        self.user = user
        self.concert = concert
        self.seats = seats
        self.total_price = sum(seat.price for seat in seats)
        self.status = BookingStatus.PENDING

    def confirm_booking(self):
        if self.status == BookingStatus.PENDING:
            self.status = BookingStatus.CONFIRMED
            # Send booking confirmation to the user
            # ...
            return True
        return False

    def cancel_booking(self):
        if self.status == BookingStatus.CONFIRMED:
            self.status = BookingStatus.CANCELLED
            for seat in self.seats:
                seat.release()
            print(f"Booking {self.id} cancelled")
            # Send booking cancellation notification to the user
            # ...
            return True
        return False
            
            
            
class ConcertTicketBookingSystemDemo:
    @staticmethod
    def run():
        # Create concert ticket booking system instance
        booking_system = ConcertTicketBookingSystem()

        # Register example observers
        booking_system.register_observer(EmailNotifier())
        booking_system.register_observer(SMSNotifier())

        # Create concerts
        concert1_seats = ConcertTicketBookingSystemDemo._generate_seats(100)
        concert1 = Concert("C001", "Artist 1", "Venue 1", datetime.now().replace(day=10, hour=20, minute=0, second=0, microsecond=0), concert1_seats)
        booking_system.add_concert(concert1)

        concert2_seats = ConcertTicketBookingSystemDemo._generate_seats(50)
        concert2 = Concert("C002", "Artist 2", "Venue 2", datetime.now().replace(day=15, hour=19, minute=30, second=0, microsecond=0), concert2_seats)
        booking_system.add_concert(concert2)

        # Create users
        user1 = User("U001", "John Doe", "john@example.com")
        user2 = User("U002", "Jane Smith", "jane@example.com")

        # Search concerts
        search_results = booking_system.search_concerts("Artist 1", "Venue 1", concert1.date_time)
        print("Search Results:")
        for concert in search_results:
            print(f"Concert: {concert.artist} at {concert.venue}")

        # Book tickets
        selected_seats1 = ConcertTicketBookingSystemDemo._select_seats(concert1, 3)
        booking1 = booking_system.book_tickets(user1, concert1, selected_seats1)

        selected_seats2 = ConcertTicketBookingSystemDemo._select_seats(concert2, 2)
        booking2 = booking_system.book_tickets(user2, concert2, selected_seats2)

        # Cancel booking
        booking_system.cancel_booking(booking1.id)

        # Book tickets again
        selected_seats3 = ConcertTicketBookingSystemDemo._select_seats(concert1, 2)
        booking3 = booking_system.book_tickets(user2, concert1, selected_seats3)

    @staticmethod
    def _generate_seats(number_of_seats: int) -> List[Seat]:
        seats = []
        for i in range(1, number_of_seats + 1):
            seat_number = f"S{i}"
            seat_type = SeatType.VIP if i <= 10 else SeatType.PREMIUM if i <= 30 else SeatType.REGULAR
            price = 100.0 if seat_type == SeatType.VIP else 75.0 if seat_type == SeatType.PREMIUM else 50.0
            seats.append(Seat(seat_number, seat_number, seat_type, price))
        return seats

    @staticmethod
    def _select_seats(concert: Concert, number_of_seats: int) -> List[Seat]:
        available_seats = [seat for seat in concert.seats if seat.status == SeatStatus.AVAILABLE]
        return available_seats[:number_of_seats]

if __name__ == "__main__":
    ConcertTicketBookingSystemDemo.run()