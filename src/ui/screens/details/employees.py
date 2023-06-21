import random
from ui.screens.details.employee import Employee
from ui.screens.details.employee import Meal

# Predefined lists for generating random attributes
names = ["John Doe", "Jane Smith", "Michael Johnson",
         "Emily Davis", "David Wilson", "Olivia Thompson"]
emails = ["john@example.com", "jane@example.com", "michael@example.com",
          "emily@example.com", "david@example.com", "olivia@example.com"]
employee_ids = ["12345", "67890", "54321", "09876", "13579", "24680"]

# Generate a list of 50 random employees
employees = []
for _ in range(50):
    name = random.choice(names)
    email = random.choice(emails)
    employee_id = random.choice(employee_ids)
    booked_meals = random.choices(list(Meal), k=random.randint(0, 3))
    is_emergency = random.choice([True, False])
    consumed_meals = random.choices(list(Meal), k=random.randint(0, 3))

    employee = Employee(
        name=name,
        email=email,
        employeeID=employee_id,
        booked_meals=booked_meals,
        isEmergency=is_emergency,
        consumed_meals=consumed_meals
    )
    employees.append(employee)
