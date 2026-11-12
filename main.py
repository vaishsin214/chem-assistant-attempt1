
from dataclasses import dataclass
from drafter import *
from chempy import *


@dataclass
class Chemical:
    """
    Stores information about one chemical.
    """
    formula: str
    mass: float
    molar_mass: float
    coefficient: int


@dataclass
class State:
    """
    Stores all information for the chemical reaction calculator.
    """
    equation: str
    reactants: list[Chemical]
    products: list[Chemical]
    actual_yield: float
    enthalpy: float
    results: list[str]


initial_state = State(
    equation="",
    reactants=[],
    products=[],
    actual_yield=0.0,
    enthalpy=0.0,
    results=[]
)


@route
def index(state: State) -> Page:
    """
    The starting page of the website.
    """
    return Page(state, [
        Header("Chemical Reaction Calculator"),
        "Enter a balanced chemical equation and its chemicals.",
        "The calculator will find the limiting reactant, leftover",
        "reactants, theoretical yield, percent yield, and reaction type.",
        Button("Start Calculation", "enter_equation")
    ])


@route
def enter_equation(state: State) -> Page:
    """
    Asks the user to enter a balanced chemical equation.
    """
    return Page(state, [
        Header("Step 1: Enter the Equation"),
        TextBox("equation", state.equation),
        Button("Save Equation", "save_equation"),
        Button("Back Home", "index")
    ])


@route
def save_equation(state: State, equation: str) -> Page:
    """
    Saves the equation and moves to the reactant page.
    """
    if equation == "":
        return Page(state, [
            Header("Input Error"),
            "Please enter a balanced chemical equation.",
            Button("Try Again", "enter_equation")
        ])

    state.equation = equation
    return enter_reactants(state)


@route
def enter_reactants(state: State) -> Page:
    """
    Shows the form for entering reactants.
    """
    content = [
        Header("Step 2: Enter Reactants"),
        "Enter each reactant separately.",
        "Chemical formula:",
        TextBox("formula", ""),
        "Coefficient:",
        TextBox("coefficient", "1"),
        "Mass in grams:",
        TextBox("mass", "0"),
        "Molar mass in grams per mole:",
        TextBox("molar_mass", "0"),
        Button("Add Reactant", "add_reactant"),
        Header("Current Reactants", 2)
    ]

    for chemical in state.reactants:
        content.append(
            chemical.formula + ": "
            + str(chemical.coefficient) + " coefficient, "
            + str(chemical.mass) + " grams"
        )

    content.append(Button("Done with Reactants", "enter_products"))
    content.append(Button("Back to Equation", "enter_equation"))

    return Page(state, content)


@route
def add_reactant(
    state: State,
    formula: str,
    coefficient: int,
    mass: float,
    molar_mass: float
) -> Page:
    """
    Checks and adds a reactant to the list.
    """
    if formula == "":
        return Page(state, [
            Header("Input Error"),
            "Please enter a chemical formula.",
            Button("Try Again", "enter_reactants")
        ])

    if coefficient <= 0:
        return Page(state, [
            Header("Input Error"),
            "The coefficient must be greater than zero.",
            Button("Try Again", "enter_reactants")
        ])

    if mass < 0:
        return Page(state, [
            Header("Input Error"),
            "Mass cannot be negative.",
            Button("Try Again", "enter_reactants")
        ])

    if molar_mass <= 0:
        return Page(state, [
            Header("Input Error"),
            "Molar mass must be greater than zero.",
            Button("Try Again", "enter_reactants")
        ])

    new_chemical = Chemical(
        formula=formula,
        mass=mass,
        molar_mass=molar_mass,
        coefficient=coefficient
    )

    state.reactants.append(new_chemical)

    return enter_reactants(state)


@route
def enter_products(state: State) -> Page:
    """
    Shows the form for entering products.
    """
    content = [
        Header("Step 3: Enter Products"),
        "Enter each product separately.",
        "Chemical formula:",
        TextBox("formula", ""),
        "Coefficient:",
        TextBox("coefficient", "1"),
        "Mass in grams:",
        TextBox("mass", "0"),
        "Molar mass in grams per mole:",
        TextBox("molar_mass", "0"),
        Button("Add Product", "add_product"),
        Header("Current Products", 2)
    ]

    for chemical in state.products:
        content.append(
            chemical.formula + ": "
            + str(chemical.coefficient) + " coefficient"
        )

    content.append(Button("Done with Products", "enter_yield"))
    content.append(Button("Back to Reactants", "enter_reactants"))

    return Page(state, content)


@route
def add_product(
    state: State,
    formula: str,
    coefficient: int,
    mass: float,
    molar_mass: float
) -> Page:
    """
    Checks and adds a product to the list.
    """
    if formula == "":
        return Page(state, [
            Header("Input Error"),
            "Please enter a chemical formula.",
            Button("Try Again", "enter_products")
        ])

    if coefficient <= 0:
        return Page(state, [
            Header("Input Error"),
            "The coefficient must be greater than zero.",
            Button("Try Again", "enter_products")
        ])

    if mass < 0:
        return Page(state, [
            Header("Input Error"),
            "Mass cannot be negative.",
            Button("Try Again", "enter_products")
        ])

    if molar_mass <= 0:
        return Page(state, [
            Header("Input Error"),
            "Molar mass must be greater than zero.",
            Button("Try Again", "enter_products")
        ])

    new_chemical = Chemical(
        formula=formula,
        mass=mass,
        molar_mass=molar_mass,
        coefficient=coefficient
    )

    state.products.append(new_chemical)

    return enter_products(state)


@route
def enter_yield(state: State) -> Page:
    """
    Asks for actual yield and enthalpy.
    """
    return Page(state, [
        Header("Step 4: Enter Reaction Information"),
        "Actual yield in grams:",
        TextBox("actual_yield", "0"),
        "Enthalpy in kJ:",
        TextBox("enthalpy", "0"),
        Button("Calculate Results", "save_reaction_info"),
        Button("Back to Products", "enter_products")
    ])


@route
def save_reaction_info(
    state: State,
    actual_yield: float,
    enthalpy: float
) -> Page:
    """
    Saves the reaction information and starts the calculations.
    """
    if actual_yield < 0:
        return Page(state, [
            Header("Input Error"),
            "Actual yield cannot be negative.",
            Button("Try Again", "enter_yield")
        ])

    state.actual_yield = actual_yield
    state.enthalpy = enthalpy

    return calculate(state)


@route
def calculate(state: State) -> Page:
    """
    Calculates limiting reactant, leftover reactants,
    theoretical yield, percent yield, and reaction type.
    """

    if len(state.reactants) == 0:
        return Page(state, [
            Header("Input Error"),
            "Please enter at least one reactant.",
            Button("Back to Reactants", "enter_reactants")
        ])

    if len(state.products) == 0:
        return Page(state, [
            Header("Input Error"),
            "Please enter at least one product.",
            Button("Back to Products", "enter_products")
        ])

    # Find the limiting reactant using moles divided by coefficient.
    smallest_ratio = None
    limiting_reactant = ""

    for chemical in state.reactants:
        available_moles = chemical.mass / chemical.molar_mass
        ratio = available_moles / chemical.coefficient

        if smallest_ratio is None or ratio < smallest_ratio:
            smallest_ratio = ratio
            limiting_reactant = chemical.formula

    results = []

    results.append("Limiting Reactant: " + limiting_reactant)

    # Calculate how much of each reactant remains.
    for chemical in state.reactants:
        available_moles = chemical.mass / chemical.molar_mass
        moles_used = smallest_ratio * chemical.coefficient
        moles_left = available_moles - moles_used
        mass_left = moles_left * chemical.molar_mass

        if mass_left < 0:
            mass_left = 0

        results.append(
            chemical.formula + " remaining: "
            + str(round(mass_left, 2)) + " grams"
        )

    # Calculate theoretical yield for each product.
    theoretical_yields = []

    for chemical in state.products:
        product_moles = smallest_ratio * chemical.coefficient
        theoretical_mass = product_moles * chemical.molar_mass

        theoretical_yields.append(theoretical_mass)

        results.append(
            chemical.formula + " theoretical yield: "
            + str(round(theoretical_mass, 2)) + " grams"
        )

    # Percent yield uses the first product's theoretical yield.
    theoretical_yield = theoretical_yields[0]

    if theoretical_yield > 0:
        percent_yield = (
            state.actual_yield / theoretical_yield
        ) * 100

        results.append(
            "Percent Yield: " + str(round(percent_yield, 2)) + "%"
        )
    else:
        results.append("Percent yield cannot be calculated.")

    # Determine the reaction type from enthalpy.
    if state.enthalpy < 0:
        reaction_type = "Exothermic"
    elif state.enthalpy > 0:
        reaction_type = "Endothermic"
    else:
        reaction_type = "Neither exothermic nor endothermic"

    results.append("Reaction Type: " + reaction_type)

    state.results = results

    return results(state)


@route
def results(state: State) -> Page:
    """
    Displays the calculation results.
    """
    content = [
        Header("Calculation Results"),
        "Balanced Equation: " + state.equation,
        Header("Results", 2)
    ]

    for result in state.results:
        content.append(result)

    content.append(Button("Start New Calculation", "reset"))

    return Page(state, content)


@route
def reset(state: State) -> Page:
    """
    Clears the previous calculation and returns to the start.
    """
    state.equation = ""
    state.reactants = []
    state.products = []
    state.actual_yield = 0.0
    state.enthalpy = 0.0
    state.results = []

    return index(state)


start_server(initial_state)

