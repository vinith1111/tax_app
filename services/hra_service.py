def calculate_hra(basic_annual, hra_received_annual, rent_annual, is_metro):
    """
    All monetary inputs are annual values.
    """
    rent_minus_10 = max(rent_annual - (0.1 * basic_annual), 0)
    salary_limit = (0.5 if is_metro else 0.4) * basic_annual

    exempt = min(hra_received_annual, rent_minus_10, salary_limit)
    taxable = max(hra_received_annual - exempt, 0)

    return {
        "exempt": round(exempt),
        "taxable": round(taxable),
        "hra_received": round(hra_received_annual),
        "rent_annual": round(rent_annual),
        "rent_minus_10": round(rent_minus_10),
        "salary_limit": round(salary_limit),
        "salary": round(basic_annual),
    }
