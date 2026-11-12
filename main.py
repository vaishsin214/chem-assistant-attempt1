
from dataclasses import dataclass
from drafter import *
from chempy import Substance
from bakery import assert_equal


@dataclass
class Chemical:
    '''
    This dataclass stores information about one chemical in a reaction.

    Args:
        formula (str): The chemical formula, such as H2O.
        mass (float): The starting mass of the chemical in grams.
        molar_mass (float): The molar mass in grams per mole.
        coefficient (int): The coefficient from the balanced equation.
    Returns:
        None: This dataclass stores chemical information.
    '''
    formula: str
    mass: float
    molar_mass: float
    coefficient: int


@dataclass
class State:
    '''
    This dataclass stores the information entered by the user.

    Args:
        equation (str): The balanced chemical equation.
        reactants (list[Chemical]): The reactants and their starting masses.
        products (list[Chemical]): The products and their coefficients.
        actual_yield (float): The actual product mass collected in grams.
        enthalpy (float): The reaction enthalpy in kilojoules.
        results (list[str]): The calculation results.
    Returns:
        None: This dataclass stores the website information.
    '''
    equation: str
    reactants: list[Chemical]
    products: list[Chemical]
    actual_yield: float
    enthalpy: float
    results: list[str]


def get_molar_mass(formula: str) -> float:
    '''
    This function uses ChemPy to calculate the molar mass of a chemical.

    Args:
        formula (str): The chemical formula, such as H2O or CO2.
    Returns:
        float: The molar mass in grams per mole.
    '''
    substance = Substance.from_formula(formula)
    return float(substance.mass)


def calculate_limiting_extent(reactants: list[Chemical]) -> float:
    '''
    This function finds how many reaction units the reactants can produce.

    Args:
        reactants (list[Chemical]): The reactants with their masses
            and balanced equation coefficients.
    Returns:
        float: The number of reaction units allowed by the limiting reactant.
    '''
    limiting_extent = -1.0

    for chemical in reactants:
        available_moles = chemical.mass / chemical.molar_mass
        possible_extent = available_moles / chemical.coefficient

        if limiting_extent == -1.0:
            limiting_extent = possible_extent
        elif possible_extent < limiting_extent:
            limiting_extent = possible_extent

    return limiting_extent


def calculate_results(state: State) -> list[str]:
    '''
    This function calculates the limiting reactant, theoretical yield,
    percent yield, leftover reactant masses, and reaction heat information.

    Args:
        state (State): The saved equation, chemicals, and reaction information.
    Returns:
        list[str]: A list of calculation results to display to the user.
    '''
    results = []

    if len(state.reactants) == 0:
        return ["Please add at least one reactant before calculating."]

    if len(state.products) == 0:
        return ["Please add at least one product before calculating."]

    if state.actual_yield < 0:
        return ["Actual product mass cannot be negative."]

    limiting_extent = calculate_limiting_extent(state.reactants)

    if limiting_extent <= 0:
        return ["Reactant masses must be greater than zero."]

    product = state.products[0]

    theoretical_product_moles = limiting_extent * product.coefficient
    theoretical_product_mass = (
        theoretical_product_moles * product.molar_mass
    )

    limiting_formula = ""

    for chemical in state.reactants:
        available_moles = chemical.mass / chemical.molar_mass
        possible_extent = available_moles / chemical.coefficient

        if possible_extent == limiting_extent:
            limiting_formula = chemical.formula

    results.append("LIMITING REACTANT")
    results.append(limiting_formula)

    results.append("THEORETICAL YIELD")
    results.append(
        str(round(theoretical_product_mass, 2))
        + " g of "
        + product.formula
    )

    if theoretical_product_mass > 0:
        percent_yield = (
            state.actual_yield / theoretical_product_mass
        ) * 100

        results.append("PERCENT YIELD")
        results.append(str(round(percent_yield, 2)) + "%")

    results.append("LEFTOVER REACTANTS")

    for chemical in state.reactants:
        starting_moles = chemical.mass / chemical.molar_mass
        used_moles = limiting_extent * chemical.coefficient
        leftover_moles = starting_moles - used_moles
        leftover_mass = leftover_moles * chemical.molar_mass

        if leftover_mass < 0:
            leftover_mass = 0

        results.append(
            chemical.formula
            + ": "
            + str(round(leftover_mass, 2))
            + " g remaining"
        )

    results.append("REACTION HEAT")

    if state.enthalpy < 0:
        results.append("Reaction type: Exothermic (releases heat)")
    elif state.enthalpy > 0:
        results.append("Reaction type: Endothermic (absorbs heat)")
    else:
        results.append("Reaction type: No heat change entered")

    heat_per_mole = state.enthalpy / product.coefficient

    results.append(
        "Heat per mole of "
        + product.formula
        + ": "
        + str(round(heat_per_mole, 2))
        + " kJ/mol"
    )

    return results


# Tests for the calculation helper functions.

assert_equal(round(get_molar_mass("H2O"), 2), 18.02)

test_reactants = [
    Chemical("H2", 4.0, get_molar_mass("H2"), 2),
    Chemical("O2", 32.0, get_molar_mass("O2"), 1)
]

assert_equal(
    round(calculate_limiting_extent(test_reactants), 2),
    0.99
)


@route
def index(state: State) -> Page:
    '''
    This route displays the home page and explains the website.

    Args:
        state (State): The current website information.
    Returns:
        Page: The home page with instructions and a start button.
    '''
    return Page(
        state,
        [
            Header("Chemistry Stoichiometry Assistant"),
            Text("A step-by-step helper for balanced chemical reactions."),
            HorizontalRule(),

            Header("What can this website calculate?", 2),
            BulletedList([
                "The limiting reactant",
                "The theoretical product yield",
                "The percent yield",
                "The leftover mass of each reactant",
                "Whether the reaction is exothermic or endothermic"
            ]),

            HorizontalRule(),
            Header("What information do you need?", 2),
            BulletedList([
                "A balanced chemical equation",
                "The starting mass of each reactant in grams",
                "The coefficient for each chemical",
                "The actual product mass collected in grams",
                "The reaction enthalpy in kJ"
            ]),

            Header("Important input instructions", 2),
            Text(
                "Type chemical formulas using regular numbers instead "
                "of subscripts. For example, type H2O instead of H₂O."
            ),
            Text(
                "Make sure your equation is balanced before continuing. "
                "This website uses the coefficients you enter."
            ),

            Button("Start Calculations", "equation_page")
        ]
    )


@route
def equation_page(state: State) -> Page:
    '''
    This route asks the user to enter the balanced chemical equation.

    Args:
        state (State): The current website information.
    Returns:
        Page: A page with a text box for the balanced equation.
    '''
    return Page(
        state,
        [
            Header("STEP 1 OF 4: Enter Your Equation"),
            Text("Enter the complete balanced chemical equation."),
            Header("Example", 2),
            Pre("2 H2 + O2 -> 2 H2O"),
            Text(
                "Include the numbers in front of each chemical formula. "
                "You will enter the individual chemicals on the next pages."
            ),
            Header("Your balanced equation:", 2),
            TextBox("equation", state.equation),
            Button("Save Equation and Continue", "save_equation"),
            Button("Back to Home", "index")
        ]
    )


@route
def save_equation(state: State, equation: str) -> Page:
    '''
    This route saves the balanced equation entered by the user.

    Args:
        state (State): The current website information.
        equation (str): The balanced chemical equation.
    Returns:
        Page: The reactant entry page.
    '''
    state.equation = equation
    return reactants_page(state)


@route
def reactants_page(state: State) -> Page:
    '''
    This route displays saved reactants and a form to add another reactant.

    Args:
        state (State): The current website information.
    Returns:
        Page: The reactant entry page with labeled input fields.
    '''
    content = [
        Header("STEP 2 OF 4: Enter Your Reactants"),
        Text(
            "Add every reactant from your balanced equation. "
            "Enter one reactant at a time."
        ),

        HorizontalRule(),
        Header("What should you type?", 2),

        Text("1. Chemical formula"),
        Text("Type the formula exactly as it appears in your equation."),
        Text("Example: H2"),

        Text("2. Starting mass (grams)"),
        Text(
            "Enter how many grams of this reactant you started with. "
            "Only enter the number, not the unit."
        ),
        Text("Example: 4.0"),

        Text("3. Balanced equation coefficient"),
        Text(
            "Enter the whole number in front of the formula. "
            "If there is no number, enter 1."
        ),
        Text("Example: In 2 H2 + O2, the H2 coefficient is 2."),

        HorizontalRule(),
        Header("Reactants You Have Added", 2)
    ]

    if len(state.reactants) == 0:
        content.append(Text("You have not added any reactants yet."))

    for chemical in state.reactants:
        content.append(
            Text(
                chemical.formula
                + " | Starting mass: "
                + str(chemical.mass)
                + " g | Coefficient: "
                + str(chemical.coefficient)
                + " | Molar mass: "
                + str(round(chemical.molar_mass, 2))
                + " g/mol"
            )
        )

    content.extend([
        HorizontalRule(),
        Header("Add a Reactant", 2),

        Text("Chemical formula:"),
        TextBox("formula", ""),

        Text("Starting mass in grams:"),
        TextBox("mass", "0"),

        Text("Balanced equation coefficient:"),
        TextBox("coefficient", "1"),

        Button("Add This Reactant", "add_reactant"),

        HorizontalRule(),
        Button("Continue to Products", "products_page"),
        Button("Back to Equation", "equation_page")
    ])

    return Page(state, content)


@route
def add_reactant(
    state: State,
    formula: str,
    mass: float,
    coefficient: int
) -> Page:
    '''
    This route checks and saves one reactant entered by the user.

    Args:
        state (State): The current website information.
        formula (str): The reactant's chemical formula.
        mass (float): The starting mass of the reactant in grams.
        coefficient (int): The reactant's balanced equation coefficient.
    Returns:
        Page: The reactant page showing the updated reactant list.
    '''
    if formula.strip() == "":
        return reactants_page(state)

    if mass <= 0 or coefficient <= 0:
        return reactants_page(state)

    molar_mass = get_molar_mass(formula.strip())

    chemical = Chemical(
        formula.strip(),
        mass,
        molar_mass,
        coefficient
    )

    state.reactants.append(chemical)

    return reactants_page(state)


@route
def products_page(state: State) -> Page:
    '''
    This route displays saved products and a form to add a product.

    Args:
        state (State): The current website information.
    Returns:
        Page: The product entry page with labeled input fields.
    '''
    content = [
        Header("STEP 3 OF 4: Enter Your Product"),
        Text(
            "Enter the product you want to calculate the yield for. "
            "This version calculates the first product you add."
        ),

        HorizontalRule(),
        Header("What should you type?", 2),

        Text("1. Product chemical formula"),
        Text("Type the product formula from your balanced equation."),
        Text("Example: H2O"),

        Text("2. Balanced equation coefficient"),
        Text(
            "Enter the whole number in front of the product formula. "
            "If there is no number, enter 1."
        ),
        Text("Example: In 2 H2 + O2 -> 2 H2O, the coefficient is 2."),

        HorizontalRule(),
        Header("Products You Have Added", 2)
    ]

    if len(state.products) == 0:
        content.append(Text("You have not added a product yet."))

    for chemical in state.products:
        content.append(
            Text(
                chemical.formula
                + " | Coefficient: "
                + str(chemical.coefficient)
                + " | Molar mass: "
                + str(round(chemical.molar_mass, 2))
                + " g/mol"
            )
        )

    content.extend([
        HorizontalRule(),
        Header("Add a Product", 2),

        Text("Product chemical formula:"),
        TextBox("formula", ""),

        Text("Balanced equation coefficient:"),
        TextBox("coefficient", "1"),

        Button("Add This Product", "add_product"),

        HorizontalRule(),
        Button("Continue to Reaction Information", "reaction_info"),
        Button("Back to Reactants", "reactants_page")
    ])

    return Page(state, content)


@route
def add_product(
    state: State,
    formula: str,
    coefficient: int
) -> Page:
    '''
    This route checks and saves one product entered by the user.

    Args:
        state (State): The current website information.
        formula (str): The product's chemical formula.
        coefficient (int): The product's balanced equation coefficient.
    Returns:
        Page: The product page showing the updated product list.
    '''
    if formula.strip() == "":
        return products_page(state)

    if coefficient <= 0:
        return products_page(state)

    molar_mass = get_molar_mass(formula.strip())

    chemical = Chemical(
        formula.strip(),
        0.0,
        molar_mass,
        coefficient
    )

    state.products.append(chemical)

    return products_page(state)


@route
def reaction_info(state: State) -> Page:
    '''
    This route asks for the actual product mass and reaction enthalpy.

    Args:
        state (State): The current website information.
    Returns:
        Page: A page with clearly labeled reaction information fields.
    '''
    return Page(
        state,
        [
            Header("STEP 4 OF 4: Reaction Information"),

            HorizontalRule(),
            Header("Actual Product Mass", 2),
            Text(
                "How many grams of product did you actually collect? "
                "Enter only the number."
            ),
            Text("Example: If you collected 3.5 grams, type 3.5."),
            TextBox("actual_yield", "0"),

            HorizontalRule(),
            Header("Reaction Enthalpy", 2),
            Text(
                "Enter the enthalpy change for the balanced reaction "
                "in kilojoules (kJ)."
            ),
            Text("Use a negative number if the reaction releases heat."),
            Text("Use a positive number if the reaction absorbs heat."),
            Text("Examples: -500 or 250"),
            TextBox("enthalpy", "0"),

            HorizontalRule(),
            Text(
                "Check that both numbers are entered correctly "
                "before calculating."
            ),
            Button("Calculate My Results", "calculate"),
            Button("Back to Products", "products_page")
        ]
    )


@route
def calculate(
    state: State,
    actual_yield: float,
    enthalpy: float
) -> Page:
    '''
    This route saves the reaction information and calculates the results.

    Args:
        state (State): The current website information.
        actual_yield (float): The actual product mass collected in grams.
        enthalpy (float): The reaction enthalpy in kilojoules.
    Returns:
        Page: The results page with the completed calculations.
    '''
    state.actual_yield = actual_yield
    state.enthalpy = enthalpy
    state.results = calculate_results(state)

    return results_page(state)


@route
def results_page(state: State) -> Page:
    '''
    This route displays the stoichiometry calculation results.

    Args:
        state (State): The current website information and results.
    Returns:
        Page: A formatted report of the stoichiometry calculations.
    '''
    content = [
        Header("Your Stoichiometry Results"),

        Header("Balanced Equation", 2),
        Text(state.equation),

        HorizontalRule()
    ]

    for result in state.results:
        if (
            result == "LIMITING REACTANT"
            or result == "THEORETICAL YIELD"
            or result == "PERCENT YIELD"
            or result == "LEFTOVER REACTANTS"
            or result == "REACTION HEAT"
        ):
            content.append(Header(result, 2))
        else:
            content.append(Text(result))

    content.extend([
        HorizontalRule(),
        Header("Before Using These Results", 2),
        Text(
            "Double-check that your equation is balanced and that "
            "you entered all masses, coefficients, and units correctly."
        ),
        Button("Start a New Calculation", "reset"),
        Button("Return to Home", "index")
    ])

    return Page(state, content)


@route
def reset(state: State) -> Page:
    '''
    This route clears the saved information and starts a new calculation.

    Args:
        state (State): The current website information.
    Returns:
        Page: The home page with all calculation information cleared.
    '''
    state.equation = ""
    state.reactants = []
    state.products = []
    state.actual_yield = 0.0
    state.enthalpy = 0.0
    state.results = []

    return index(state)


initial_state = State(
    "",
    [],
    [],
    0.0,
    0.0,
    []
)

start_server(initial_state)

