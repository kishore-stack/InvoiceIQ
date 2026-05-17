import random
from faker import Faker
from typing import List, Dict, Any, Optional

fake = Faker()
Faker.seed(42)

CURRENCIES = ["USD", "EUR", "GBP", "INR", "AED", "SGD", "AUD", "CAD"]
CURRENCY_SYMBOLS = {
    "USD": "$", "EUR": "€", "GBP": "£", "INR": "₹",
    "AED": "AED", "SGD": "S$", "AUD": "A$", "CAD": "C$",
}
CURRENCY_WEIGHTS = [40, 20, 15, 15, 3, 3, 2, 2]

PRODUCT_DESCRIPTIONS = [
    "Web Development Services", "Software License - Annual",
    "Consulting Hours", "Cloud Hosting (Monthly)", "Database Management",
    "UI/UX Design Services", "Technical Support Plan", "Server Maintenance",
    "Security Audit & Assessment", "API Integration Work",
    "Mobile App Development", "SEO Optimization Services",
    "Data Analytics Dashboard", "Network Infrastructure Setup",
    "Hardware & Equipment Supply", "Office Supplies Bundle",
    "Marketing Campaign Management", "Legal Advisory Services",
    "Accounting & Bookkeeping", "Training & Workshop Sessions",
    "Custom Software Development - Phase 1",
    "Annual Enterprise Subscription",
    "Professional Services - Quarterly Deliverables",
    "Infrastructure Migration - Legacy to Cloud",
    "QA & Testing Services", "Content Creation Package",
    "Project Management Services", "DevOps Consulting",
    "Business Intelligence Report", "Customer Support Package",
]

PAYMENT_TERMS = [7, 14, 15, 30, 45, 60, 90]

TAX_RATES = [0, 0.05, 0.09, 0.10, 0.12, 0.18, 0.20, 0.28]
DISCOUNT_RATES = [0, 0, 0, 0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]


def pick_currency() -> str:
    return random.choices(CURRENCIES, weights=CURRENCY_WEIGHTS)[0]


def generate_company() -> Dict[str, str]:
    return {
        "name": fake.company(),
        "address": fake.street_address(),
        "city": fake.city(),
        "country": fake.country(),
        "email": fake.company_email(),
        "phone": fake.phone_number(),
        "tax_id": f"TAX-{random.randint(100000, 999999)}",
    }


def generate_line_item(inject_multiline: bool = False) -> Dict[str, Any]:
    description = random.choice(PRODUCT_DESCRIPTIONS)
    if inject_multiline and random.random() < 0.4:
        description += f" - {fake.bs().title()}"

    quantity = round(random.uniform(1, 50), 2)
    unit_price = round(random.uniform(10, 5000), 2)
    base = round(quantity * unit_price, 2)

    tax_rate = random.choice(TAX_RATES)
    discount_rate = random.choice(DISCOUNT_RATES)

    tax_amount = round(base * tax_rate, 2)
    discount_amount = round(base * discount_rate, 2)
    line_total = round(base + tax_amount - discount_amount, 2)

    return {
        "description": description,
        "quantity": quantity,
        "unit_price": unit_price,
        "tax_amount": tax_amount,
        "discount_amount": discount_amount,
        "line_total": line_total,
        "_tax_rate": tax_rate,
        "_discount_rate": discount_rate,
    }


def generate_invoice_data(
    inject_errors: Optional[List[str]] = None,
    num_items: Optional[int] = None,
    force_long: bool = False,
    force_multi_tax: bool = False,
) -> Dict[str, Any]:
    """
    Generate one synthetic invoice.

    force_long       — guarantees >=30 items so the table genuinely spans pages.
    force_multi_tax  — splits tax into a CGST/SGST/IGST breakdown rendered as
                       multiple tax rows in the totals block.
    """
    inject_errors = inject_errors or []

    currency = pick_currency()
    if force_long:
        n = random.randint(30, 40)
    elif num_items is not None:
        n = num_items
    else:
        n = random.randint(1, 40)
    inject_multiline = random.random() < 0.35
    line_items = [generate_line_item(inject_multiline) for _ in range(n)]

    true_subtotal = round(sum(item["line_total"] for item in line_items), 2)
    tax_rate = round(random.uniform(0, 0.28), 4)
    discount_rate = round(random.uniform(0, 0.30), 4)
    true_tax = round(true_subtotal * tax_rate, 2)
    true_discount = round(true_subtotal * discount_rate, 2)
    true_total = round(true_subtotal + true_tax - true_discount, 2)

    # Tax breakdown: real Indian-style invoices split a single tax into
    # CGST + SGST (intra-state) or IGST (inter-state). When force_multi_tax
    # is set we emit two or three rows that sum to the same true_tax.
    tax_breakdown: List[Dict[str, Any]] = []
    if force_multi_tax and true_tax > 0:
        style = random.choice(["cgst_sgst", "cgst_sgst_cess", "igst"])
        if style == "cgst_sgst":
            half = round(true_tax / 2, 2)
            tax_breakdown = [
                {"label": "CGST", "rate": round(tax_rate / 2, 4), "amount": half},
                {"label": "SGST", "rate": round(tax_rate / 2, 4), "amount": round(true_tax - half, 2)},
            ]
        elif style == "cgst_sgst_cess":
            cgst = round(true_tax * 0.45, 2)
            sgst = round(true_tax * 0.45, 2)
            cess = round(true_tax - cgst - sgst, 2)
            tax_breakdown = [
                {"label": "CGST", "rate": round(tax_rate * 0.45, 4), "amount": cgst},
                {"label": "SGST", "rate": round(tax_rate * 0.45, 4), "amount": sgst},
                {"label": "Cess", "rate": round(tax_rate * 0.10, 4), "amount": cess},
            ]
        else:
            tax_breakdown = [
                {"label": "IGST", "rate": tax_rate, "amount": true_tax},
            ]

    # Start with true values, then corrupt where errors are injected
    display_subtotal = true_subtotal
    display_tax = true_tax
    display_discount = true_discount
    display_total = true_total

    validation_errors: List[str] = []

    if "subtotal_mismatch" in inject_errors:
        display_subtotal = round(true_subtotal * random.uniform(1.05, 1.25), 2)
        validation_errors.append("subtotal_mismatch")

    if "tax_mismatch" in inject_errors:
        display_tax = round(true_tax * random.uniform(1.10, 1.50), 2)
        validation_errors.append("tax_mismatch")

    if "discount_mismatch" in inject_errors:
        display_discount = round(true_discount * random.uniform(1.10, 1.40), 2)
        validation_errors.append("discount_mismatch")

    if "total_mismatch" in inject_errors:
        display_total = round(true_total * random.uniform(1.05, 1.20), 2)
        validation_errors.append("total_mismatch")

    invoice_number: Optional[str] = None
    if "missing_invoice_number" in inject_errors:
        validation_errors.append("missing_invoice_number")
    else:
        invoice_number = f"INV-{fake.year()}-{random.randint(1000, 9999)}"

    if "missing_line_items" in inject_errors:
        line_items = []
        validation_errors.append("missing_line_items")

    return {
        "invoice_number": invoice_number,
        "seller": generate_company(),
        "buyer": generate_company(),
        "issue_date": fake.date_between(start_date="-2y", end_date="today").strftime("%Y-%m-%d"),
        "due_date": fake.date_between(start_date="today", end_date="+90d").strftime("%Y-%m-%d"),
        "currency": currency,
        "currency_symbol": CURRENCY_SYMBOLS[currency],
        "subtotal": display_subtotal,
        "tax_amount": display_tax,
        "tax_rate": tax_rate,
        "tax_breakdown": tax_breakdown,  # empty for non-multi-tax invoices
        "discount_amount": display_discount,
        "discount_rate": discount_rate,
        "total_amount": display_total,
        "payment_terms_days": random.choice(PAYMENT_TERMS),
        "notes": fake.sentence() if random.random() < 0.4 else None,
        "line_items": line_items,
        "validation_errors": validation_errors,
        # Ground truth for annotation (not rendered)
        "_true_subtotal": true_subtotal,
        "_true_tax": true_tax,
        "_true_discount": true_discount,
        "_true_total": true_total,
    }


def pick_error_set() -> List[str]:
    """Return a random subset of errors to inject, weighted toward no errors."""
    all_errors = [
        "subtotal_mismatch", "tax_mismatch",
        "discount_mismatch", "total_mismatch",
        "missing_invoice_number", "missing_line_items",
    ]
    roll = random.random()
    if roll < 0.70:
        return []
    elif roll < 0.85:
        return [random.choice(all_errors[:4])]  # math errors only
    elif roll < 0.95:
        return [random.choice(all_errors)]
    else:
        return random.sample(all_errors, 2)
