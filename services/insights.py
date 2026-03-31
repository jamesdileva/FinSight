from collections import defaultdict
from openai import OpenAI
# ------------------------
# MAIN FUNCTION
# ------------------------
def generate_insights(transactions, all_transactions=None):
    if not transactions:
        return ["No data yet"]

    insights = []

    # ------------------------
    # SPLIT DATA (FIX)
    # ------------------------
    expenses = [t for t in transactions if t["amount"] > 0 and t["category"] != "Income"]
    income = [t for t in transactions if t["category"] == "Income"]
    refunds = [t for t in transactions if t["amount"] < 0]

    # ------------------------
    # TOTALS
    # ------------------------
    total_spent = sum(t["amount"] for t in expenses)
    total_income = sum(t["amount"] for t in income)
    total_refunds = abs(sum(t["amount"] for t in refunds))

    insights.append(f"Total spending: ${total_spent:.2f}")

    if total_income > 0:
        insights.append(f"Total income: ${total_income:.2f}")

    if total_refunds > 0:
        insights.append(f"Refunds: -${total_refunds:.2f}")

    # % of total spending (based on expenses only)
    if all_transactions:
        all_expenses = [
            t for t in all_transactions
            if t["amount"] > 0 and t["category"] != "Income"
        ]
        total_all = sum(t["amount"] for t in all_expenses)

        if total_all > 0 and total_spent != total_all:
            percent_total = (total_spent / total_all) * 100
            insights.append(f"This is {percent_total:.1f}% of total spending")

    # ------------------------
    # CATEGORIES (EXPENSES ONLY)
    # ------------------------
    categories = defaultdict(float)
    for t in expenses:
        categories[t["category"]] += t["amount"]

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

    return insights


# ------------------------
# HELPERS (DO NOT REMOVE)
# ------------------------

def monthly_spending(transactions):
    months = defaultdict(float)
    for t in transactions:
        months[t["date"][:7]] += t["amount"]
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