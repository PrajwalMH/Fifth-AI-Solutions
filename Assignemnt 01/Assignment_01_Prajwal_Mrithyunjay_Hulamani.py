# ASSIGNMENT 01
# Name : PRAJWAL MRITHYUNJAY HULAMANI

scenarios = [
    ("Send a reminder email 3 days before invoice due date", None),
    ("Predict which invoices will be paid late", None),
    ("Show total revenue by region last quarter", None),
    ("Approve an expense claim if it is under $500 and has a receipt", None),
    ("Automatically back up the database every midnight", None),
    ("Calculate the average customer support response time last month", None),
    ("Recommend products based on a customer's previous purchases", None),
    ("Lock a user account after five failed login attempts", None),
    ("Send an onboarding checklist when a new employee account is created", None),
    ("Forecast next month's sales using previous sales data", None),
]


def classify(description):
    """Return 'rule', 'automation', 'analytics' or 'learning'."""

    text = description.lower()

    # Learning involves prediction, forecasting, or recommendations.
    if any(word in text for word in ["predict", "forecast", "recommend"]):
        return "learning"

    # Analytics summarizes or calculates information from existing data.
    if any(word in text for word in ["total revenue", "average", "show total"]):
        return "analytics"

    # Rules use fixed conditions or thresholds.
    if any(word in text for word in [" if ", "after five", "under $"]):
        return "rule"

    # Automation performs an action automatically when triggered or scheduled.
    if any(word in text for word in
           ["reminder", "automatically", "every midnight", "onboarding checklist"]):
        return "automation"

    return "rule"


def explain(category):
    """Explain why a scenario belongs to a category."""

    explanations = {
        "rule":
            "It uses fixed conditions or predefined logic to make a decision.",

        "automation":
            "It automatically performs a predefined action when a time or event triggers it.",

        "analytics":
            "It summarizes or analyzes existing data to provide information or insights.",

        "learning":
            "It uses historical data or patterns to make predictions or recommendations."
    }

    return explanations[category]


for description, _ in scenarios:
    category = classify(description)

    print("Scenario:", description)
    print("Classification:", category)
    print("Why:", explain(category))
    print()
