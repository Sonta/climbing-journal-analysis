# %%
import re

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

# %%


# Define a function to classify weighing factors
def classify_weighing_factor(factor):
    if re.match(
        r"^[0-9]+[+-]?$|^[0-9]+$", str(factor)
    ):  # Matches numeric group (e.g., "4", "5+", "5-")
        return "Numeric Group"
    elif re.match(
        r"^[0-9]+[a-z]+$", str(factor), re.IGNORECASE
    ):  # Matches alpha group (e.g., "4a", "4b", "4c")
        return "Alpha Group"
    else:
        return "Unknown"


# Define a function to sort weighing factors
def sort_weighing_factor(factor):
    try:
        # Check for numeric weighing factors
        if re.match(
            r"^[0-9]+[+-]?$|^[0-9]+$", str(factor)
        ):  # Matches "4", "5-", "5+" etc.
            if "+" in str(factor):
                return (int(str(factor).replace("+", "")), 1)  # Sort "+" as higher
            elif "-" in str(factor):
                return (int(str(factor).replace("-", "")), -1)  # Sort "-" as lower
            else:
                return (int(str(factor)), 0)  # No suffix
        # Check for alpha group weighing factors
        elif re.match(
            r"^[0-9]+[a-z]+$", str(factor), re.IGNORECASE
        ):  # Matches "4a", "4b", "4c"
            return (
                int(str(factor)[:-1]),
                str(factor)[-1],
            )  # Sort by number and then alphabetically
        else:
            return (
                float("inf"),
                str(factor),
            )  # For unknown weighing factors, push them to the end
    except TypeError as e:
        print(factor)


# %%

# Path to your Excel file
file_path = "./data/Kletter-Tagebuch.xlsx"

# Load all sheets into a dictionary
sheets_dict = pd.read_excel(file_path, sheet_name=None)

# Initialize an empty list to store DataFrames
dataframes = []

# Process each sheet
for sheet_name, df in sheets_dict.items():
    # Extract month and year from the sheet name
    month = int(sheet_name[:2])  # First 2 characters are the month
    year = 2000 + int(sheet_name[2:])  # Last 2 characters are the year (assumes 2000+)

    # Melt the DataFrame to transform columns (days) into rows
    melted_df = df.melt(id_vars="Datum", var_name="Day", value_name="n_climbs")
    melted_df.rename({"Datum": "difficulty"}, axis=1, inplace=True)
    melted_df.dropna(inplace=True)
    melted_df = melted_df[melted_df["n_climbs"] != 0]

    # Add year, month, and a date column
    melted_df["Year"] = year
    melted_df["Month"] = month
    melted_df["date"] = pd.to_datetime(
        melted_df[["Year", "Month"]].assign(Day=melted_df["Day"])
    )

    # Append the processed DataFrame to the list
    dataframes.append(melted_df)

# Combine all the DataFrames into a single DataFrame
final_df = pd.concat(dataframes, ignore_index=True)

# Drop unnecessary columns (e.g., Year and Month, if not needed)
final_df = final_df[["date", "n_climbs", "difficulty"]]

# Display the result
print(final_df)
# %%

# Apply classification to create a new column
final_df["Group"] = final_df["difficulty"].apply(classify_weighing_factor)

final_df["Month-Year"] = final_df["date"].dt.to_period("M")
numeric_group_df = final_df[final_df["Group"] == "Numeric Group"]

# Group by Month-Year and Weighing Factor
monthly_factor_evolution = numeric_group_df.groupby(
    ["Month-Year", "difficulty"], as_index=False
)["n_climbs"].mean()

# Convert Month-Year back to a datetime object
monthly_factor_evolution["Month-Year"] = monthly_factor_evolution[
    "Month-Year"
].dt.to_timestamp()

# Plot with separate lines for each weighing factor
plt.figure(figsize=(12, 6))
sns.lineplot(
    data=monthly_factor_evolution,
    x="Month-Year",
    y="n_climbs",
    hue="difficulty",
    marker="o",
    # palette="viridis",
    hue_order=sorted(numeric_group_df["difficulty"].unique(), key=sort_weighing_factor),
)

# Customize the plot
plt.title("Evolution of Average n_climbs Across Months by difficulty", fontsize=16)
plt.xlabel("Month-Year", fontsize=14)
plt.ylabel("Average n_climbs", fontsize=14)
plt.legend(title="difficulty", fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.xticks(rotation=45)

# Show the plot
plt.tight_layout()
plt.show()
# %%
bouldering_group_df = final_df[final_df["Group"] == "Alpha Group"]

# Group by Month-Year and Weighing Factor
monthly_factor_evolution = bouldering_group_df.groupby(
    ["Month-Year", "difficulty"], as_index=False
)["n_climbs"].mean()

# Convert Month-Year back to a datetime object
monthly_factor_evolution["Month-Year"] = monthly_factor_evolution[
    "Month-Year"
].dt.to_timestamp()

# Plot with separate lines for each weighing factor
plt.figure(figsize=(12, 6))
sns.lineplot(
    data=monthly_factor_evolution,
    x="Month-Year",
    y="n_climbs",
    hue="difficulty",
    marker="o",
    # palette="viridis",
    hue_order=sorted(
        bouldering_group_df["difficulty"].unique(), key=sort_weighing_factor
    ),
)

# Customize the plot
plt.title("Evolution of Average n_climbs Across Months by difficulty", fontsize=16)
plt.xlabel("Month-Year", fontsize=14)
plt.ylabel("Average n_climbs", fontsize=14)
plt.legend(title="difficulty", fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.xticks(rotation=45)

# Show the plot
plt.tight_layout()
plt.show()
