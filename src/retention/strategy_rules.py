def build_retention_actions(customer: dict) -> list[str]:
    """
    Generate rule-based retention actions for a customer based on available fields.
    """
    actions = []

    contract_type = customer.get("contract_type")
    tenure = customer.get("tenure")
    monthly_charges = customer.get("monthly_charges")
    has_partner = customer.get("has_partner")
    has_dependents = customer.get("has_dependents")

    # Contract-based recommendation
    if contract_type == "Month-to-month":
        actions.append(
            "Offer an incentive to migrate to a longer-term contract, such as an annual plan discount or loyalty reward."
        )

    # Tenure-based recommendation
    if tenure is not None and tenure <= 3:
        actions.append(
            "Provide proactive onboarding support and early follow-up to strengthen engagement during the first months."
        )

    # Monthly charges-based recommendation
    if monthly_charges is not None and monthly_charges >= 80:
        actions.append(
            "Review pricing sensitivity and consider a discount, bundle, or plan optimization offer."
        )

    # Household engagement-based recommendation
    if has_partner == "No" and has_dependents == "No":
        actions.append(
            "Use a personalized engagement campaign focused on individual customer value and service relevance."
        )

    # Fallback recommendation
    if not actions:
        actions.append(
            "Schedule proactive outreach to understand dissatisfaction and reinforce the value of the service."
        )

    return actions


def attach_retention_actions(customers: list[dict]) -> list[dict]:
    """
    Add rule-based retention actions to each customer record.
    """
    enriched_customers = []

    for customer in customers:
        enriched_customer = customer.copy()
        enriched_customer["recommended_actions"] = build_retention_actions(customer)
        enriched_customers.append(enriched_customer)

    return enriched_customers