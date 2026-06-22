from collections import defaultdict
from openai import OpenAI
# ------------------------
# MAIN FUNCTION
# ------------------------
def generate_insights(
    transactions,
    all_transactions=None,
    budgets=None
):
    if not transactions:
        return ["No data yet"]

    insights = []

    # ------------------------
    # SPLIT DATA (FIX)
    # ------------------------
    expenses = [
        t for t in transactions
        if float(float(t["amount"] or 0) or 0) > 0
        and t["category"] != "Income"
    ]

    income = [
        t for t in transactions
        if t["category"] == "Income"
    ]

    refunds = [
        t for t in transactions
        if float(float(t["amount"] or 0) or 0) < 0
    ]

    # ------------------------
    # TOTALS
    # ------------------------
    total_spent = sum(float(t["amount"] or 0) for t in expenses)
    total_income = sum(float(t["amount"] or 0) for t in income)
    total_refunds = abs(sum(float(t["amount"] or 0) for t in refunds))

    insights.append(f"Total spending: ${total_spent:.2f}")

    if total_income > 0:
        insights.append(f"Total income: ${total_income:.2f}")

    if total_refunds > 0:
        insights.append(f"Refunds: -${total_refunds:.2f}")

    # % of total spending (based on expenses only)
    if all_transactions:
        all_expenses = [
            t for t in all_transactions
            if float(t["amount"] or 0) > 0 and t["category"] != "Income"
        ]
        total_all = sum(float(t["amount"] or 0) for t in all_expenses)

        if total_all > 0 and total_spent != total_all:
            percent_total = (total_spent / total_all) * 100
            insights.append(f"This is {percent_total:.1f}% of total spending")

    # ------------------------
    # CATEGORIES (EXPENSES ONLY)
    # ------------------------
    categories = defaultdict(float)
    for t in expenses:
        categories[t["category"]] += float(t["amount"] or 0)

    if not categories:
        insights.append("No spending data for this selection")
        return insights

    single_category = len(categories) == 1

    if not single_category:
        top = max(categories, key=categories.get)
        percent = (categories[top] / sum(categories.values())) * 100
        insights.append(f"Top category: {top} ({percent:.1f}%)")

        smallest = min(categories, key=categories.get)
        insights.append(f"Lowest spending category: {smallest}")

    # ------------------------
    # MONTHLY (EXPENSES ONLY)
    # ------------------------
    months = monthly_spending(expenses)

    if len(months) > 0:
        highest_month = max(months, key=months.get)
        insights.append(f"Highest spending month: {highest_month}")

    # ------------------------
    # GROWTH
    # ------------------------
    growth = monthly_growth_rate(months)

    if growth is not None:
        last_month = sorted(months.keys())[-1]

        if growth > 0:
            insights.append(f"Last month ({last_month}) increased by {growth:.2f}%")
        else:
            insights.append(f"Last month ({last_month}) decreased by {abs(growth):.2f}%")
    else:
        insights.append(spending_trend(months))

    # ------------------------
    # SPIKE
    # ------------------------
    spike = detect_spike(months)
    if spike:
        insights.append(spike)

    # ------------------------
    # SINGLE CATEGORY BONUS
    # ------------------------
    if single_category and len(months) > 0:
        avg = total_spent / len(months)
        insights.append(f"Average monthly spending: ${avg:.2f}")
    
    recurring = detect_recurring(expenses)

    insights.extend(recurring)
    budget_insights = analyze_budgets(transactions, budgets)

    insights.extend(budget_insights)

    
    return insights


# ------------------------
# HELPERS (DO NOT REMOVE)
# ------------------------

def monthly_spending(transactions):
    months = defaultdict(float)
    for t in transactions:
        months[t["date"][:7]] += float(t["amount"] or 0)
    return months


def spending_trend(months):
    keys = sorted(months.keys())

    if len(keys) < 2:
        return "Not enough data for trends"

    avg = sum(months.values()) / len(months)

    if months[keys[-1]] > avg:
        return "Spending is trending upward"
    return "Spending is trending downward"


def monthly_growth_rate(months):
    keys = sorted(months.keys())

    if len(keys) < 2:
        return None

    last = months[keys[-1]]
    prev = months[keys[-2]]

    if prev == 0:
        return None

    return round(((last - prev) / prev) * 100, 2)


def detect_spike(months):
    keys = sorted(months.keys())

    for i in range(1, len(keys)):
        prev = months[keys[i - 1]]
        curr = months[keys[i]]

        if prev == 0:
            continue

        change = ((curr - prev) / prev) * 100

        if change > 20:
            return f"Spending spiked in {keys[i]} (+{round(change,1)}%)"
        elif change < -20:
            return f"Spending dropped in {keys[i]} ({round(change,1)}%)"

    return None
## OPEN AI INSIGHTS TO COME WITH API
##client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def detect_recurring(transactions):

    recurring = []

    grouped = defaultdict(list)
    
    for t in transactions:

        key = (
            t["description"].strip().lower(),
            round(abs(float(float(t["amount"] or 0))), 2)
        )

        grouped[key].append(t)

    for (description, amount), items in grouped.items():

        if len(items) >= 3 and description:

            recurring.append(
                f"Recurring expense detected: "
                f"{description.title()} "
                f"(${amount:.2f}) "
                f"{len(items)} times"
            )

    return recurring

def analyze_budgets(transactions, budgets):

    insights = []

    if not budgets:
        return insights

   
    current_month = max(
        t["date"][:7]
        for t in transactions
    )

    if not current_month:
        return insights

    # Calculate spending by category
    category_totals = defaultdict(float)

    for t in transactions:

        if t["date"].startswith(current_month):

            amount = float(float(t["amount"] or 0))

            # Ignore income/refunds
            if amount <= 0:
                continue

            normalized = t["category"].strip().lower()

            category_totals[normalized] += amount

    # Compare against budgets
    for budget in budgets:

        category = budget["category"]
        limit = float(budget["monthly_limit"])

        spent = category_totals.get(category.strip().lower(), 0)

        if limit <= 0:
            continue

        percent = (spent / limit) * 100

        if percent >= 100:

            insights.append(
                f"{category} exceeded budget by "
                f"${spent - limit:.2f}"
            )

        elif percent >= 80:

            insights.append(
                f"{category} budget at "
                f"{percent:.0f}%"
            )

    return insights    

def generate_ai_insights(total_spent, total_income, categories, months):
    try:
        prompt = f"""
        You are a financial assistant.

        Data:
        - Total spending: {total_spent}
        - Total income: {total_income}
        - Categories: {dict(categories)}
        - Monthly spending: {dict(months)}

        Give 3 short, helpful financial insights.
        Keep them simple and human.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.choices[0].message.content

        return text.split("\n")

    except Exception as e:
        print("AI error:", e)
        return []