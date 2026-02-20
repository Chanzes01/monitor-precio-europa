def calculate_transaction_cost(price_origin, transport_cost_hl, taxes_hl=0):
    """
    Calculates the total estimated transaction cost per hectoliter.
    
    Args:
        price_origin (float): Price at origin (EUR/hl).
        transport_cost_hl (float): Estimated transport cost (EUR/hl).
        taxes_hl (float): Applicable taxes/duties (EUR/hl).
        
    Returns:
        float: Total cost at destination.
    """
    return price_origin + transport_cost_hl + taxes_hl

def check_opportunity(total_cost_at_dest, price_at_dest, min_margin_hl=2.0):
    """
    Determines if there is a trade opportunity.
    
    Args:
        total_cost_at_dest (float): Calculated cost to bring wine to destination.
        price_at_dest (float): Market price at destination.
        min_margin_hl (float): Minimum desired margin per hl to consider it an opportunity.
        
    Returns:
        dict: Opportunity details or None.
    """
    potential_margin = price_at_dest - total_cost_at_dest
    is_opportunity = potential_margin >= min_margin_hl
    
    return {
        "is_opportunity": is_opportunity,
        "margin_eur_hl": round(potential_margin, 2),
        "total_cost": round(total_cost_at_dest, 2)
    }

# Estimated defaults (Can be updated via config or DB)
# Transport estimation (e.g., tanker truck 250HL)
# These are rough estimates for logic testing.
DEFAULT_TRANSPORT_COSTS = {
    ("ES", "FR"): 3.5,  # Spain to France ~3.5 EUR/hl
    ("ES", "IT"): 5.5,  # Spain to Italy ~5.5 EUR/hl
}
