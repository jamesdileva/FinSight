from collections import defaultdict


def generate_insights(transactions, all_transactions=None):
    if not transactions:
        return ["No data yet"]

    insights = []

    # ------------------------
    # Total Spending
    # ------------------------
    total = sum(t["amount"] for t in transactions)
    insights.append(f"Total spending: ${total:.2f}")

    if all_transactions:
        total_all = sum(t["amount"] for t in all_transactions)
        if total_all > 0:
            percent_total = (total / total_all) * 100
            insights.append(f"This is {percent_total:.1f}% of total spending")

    # ------------------------
    # Categories
    # ------------------------
    categories = defaultdict(float)
    for t in transactions:
        categories[t["category"]] += t["amount"]

    total_cat = sum(categories.values())

    top = max(categories, key=categories.get)
    percent = (categories[top] / total_cat) * 100
    insights.append(f"Top category: {top} ({percent:.1f}%)")

    single_category = len(categories) == 1
    if single_category:
        insights.append("Viewing a single category")

    # ------------------------
    # Monthly
    # ------------------------
    months = monthly_spending(transactions)

    insights.append(spending_trend(months))

    # ------------------------
    # Growth
    # ------------------------
    growth = monthly_growth_rate(months)
    if growth is not None:
        if growth > 0:
            insights.append(f"Spending increased by {growth}%")
        else:
            insights.append(f"Spending decreased by {abs(growth)}%")

    # ------------------------
    # Spike
    # ------------------------
    spike = detect_spike(months)
    if spike:
        insights.append(spike)

    # ------------------------
    # Category comparison
    # ------------------------
    if not single_category:
        largest = max(categories, key=categories.get)
        smallest = min(categories, key=categories.get)

        insights.append(f"Highest spending category: {largest}")
        insights.append(f"Lowest spending category: {smallest}")

    # ------------------------
    # Filter-specific insight
    # ------------------------
    if single_category and len(months) > 0:
        avg = total / len(months)
        insights.append(f"Average monthly spending: ${avg:.2f}")

    return insights


# ------------------------
# Helpers
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

    if months[keys[-1]] > months[keys[0]]:
        return "Spending is increasing over time"
    return "Spending is decreasing over time"


def monthly_growth_rate(months):
    keys = sorted(months.keys())
    if len(keys) < 2:
        return None

    first = months[keys[0]]
    last = months[keys[-1]]

    if first == 0:
        return None

    return round(((last - first) / first) * 100, 2)


def detect_spike(months):
    keys = sorted(months.keys())

    for i in range(1, len(keys)):
        prev = months[keys[i-1]]
        curr = months[keys[i]]

        if prev == 0:
            continue

        change = ((curr - prev) / prev) * 100

        if change > 20:
            return f"Spending spiked in {keys[i]} (+{round(change,1)}%)"
        elif change < -20:
            return f"Spending dropped sharply in {keys[i]} ({round(change,1)}%)"

    return None