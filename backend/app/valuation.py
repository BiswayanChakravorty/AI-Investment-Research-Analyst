def scenario_value(revenue,growth_pct,margin_pct,exit_multiple):
    forward_revenue=revenue*(1+growth_pct/100); return forward_revenue*(margin_pct/100)*exit_multiple
