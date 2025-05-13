import pandas as pd
import numpy as np

tukey_q1_percentile = 0.25
tukey_q3_percentile = 0.75
tukey_iqr_multiplier = 1.5
gdp_column = "GDP_per_capita_PPP"

# Loading csv files
df_gdp = pd.read_csv("gdp_per_capita_2021.csv", na_values=["None"])
df_pop = pd.read_csv("population_2021.csv", na_values=["None"])

"""
removing "the" from country names and normalizing them to a certain format
"   The netherlands " -> "Netherlands"
returning the corrected dataframe
"""
def normalize_country_names(df):
    df["Country"] = (df["Country"].
                     str.replace("^the ", "", case=False, regex=True).
                     str.title().
                     str.strip())
    return df

"""
Cleaning the GDP df
a) Converting GDP to numeric
b) Removing rows with missing GDP
c) Identifying outliers using Tukey method
d) Removing duplicates
e) Normalizing country names
f) Setting index to Country
"""
def clean_gdp(df_gdp):
    # a)
    df_gdp[gdp_column] = (
        df_gdp[gdp_column]
        .astype(str)
        .str.replace(",", "")
        .str.replace("$", "")
    )
    # coercing errors to NaN
    df_gdp[gdp_column] = pd.to_numeric(df_gdp[gdp_column], errors='coerce')

    # b)
    dropped_gdp = df_gdp[df_gdp[gdp_column].isna()]
    # creating a copy of the dropped rows
    dropped_gdp.to_csv("output/dropped_gdp.csv", index=False)
    df_gdp = df_gdp.dropna(subset=[gdp_column])

    # c)
    q1 = df_gdp[gdp_column].quantile(tukey_q1_percentile)
    q3 = df_gdp[gdp_column].quantile(tukey_q3_percentile)
    iqr = q3 - q1
    lower = q1 - tukey_iqr_multiplier * iqr
    upper = q3 + tukey_iqr_multiplier * iqr
    outliers = df_gdp[(df_gdp[gdp_column] < lower) | (df_gdp[gdp_column] > upper)]
    # TODO We should write this output in our report
    print(f"___________GDP outliers:___________\n {outliers}")

    # d)
    # TODO We should document in the report our decision process here, go figure
    df_gdp = df_gdp.drop_duplicates(subset="Country", keep="first")

    # e)
    df_gdp = normalize_country_names(df_gdp)

    # f)
    df_gdp = df_gdp.set_index("Country")

    return df_gdp

"""
Cleaning the Population df
a) Converting Population to numeric
b) Removing rows with missing Population
c) Identifying outliers using Tukey method
d) Removing duplicates and normalizing country names
e) Set index to Country
"""
def clean_pop(df_pop):
    # a)
    df_pop["Population"] = (
        df_pop["Population"]
        .astype(str)
        .str.replace(",", "")
    )
    # same logic as previously
    df_pop["Population"] = pd.to_numeric(df_pop["Population"], errors='coerce')

    # b)
    before = len(df_pop)
    df_pop = df_pop.dropna(subset=["Population"])
    after = len(df_pop)
    # TODO We should write this output in our report
    print(f"\nPopulation rows removed due to missing values: {before - after}\n")

    # c)
    df_pop["LogPopulation"] = np.log10(df_pop["Population"])
    q1 = df_pop["LogPopulation"].quantile(tukey_q1_percentile)
    q3 = df_pop["LogPopulation"].quantile(tukey_q3_percentile)
    iqr = q3 - q1
    lower = q1 - tukey_iqr_multiplier * iqr
    upper = q3 + tukey_iqr_multiplier * iqr
    outliers = df_pop[(df_pop["LogPopulation"] < lower) | (df_pop["LogPopulation"] > upper)]
    # TODO We should write this output in our report
    print(f"___________Population outliers:___________\n {outliers}")

    # d)
    df_pop = df_pop.drop_duplicates(subset="Country", keep="first")
    df_pop = normalize_country_names(df_pop)

    # e)
    df_pop = df_pop.set_index("Country")

    return df_pop

# Run cleaning
df_gdp_clean = clean_gdp(df_gdp)
df_pop_clean= clean_pop(df_pop)

# Save cleaned data
df_gdp_clean.to_csv("output/cleaned_gdp.csv")
df_pop_clean.to_csv("output/cleaned_pop.csv")