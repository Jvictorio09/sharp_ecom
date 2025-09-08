# utils.py or forms.py
from django_countries import countries

# Middle East + USA (add/remove as needed)
SHIP_TO = [
    "AE", "SA", "QA", "KW", "OM", "BH", "JO", "LB", "EG", "US"
]

SHIP_TO_COUNTRIES = [(code, dict(countries)[code]) for code in SHIP_TO]
