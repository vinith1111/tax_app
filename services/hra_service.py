def calculate_hra(salary, hra_received, rent, is_metro):

    rent_annual = rent * 12
    rent_minus_10 = max(rent_annual - (0.1 * salary), 0)
    salary_limit = 0.5 * salary if is_metro else 0.4 * salary

    exempt = min(hra_received, rent_minus_10, salary_limit)
    taxable = max(hra_received - exempt, 0)

    return round(exempt), round(taxable)
