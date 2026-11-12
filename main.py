
from drafter import *
from dataclasses import dataclass, field


# Website title and authorship information.
set_website_title("Travel Budget Planner")

set_site_information(
    author="Kingsley Royal",
    description="Plan travel expenses, calculate daily budgets, "
                "and organize spending based on travel preferences.",
    sources="Drafter documentation, ChatGPT assistance, "
            "and CISC106 course materials.",
    planning=[],
    links=["https://github.com/royalk-ai/travel-budget-planner"]
)

set_website_framed(False)


# ----------------------------------
# DATA CLASSES
# ----------------------------------

@dataclass
class Expense:
    """Represent one planned expense during a trip."""
    name: str
    category: str
    cost: float


@dataclass
class State:
    """Store trip details and planned expenses between pages."""
    destination: str = ""
    total_budget: float = 0.0
    flight_cost: float = 0.0
    accommodation_cost: float = 0.0
    length_of_stay: int = 1
    exchange_rate: float = 1.0
    currency_name: str = ""
    travel_preference: str = "Balanced"

    # default_factory gives each State its own expense list.
    expenses: list[Expense] = field(default_factory=list)


# ----------------------------------
# HELPER FUNCTIONS
# ----------------------------------

def remaining_budget(state: State) -> float:
    """Calculate money remaining after flight and hotel costs."""
    return (state.total_budget - state.flight_cost
            - state.accommodation_cost)


def daily_budget(state: State) -> float:
    """Calculate daily spending while reserving 10% for savings."""
    spending = remaining_budget(state) * 0.90
    return spending / state.length_of_stay


def money(amount: float) -> str:
    """Format a number as a USD amount."""
    return f"${amount:,.2f}"


def budget_categories(
    state: State
) -> tuple[float, float, float, float]:
    """Divide remaining money based on travel preference."""
    remaining = remaining_budget(state)

    # Select budget percentages based on user preference.
    if state.travel_preference == "Food":
        food = remaining * 0.50
        transportation = remaining * 0.20
        activities = remaining * 0.20

    elif state.travel_preference == "Activities":
        food = remaining * 0.30
        transportation = remaining * 0.20
        activities = remaining * 0.40

    elif state.travel_preference == "Transportation":
        food = remaining * 0.30
        transportation = remaining * 0.40
        activities = remaining * 0.20

    else:
        food = remaining * 0.40
        transportation = remaining * 0.30
        activities = remaining * 0.20

    savings = remaining * 0.10

    return food, transportation, activities, savings


def total_planned_expenses(state: State) -> float:
    """Add the costs of all expenses stored in State."""
    total = 0.0

    # Each Expense object contains a cost attribute.
    for expense in state.expenses:
        total += expense.cost

    return total


# ----------------------------------
# PAGE 1: HOME
# ----------------------------------

@route
def index(state: State) -> Page:
    """Display the homepage and introduction."""
    return Page(state, [
        Header("Travel Budget Planner"),
        "Welcome to your travel budgeting assistant!\n",
        "Plan your trip and organize your spending.\n",
        "Create a personalized daily budget based "
        "on your travel preferences.\n",
        Button("Start Planning", "start_planning")
    ])


# ----------------------------------
# PAGE 2: TRIP INPUT
# ----------------------------------

@route
def start_planning(state: State) -> Page:
    """Collect travel information and spending preferences."""
    return Page(state, [
        Header("Enter Your Trip Details"),

        "Travel Destination:",
        TextBox("destination", state.destination),

        "\nTotal Budget (USD):",
        TextBox("total_budget", state.total_budget, "number"),

        "\nFlight Cost (USD):",
        TextBox("flight_cost", state.flight_cost, "number"),

        "\nAccommodation Cost (USD):",
        TextBox(
            "accommodation_cost",
            state.accommodation_cost,
            "number"
        ),

        "\nLength of Stay (Days):",
        TextBox("length_of_stay", state.length_of_stay, "number"),

        "\nExchange Rate (1 USD equals):",
        TextBox("exchange_rate", state.exchange_rate, "number"),

        "\nForeign Currency Name (e.g. JPY):",
        TextBox("currency_name", state.currency_name),

        "\nWhat do you plan to spend the most on?",
        SelectBox(
            "travel_preference",
            ["Balanced", "Food", "Activities", "Transportation"],
            state.travel_preference
        ),

        "\n",
        Button("Calculate Budget", "calculate_budget")
    ])


# ----------------------------------
# ROUTE: CALCULATE BUDGET
# ----------------------------------

@route
def calculate_budget(
    state: State,
    destination: str,
    total_budget: float,
    flight_cost: float,
    accommodation_cost: float,
    length_of_stay: int,
    exchange_rate: float,
    currency_name: str,
    travel_preference: str
) -> Page:
    """Validate trip inputs and save information in State."""

    # Check that the trip duration is valid.
    if length_of_stay <= 0:
        return Page(state, [
            Header("Invalid Trip Length"),
            "Your trip must be at least one day.",
            Button("Try Again", "start_planning")
        ])

    # Check for invalid amounts.
    if (total_budget < 0 or flight_cost < 0
            or accommodation_cost < 0 or exchange_rate <= 0):
        return Page(state, [
            Header("Invalid Amount"),
            "Costs must be nonnegative, and the exchange "
            "rate must be greater than zero.",
            Button("Try Again", "start_planning")
        ])

    # Check whether fixed expenses exceed the budget.
    if flight_cost + accommodation_cost > total_budget:
        return Page(state, [
            Header("Over Budget!"),
            "Your flight and accommodation exceed "
            "your available travel budget.",
            Button("Try Again", "start_planning")
        ])

    # Check for a missing destination.
    if destination.strip() == "":
        return Page(state, [
            Header("Missing Destination"),
            "Please enter your travel destination.",
            Button("Try Again", "start_planning")
        ])

    # Update State with the submitted information.
    state.destination = destination
    state.total_budget = total_budget
    state.flight_cost = flight_cost
    state.accommodation_cost = accommodation_cost
    state.length_of_stay = length_of_stay
    state.exchange_rate = exchange_rate
    state.currency_name = currency_name
    state.travel_preference = travel_preference

    # Begin a new trip with an empty expense list.
    state.expenses = []

    return results_page(state)


# ----------------------------------
# PAGE 3: BUDGET RESULTS
# ----------------------------------

@route
def results_page(state: State) -> Page:
    """Display personalized budgets and daily spending."""
    remaining = remaining_budget(state)

    food, transportation, activities, savings = budget_categories(state)

    daily = daily_budget(state)
    foreign_daily = daily * state.exchange_rate

    content = [
        Header("Your Travel Budget Results"),

        "Destination: " + state.destination + "\n",
        "Length of Stay: " + str(state.length_of_stay) + " days\n",
        "Travel Preference: " + state.travel_preference + "\n",

        Header("Budget Summary", 2),
        "Total Budget: " + money(state.total_budget) + "\n",
        "Flight: " + money(state.flight_cost) + "\n",
        "Accommodation: " + money(state.accommodation_cost) + "\n",
        "Remaining Budget: " + money(remaining) + "\n",

        Header("Personalized Budget Allocation", 2),
        "Food: " + money(food) + "\n",
        "Transportation: " + money(transportation) + "\n",
        "Activities: " + money(activities) + "\n",
        "Emergency Savings: " + money(savings) + "\n",

        Header("Daily Spending Budget", 2),
        "Total Daily Allowance: " + money(daily) + "\n",
        "Daily Food: "
        + money(food / state.length_of_stay) + "\n",
        "Daily Transportation: "
        + money(transportation / state.length_of_stay) + "\n",
        "Daily Activities: "
        + money(activities / state.length_of_stay) + "\n",

        Header("Foreign Currency Estimate", 2),
        f"{foreign_daily:,.2f} {state.currency_name} per day\n"
    ]

    # Warn the user about a low daily allowance.
    if daily < 50:
        content.append(
            "Warning: Your daily spending budget is below $50.\n"
        )
    else:
        content.append(
            "Your daily spending budget is at least $50.\n"
        )

    content.extend([
        Button("Add Expenses", "expenses_page"),
        Button("View Report", "report_page"),
        Button("Edit Trip", "start_planning"),
        Button("Back to Home", "back_to_home")
    ])

    return Page(state, content)


# ----------------------------------
# PAGE 4: ADD EXPENSES
# ----------------------------------

@route
def expenses_page(state: State) -> Page:
    """Display a form for adding planned travel expenses."""
    return Page(state, [
        Header("Add Planned Expenses"),

        "Enter an expense you expect during your trip.\n",

        "Expense Name:",
        TextBox("expense_name", ""),

        "\nExpense Category:",
        SelectBox(
            "category",
            ["Food", "Transportation", "Activities"]
        ),

        "\nExpense Cost (USD):",
        TextBox("cost", 0.0, "number"),

        "\n",
        Button("Save Expense", "save_expense")
    ])


# ----------------------------------
# ROUTE: SAVE EXPENSE
# ----------------------------------

@route
def save_expense(
    state: State,
    expense_name: str,
    category: str,
    cost: float
) -> Page:
    """Create an Expense object and save it in the State list."""

    # Reject negative costs and empty expense names.
    if cost < 0 or expense_name.strip() == "":
        return Page(state, [
            Header("Invalid Expense"),
            "Enter an expense name and a nonnegative cost.",
            Button("Try Again", "expenses_page")
        ])

    new_expense = Expense(expense_name, category, cost)

    # Add the new Expense instance to the list.
    state.expenses.append(new_expense)

    return Page(state, [
        Header("Expense Saved!"),
        expense_name + ": " + money(cost) + "\n",
        "Category: " + category + "\n",
        Button("Add Another Expense", "expenses_page"),
        Button("View Report", "report_page"),
        Button("Back to Results", "results_page")
    ])


# ----------------------------------
# PAGE 5: EXPENSE REPORT
# ----------------------------------

@route
def report_page(state: State) -> Page:
    """Display planned expenses and remaining spending money."""
    remaining = remaining_budget(state)

    food, transportation, activities, savings = budget_categories(state)

    spending_budget = remaining - savings
    total_expenses = total_planned_expenses(state)
    uncommitted = spending_budget - total_expenses

    content = [
        Header("Your Expense Report"),

        "Destination: " + state.destination + "\n",
        "Travel Preference: " + state.travel_preference + "\n",

        Header("Fixed Trip Expenses", 2),
        "Flight: " + money(state.flight_cost) + "\n",
        "Accommodation: " + money(state.accommodation_cost) + "\n",

        Header("Category Budgets", 2),
        "Food: " + money(food) + "\n",
        "Transportation: " + money(transportation) + "\n",
        "Activities: " + money(activities) + "\n",
        "Emergency Savings: " + money(savings) + "\n",

        Header("Planned Additional Expenses", 2)
    ]

    # Show a message when the expense list is empty.
    if len(state.expenses) == 0:
        content.append("No planned expenses added yet.\n")
    else:
        # Display each Expense object in the report.
        for expense in state.expenses:
            content.append(
                expense.name + " (" + expense.category + "): "
                + money(expense.cost) + "\n"
            )

    content.extend([
        Header("Final Budget Summary", 2),
        "Original Budget: " + money(state.total_budget) + "\n",
        "Budget After Flight and Hotel: "
        + money(remaining) + "\n",
        "Emergency Savings: " + money(savings) + "\n",
        "Daily Spending Allowance: "
        + money(daily_budget(state)) + "\n",
        "Total Planned Expenses: "
        + money(total_expenses) + "\n",
        "Uncommitted Spending Budget: "
        + money(uncommitted) + "\n"
    ])

    # Warn if planned expenses exceed available spending money.
    if uncommitted < 0:
        content.append(
            "Warning: Your planned expenses exceed "
            "your available spending budget.\n"
        )

    content.extend([
        Button("Add More Expenses", "expenses_page"),
        Button("Back to Results", "results_page"),
        Button("Back to Home", "back_to_home")
    ])

    return Page(state, content)


# ----------------------------------
# ROUTE: RETURN HOME
# ----------------------------------

@route
def back_to_home(state: State) -> Page:
    """Return to the homepage without clearing trip information."""
    return index(state)


# ----------------------------------
# UNIT TESTS
# ----------------------------------

def run_tests() -> None:
    """Test calculations, route navigation, and State changes."""

    # Use a sample 10-day trip for testing.
    sample = State(
        destination="Tokyo",
        total_budget=3000.0,
        flight_cost=900.0,
        accommodation_cost=800.0,
        length_of_stay=10,
        exchange_rate=150.0,
        currency_name="JPY",
        travel_preference="Balanced"
    )

    # Test helper functions.
    assert_equal(remaining_budget(sample), 1300.0)
    assert_equal(daily_budget(sample), 117.0)
    assert_equal(money(25.0), "$25.00")

    food, transport, activities, savings = budget_categories(sample)

    assert_equal(food, 520.0)
    assert_equal(transport, 390.0)
    assert_equal(activities, 260.0)
    assert_equal(savings, 130.0)

    # Test all spending preferences.
    sample.travel_preference = "Food"
    food, transport, activities, savings = budget_categories(sample)
    assert_equal(food, 650.0)

    sample.travel_preference = "Activities"
    food, transport, activities, savings = budget_categories(sample)
    assert_equal(activities, 520.0)

    sample.travel_preference = "Transportation"
    food, transport, activities, savings = budget_categories(sample)
    assert_equal(transport, 520.0)

    sample.travel_preference = "Balanced"

    # Test homepage route.
    assert_has(
        index(sample),
        Button("Start Planning", "start_planning")
    )

    # Test trip input route.
    assert_has(
        start_planning(sample),
        Button("Calculate Budget", "calculate_budget")
    )

    # Test the calculation route and State modifications.
    new_trip = State()

    calculated = calculate_budget(
        new_trip, "Tokyo", 3000.0, 900.0, 800.0,
        10, 150.0, "JPY", "Balanced"
    )

    assert_equal(calculated.state.destination, "Tokyo")
    assert_equal(calculated.state.total_budget, 3000.0)
    assert_equal(calculated.state.length_of_stay, 10)
    assert_equal(calculated.state.travel_preference, "Balanced")

    # Test invalid trip length.
    invalid_days = calculate_budget(
        State(), "Tokyo", 3000.0, 900.0, 800.0,
        0, 150.0, "JPY", "Balanced"
    )
    assert_has(
        invalid_days,
        Button("Try Again", "start_planning")
    )

    # Test a trip that exceeds the budget.
    over_budget = calculate_budget(
        State(), "Tokyo", 1000.0, 900.0, 800.0,
        10, 150.0, "JPY", "Balanced"
    )
    assert_has(
        over_budget,
        Button("Try Again", "start_planning")
    )

    # Test results page route.
    assert_has(
        results_page(sample),
        Button("View Report", "report_page")
    )

    # Test add expenses page route.
    assert_has(
        expenses_page(sample),
        Button("Save Expense", "save_expense")
    )

    # Test saving a new Expense object.
    expense_state = State(
        destination="Tokyo",
        total_budget=3000.0,
        flight_cost=900.0,
        accommodation_cost=800.0,
        length_of_stay=10
    )

    saved_page = save_expense(
        expense_state, "Museum Ticket", "Activities", 25.0
    )

    assert_equal(len(expense_state.expenses), 1)
    assert_equal(expense_state.expenses[0].name, "Museum Ticket")
    assert_equal(expense_state.expenses[0].category, "Activities")
    assert_equal(expense_state.expenses[0].cost, 25.0)
    assert_equal(total_planned_expenses(expense_state), 25.0)

    assert_has(
        saved_page,
        Button("View Report", "report_page")
    )

    # Test invalid expenses.
    invalid_expense = save_expense(
        expense_state, "", "Food", -5.0
    )
    assert_has(
        invalid_expense,
        Button("Try Again", "expenses_page")
    )

    # Test the report page route.
    assert_has(
        report_page(expense_state),
        Button("Back to Results", "results_page")
    )

    # Test the back-to-home route.
    assert_has(
        back_to_home(sample),
        Button("Start Planning", "start_planning")
    )


# Run tests before starting the website.
run_tests()

# Launch the Drafter application.
start_server(State())
