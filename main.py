
from drafter import *
from dataclasses import dataclass, field

# Website information and authorship
set_website_title("Travel Budget Planner")

set_site_information(
    author="Kingsley Royal",
    description=
    """
    A travel budgeting website that helps users plan expenses,
    calculate daily spending limits,
    and organize their money based on travel preferences.
    """,
    sources="Drafter documentation, ChatGPT assistance, and course materials.",
    planning=["plan.pdf", "design.pdf"],
    links=["https://github.com/royalk-ai/travel-budget-planner"]
)

hide_debug_information()
set_website_framed(False)



# Stores each planned travel expense.
@dataclass
class Expense:
    name: str
    category: str
    cost: float


# Stores trip information between pages.
@dataclass
class State:
    destination: str = ""
    total_budget: float = 0.0
    flight_cost: float = 0.0
    accommodation_cost: float = 0.0
    length_of_stay: int = 1
    exchange_rate: float = 1.0
    currency_name: str = ""
    travel_preference: str = "Balanced"
    expenses: list[Expense] = field(default_factory=list)


# Calculates money left after fixed expenses.
def remaining_budget(state: State) -> float:
    return (state.total_budget - state.flight_cost
            - state.accommodation_cost)


# Calculates daily spending with 10% saved.
def daily_budget(state: State) -> float:
    spending = remaining_budget(state) * 0.90
    return spending / state.length_of_stay


# Formats amounts in USD.
def money(amount: float) -> str:
    return "$" + f"{amount:,.2f}"


# HOME PAGE
@route
def index(state: State) -> Page:
    return Page(state, [
        Header("Travel Budget Planner"),
        "Welcome to your travel budgeting assistant!\n",
        "Plan your trip and organize your money.\n",
        "Create a personalized daily spending budget "
        "based on your travel priorities.\n",
        Button("Start Planning", "start_planning")
    ])


# TRIP INPUT PAGE
@route
def start_planning(state: State) -> Page:
    return Page(state, [
        Header("Enter Your Trip Details"),

        "Travel Destination:",
        TextBox("destination", state.destination),

        "\nTotal Budget (USD):",
        TextBox("total_budget", state.total_budget, "number"),

        "\nFlight Cost (USD):",
        TextBox("flight_cost", state.flight_cost, "number"),

        "\nAccommodation Cost (USD):",
        TextBox("accommodation_cost",
                state.accommodation_cost, "number"),

        "\nLength of Stay (Days):",
        TextBox("length_of_stay",
                state.length_of_stay, "number"),

        "\nExchange Rate (1 USD equals):",
        TextBox("exchange_rate",
                state.exchange_rate, "number"),

        "\nForeign Currency Name (e.g. JPY):",
        TextBox("currency_name", state.currency_name),

        "\nWhat do you plan to spend the most on?",
        SelectBox(
            "travel_preference",
            ["Balanced", "Food", "Activities", "Transportation"],
            state.travel_preference
        ),

        "\n",
        Button("Calculate Budget", "calculate_budget"),
        Link("Back to Home", "index")
    ])


# Validates inputs and saves trip information.
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

    # Prevents invalid trip lengths.
    if length_of_stay <= 0:
        return Page(state, [
            Header("Invalid Trip Length"),
            "Your trip must be at least one day.",
            Button("Try Again", "start_planning")
        ])

    # Rejects negative costs and invalid exchange rates.
    if (total_budget < 0 or flight_cost < 0
            or accommodation_cost < 0 or exchange_rate <= 0):
        return Page(state, [
            Header("Invalid Amount"),
            "Costs cannot be negative, and the "
            "exchange rate must be greater than zero.",
            Button("Try Again", "start_planning")
        ])

    # Checks if fixed expenses exceed the budget.
    if flight_cost + accommodation_cost > total_budget:
        return Page(state, [
            Header("Over Budget!"),
            "Your flight and accommodation cost more "
            "than your total budget.",
            Button("Try Again", "start_planning")
        ])

    # Saves user inputs in State.
    state.destination = destination
    state.total_budget = total_budget
    state.flight_cost = flight_cost
    state.accommodation_cost = accommodation_cost
    state.length_of_stay = length_of_stay
    state.exchange_rate = exchange_rate
    state.currency_name = currency_name
    state.travel_preference = travel_preference

    # Clears expenses when creating a new budget.
    state.expenses = []

    return results_page(state)


# Determines category budgets based on travel preference.
def budget_categories(state: State) -> tuple:
    remaining = remaining_budget(state)

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
        # Default balanced allocation.
        food = remaining * 0.40
        transportation = remaining * 0.30
        activities = remaining * 0.20

    # Emergency savings always stays at 10%.
    savings = remaining * 0.10

    return food, transportation, activities, savings


# BUDGET RESULTS PAGE
@route
def results_page(state: State) -> Page:

    remaining = remaining_budget(state)

    # Gets category amounts for the selected preference.
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
        "Total: " + money(daily) + " per day\n",
        "Food: " + money(food / state.length_of_stay) + "\n",
        "Transportation: "
        + money(transportation / state.length_of_stay) + "\n",
        "Activities: "
        + money(activities / state.length_of_stay) + "\n",

        Header("Foreign Currency Estimate", 2),
        f"{foreign_daily:,.2f} {state.currency_name} per day\n"
    ]

    # Warns users when daily spending is limited.
    if daily < 50:
        content.append(
            "Warning: Your daily spending budget is below $50."
        )
    else:
        content.append(
            "Your daily spending budget is at least $50."
        )

    content.extend([
        Button("Add Expenses", "expenses_page"),
        Button("View Report", "report_page"),
        Button("Back to Home", "back_to_home")
    ])

    return Page(state, content)


# ADD EXPENSES PAGE
@route
def expenses_page(state: State) -> Page:
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
        Button("Save Expense", "save_expense"),
        Link("Back to Results", "results_page")
    ])


# Creates and saves an Expense object.
@route
def save_expense(
    state: State,
    expense_name: str,
    category: str,
    cost: float
) -> Page:

    # Checks for invalid expense information.
    if cost < 0 or expense_name.strip() == "":
        return Page(state, [
            Header("Invalid Expense"),
            "Enter an expense name and a nonnegative cost.",
            Button("Try Again", "expenses_page")
        ])

    new_expense = Expense(expense_name, category, cost)
    state.expenses.append(new_expense)

    return Page(state, [
        Header("Expense Saved!"),
        expense_name + ": " + money(cost) + "\n",
        "Category: " + category + "\n",
        Button("Add Another Expense", "expenses_page"),
        Button("View Report", "report_page"),
        Button("Back to Results", "results_page")
    ])


# EXPENSE REPORT PAGE
@route
def report_page(state: State) -> Page:

    total_expenses = 0.0
    expense_lines = []

    # Loops through the expenses and totals their costs.
    for expense in state.expenses:
        total_expenses += expense.cost
        expense_lines.append(
            expense.name + " (" + expense.category + "): "
            + money(expense.cost) + "\n"
        )

    remaining = remaining_budget(state)
    food, transportation, activities, savings = budget_categories(state)

    spending_budget = remaining - savings
    uncommitted = spending_budget - total_expenses

    content = [
        Header("Your Expense Report"),

        "Destination: " + state.destination + "\n",
        "Travel Preference: " + state.travel_preference + "\n",

        Header("Trip Expenses", 2),
        "Flight: " + money(state.flight_cost) + "\n",
        "Accommodation: " + money(state.accommodation_cost) + "\n",

        Header("Category Budgets", 2),
        "Food: " + money(food) + "\n",
        "Transportation: " + money(transportation) + "\n",
        "Activities: " + money(activities) + "\n",
        "Emergency Savings: " + money(savings) + "\n",

        Header("Planned Additional Expenses", 2)
    ]

    # Displays expenses stored in State.
    if len(state.expenses) == 0:
        content.append("No planned expenses added yet.\n")
    else:
        content.extend(expense_lines)

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

    # Checks whether planned expenses exceed available funds.
    if uncommitted < 0:
        content.append(
            "Warning: Your planned expenses exceed "
            "your available spending budget."
        )

    content.extend([
        Button("Add More Expenses", "expenses_page"),
        Button("Back to Results", "results_page"),
        Button("Back to Home", "back_to_home")
    ])

    return Page(state, content)


# Returns to the home page.
@route
def back_to_home(state: State) -> Page:
    return index(state)


# Starts the Drafter website.
start_server(State())

