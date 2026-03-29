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
        if total_all > 0 and total != total_all:
            percent_total = (total / total_all) * 100
            insights.append(f"This is {percent_total:.1f}% of total spending")

    # ------------------------
    # Categories
    # ------------------------
    categories = defaultdict(float)
    for t in transactions:
        categories[t["category"]] += t["amount"]

    if not categories:
        return ["No data for this category"]

    single_category = len(categories) == 1

    if not single_category:
        top = max(categories, key=categories.get)
        percent = (categories[top] / sum(categories.values())) * 100
        insights.append(f"Top category: {top} ({percent:.1f}%)")

        smallest = min(categories, key=categories.get)
        insights.append(f"Lowest spending category: {smallest}")

    # ------------------------
    # Monthly Data
    # ------------------------
    months = monthly_spending(transactions)

    # ✅ Always show highest month
    if len(months) > 0:
        highest_month = max(months, key=months.get)
        insights.append(f"Highest spending month: {highest_month}")

    # ------------------------
    # Month-to-month change
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
    # Spike detection
    # ------------------------
    spike = detect_spike(months)
    if spike:
        insights.append(spike)

    # ------------------------
    # Single category extras
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