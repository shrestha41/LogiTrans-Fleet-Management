"""Unit tests for the fleet management prototype.

Run with:  python test_fleet.py
"""
import contextlib
import inspect
import io
import unittest

from fleet import Vehicle, PassengerCar, CargoTruck, generate_fleet_manifest


class Van(Vehicle):
    """A brand-new vehicle type, used to prove the manifest needs no changes."""

    def calculate_rental_cost(self, days):
        return self.get_daily_rate() * days + 25.0

    def __str__(self):
        return f"Van [{self.vehicle_id}] {self.model}"


class TestAbstraction(unittest.TestCase):
    def test_vehicle_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            Vehicle("X-1", "Generic", 50.0)

    def test_subclass_without_billing_cannot_be_instantiated(self):
        class Incomplete(Vehicle):
            pass
        with self.assertRaises(TypeError):
            Incomplete("X-2", "Broken", 50.0)


class TestEncapsulation(unittest.TestCase):
    def setUp(self):
        self.car = PassengerCar("PC-1", "Camry", 60.0, 5)

    def test_getter_returns_rate(self):
        self.assertEqual(self.car.get_daily_rate(), 60.0)

    def test_setter_updates_rate(self):
        self.car.set_daily_rate(70)
        self.assertEqual(self.car.get_daily_rate(), 70.0)

    def test_zero_rate_rejected(self):
        with self.assertRaises(ValueError):
            self.car.set_daily_rate(0)

    def test_negative_rate_rejected(self):
        with self.assertRaises(ValueError):
            self.car.set_daily_rate(-5.5)

    def test_failed_set_keeps_old_rate(self):
        with self.assertRaises(ValueError):
            self.car.set_daily_rate(-1)
        self.assertEqual(self.car.get_daily_rate(), 60.0)

    def test_invalid_rate_in_constructor(self):
        with self.assertRaises(ValueError):
            CargoTruck("CT-9", "Bad", -10.0, 3.0)

    def test_non_numeric_rate_rejected(self):
        for bad in ("abc", None, True):
            with self.assertRaises(ValueError):
                self.car.set_daily_rate(bad)

    def test_private_attribute_hidden(self):
        with self.assertRaises(AttributeError):
            _ = self.car.__daily_rate
        self.assertFalse(hasattr(self.car, "daily_rate"))


class TestInheritance(unittest.TestCase):
    def test_base_attributes_set_through_super(self):
        truck = CargoTruck("CT-1", "Volvo", 150.0, 12.5)
        self.assertEqual((truck.vehicle_id, truck.model), ("CT-1", "Volvo"))
        self.assertEqual(truck.get_daily_rate(), 150.0)
        self.assertEqual(truck.cargo_capacity_tons, 12.5)

    def test_children_are_vehicles(self):
        self.assertTrue(issubclass(PassengerCar, Vehicle))
        self.assertTrue(issubclass(CargoTruck, Vehicle))


class TestPolymorphism(unittest.TestCase):
    def setUp(self):
        self.car = PassengerCar("PC-1", "Camry", 60.0, 5)
        self.truck = CargoTruck("CT-1", "Volvo", 150.0, 12.5)

    def test_car_cost(self):            # 60*3 + 15*5 = 255
        self.assertEqual(self.car.calculate_rental_cost(3), 255.0)

    def test_truck_cost(self):          # 150*3 + 50*12.5 = 1075
        self.assertEqual(self.truck.calculate_rental_cost(3), 1075.0)

    def test_zero_days_charges_fixed_fee_only(self):
        self.assertEqual(self.car.calculate_rental_cost(0), 75.0)

    def test_negative_days_rejected(self):
        with self.assertRaises(ValueError):
            self.truck.calculate_rental_cost(-2)

    def test_sorting_by_rate(self):
        self.assertEqual(sorted([self.truck, self.car]), [self.car, self.truck])
        self.assertIs(max([self.car, self.truck]), self.truck)

    def test_equal_rates_not_less_than(self):
        other = PassengerCar("PC-2", "Corolla", 60.0, 4)
        self.assertFalse(self.car < other)
        self.assertFalse(other < self.car)

    def test_str_descriptions(self):
        self.assertIn("5 seats", str(self.car))
        self.assertIn("12.5 tons", str(self.truck))


class TestManifest(unittest.TestCase):
    def run_manifest(self, fleet, days):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            total = generate_fleet_manifest(fleet, days)
        return total, out.getvalue()

    def test_mixed_fleet_total(self):
        fleet = [PassengerCar("PC-1", "Camry", 60.0, 5),
                 CargoTruck("CT-1", "Volvo", 150.0, 12.5)]
        total, text = self.run_manifest(fleet, 3)
        self.assertEqual(total, 1330.0)
        self.assertIn("$255.00", text)
        self.assertIn("$1,075.00", text)

    def test_empty_fleet(self):
        total, _ = self.run_manifest([], 5)
        self.assertEqual(total, 0.0)

    def test_manifest_has_no_type_checks(self):
        source = inspect.getsource(generate_fleet_manifest)
        self.assertNotIn("isinstance", source)
        self.assertNotIn("type(", source)

    def test_new_vehicle_type_works_unchanged(self):
        total, text = self.run_manifest([Van("V-1", "Ford Transit", 80.0)], 2)
        self.assertEqual(total, 185.0)
        self.assertIn("Van [V-1]", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
