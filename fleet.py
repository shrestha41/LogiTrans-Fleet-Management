"""LogiTrans Logistics - Object-Oriented Fleet Management Prototype.

Demonstrates the four pillars of OOP:
  * Abstraction   - Vehicle is an abstract base class
  * Encapsulation - the daily rate is private and validated
  * Inheritance   - PassengerCar and CargoTruck extend Vehicle
  * Polymorphism  - overridden billing, __str__, __lt__ and a type-blind manifest
"""
from abc import ABC, abstractmethod


class Vehicle(ABC):
    """Abstract blueprint for every rentable vehicle."""

    def __init__(self, vehicle_id, model, daily_rate):
        self.vehicle_id = vehicle_id
        self.model = model
        self.__daily_rate = None          # private (name-mangled) attribute
        self.set_daily_rate(daily_rate)   # reuse the validation logic

    # ---- Encapsulation: controlled access to the private rate ----
    def get_daily_rate(self):
        return self.__daily_rate

    def set_daily_rate(self, rate):
        if isinstance(rate, bool) or not isinstance(rate, (int, float)):
            raise ValueError("Daily rate must be a number")
        if rate <= 0.0:
            raise ValueError("Daily rate must be greater than 0.0")
        self.__daily_rate = float(rate)

    # ---- Abstraction: every subclass must supply its own billing ----
    @abstractmethod
    def calculate_rental_cost(self, days):
        """Return the total rental cost for the given number of days."""

    @staticmethod
    def _check_days(days):
        """Shared guard used by the subclasses' billing methods."""
        if isinstance(days, bool) or not isinstance(days, (int, float)) or days < 0:
            raise ValueError("Rental days must be a number that is 0 or more")

    # ---- Operator overloading: sort vehicles by daily rate ----
    def __lt__(self, other):
        if not isinstance(other, Vehicle):
            return NotImplemented
        return self.get_daily_rate() < other.get_daily_rate()


class PassengerCar(Vehicle):
    SEAT_FEE = 15.0

    def __init__(self, vehicle_id, model, daily_rate, num_seats):
        super().__init__(vehicle_id, model, daily_rate)
        self.num_seats = num_seats

    def calculate_rental_cost(self, days):
        self._check_days(days)
        return (self.get_daily_rate() * days) + (self.SEAT_FEE * self.num_seats)

    def __str__(self):
        return (f"PassengerCar [{self.vehicle_id}] {self.model} | "
                f"{self.num_seats} seats | ${self.get_daily_rate():.2f}/day")


class CargoTruck(Vehicle):
    TONNAGE_FEE = 50.0

    def __init__(self, vehicle_id, model, daily_rate, cargo_capacity_tons):
        super().__init__(vehicle_id, model, daily_rate)
        self.cargo_capacity_tons = cargo_capacity_tons

    def calculate_rental_cost(self, days):
        self._check_days(days)
        return (self.get_daily_rate() * days) + (self.TONNAGE_FEE * self.cargo_capacity_tons)

    def __str__(self):
        return (f"CargoTruck  [{self.vehicle_id}] {self.model} | "
                f"{self.cargo_capacity_tons} tons | ${self.get_daily_rate():.2f}/day")


def generate_fleet_manifest(fleet_list, days):
    """Print a manifest for a mixed fleet and return the fleet total.

    The function never checks what kind of vehicle it is handling: each
    object decides its own billing through method overriding.
    """
    print(f"===== LogiTrans Fleet Manifest ({days} days) =====")
    total = 0.0
    for vehicle in fleet_list:
        cost = vehicle.calculate_rental_cost(days)   # polymorphic call
        print(f"{str(vehicle)} -> Total: ${cost:,.2f}")
        total += cost
    print(f"Fleet total: ${total:,.2f}")
    return total


if __name__ == "__main__":
    fleet = [
        PassengerCar("PC-101", "Toyota Camry", 60.0, 5),
        CargoTruck("CT-201", "Volvo FH16", 150.0, 12.5),
        PassengerCar("PC-102", "Honda Odyssey", 85.0, 7),
        CargoTruck("CT-202", "Isuzu NPR", 110.0, 4.0),
    ]
    generate_fleet_manifest(fleet, 3)
    print("\nSorted by daily rate (uses __lt__):")
    for v in sorted(fleet):
        print("  ", v)
