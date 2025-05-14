import pandas as pd
import numpy as np

tukey_q1_percentile = 0.25
tukey_q3_percentile = 0.75
tukey_iqr_multiplier = 1.5

def loading_2021_files():
    """
    part 3.2
    a) Loading the csv files
    b) Confirming the columns
    c) Ensuring numeric type
    d) Saving the first 5 rows of the original dataframes
    e) Running describe
    """
    # a)
    df_gdp = pd.read_csv("../output/gdp_per_capita_2021.csv", na_values=["None"])
    df_pop = pd.read_csv("../output/population_2021.csv", na_values=["None"])

    # b) & c)
    df_gdp["GDP_per_capita_PPP"] = pd.to_numeric(df_gdp["GDP_per_capita_PPP"], errors='coerce')
    df_pop["Population"] = pd.to_numeric(df_pop["Population"], errors='coerce')

    # d)
    df_gdp.head(5).to_csv("../output/gdp_before_sort.csv", index=False)
    df_pop.head(5).to_csv("../output/pop_before_sort.csv", index=False)

    df_gdp_sorted = df_gdp.sort_values("Country")
    df_pop_sorted = df_pop.sort_values("Country")
    df_gdp_sorted.head(5).to_csv("../output/gdp_after_sort.csv", index=False)
    df_pop_sorted.head(5).to_csv("../output/pop_after_sort.csv", index=False)

    # e)
    df_gdp.describe().to_csv("../output/gdp_describe.csv")
    df_pop.describe().to_csv("../output/pop_describe.csv")

    return df_gdp, df_pop


def normalize_country_names(df):
    """
    removing "the" from country names and normalizing them to a certain format
    "   The netherlands " -> "Netherlands"
    returning the corrected dataframe along with the names that have been corrected
    """
    original = df["Country"].copy()
    df["Country"] = df["Country"].str.replace("^the ", "", case=False, regex=True).str.title().str.strip()
    mismatches = pd.DataFrame({"Original": original, "Corrected": df["Country"]})
    mismatches = mismatches[mismatches["Original"] != mismatches["Corrected"]]
    return df, mismatches

def clean_gdp(df_gdp):
    """
    part 4.2
    Cleaning the GDP df
    a) Converting GDP to numeric
    b) Removing rows with missing GDP
    c) Identifying outliers using Tukey method
    d) Removing duplicates
    e) Normalizing country names
    f) Setting index to Country
    """
    # a)
    df_gdp["GDP_per_capita_PPP"] = (
        df_gdp["GDP_per_capita_PPP"]
        .astype(str)
        .str.replace(",", "")
        .str.replace("$", "")
    )
    df_gdp["GDP_per_capita_PPP"] = pd.to_numeric(df_gdp["GDP_per_capita_PPP"], errors='coerce')

    # b)
    dropped_gdp = df_gdp[df_gdp["GDP_per_capita_PPP"].isna()]
    # creating a copy of the dropped rows
    dropped_gdp.to_csv("../output/dropped_gdp.csv", index=False)
    df_gdp = df_gdp.dropna(subset=["GDP_per_capita_PPP"])

    # c)
    q1 = df_gdp["GDP_per_capita_PPP"].quantile(tukey_q1_percentile)
    q3 = df_gdp["GDP_per_capita_PPP"].quantile(tukey_q3_percentile)
    iqr = q3 - q1
    lower = q1 - tukey_iqr_multiplier * iqr
    upper = q3 + tukey_iqr_multiplier * iqr
    outliers = df_gdp[(df_gdp["GDP_per_capita_PPP"] < lower) | (df_gdp["GDP_per_capita_PPP"] > upper)]
    # TODO We should write this output in our report
    print(f"___________GDP outliers:___________\n{outliers}")

    # d)
    # TODO We should document in the report our decision process here, go figure
    df_gdp = df_gdp.drop_duplicates(subset="Country", keep="first")

    # e)
    df_gdp, mismatches_gdp = normalize_country_names(df_gdp)

    # f)
    df_gdp = df_gdp.set_index("Country")

    return df_gdp, mismatches_gdp


def clean_pop(df_pop):
    """
    part 4.3
    Cleaning the Population df
    a) Converting Population to numeric
    b) Removing rows with missing Population
    c) Identifying outliers using Tukey method
    d) Removing duplicates and normalizing country names
    e) Set index to Country
    """
    # a)
    df_pop["Population"] = (
        df_pop["Population"]
        .astype(str)
        .str.replace(",", "")
    )
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
    q3 = df_pop["LogPopulation"].quantile(tukey_q1_percentile)
    iqr = q3 - q1
    lower = q1 - tukey_iqr_multiplier * iqr
    upper = q3 + tukey_iqr_multiplier * iqr
    outliers = df_pop[(df_pop["LogPopulation"] < lower) | (df_pop["LogPopulation"] > upper)]
    # TODO We should write this output in our report
    print(f"___________Population outliers count:___________\n{len(outliers)}")

    # d)
    df_pop = df_pop.drop_duplicates(subset="Country", keep="first")
    df_pop, mismatches_pop = normalize_country_names(df_pop)

    # Set index
    df_pop = df_pop.set_index("Country")

    return df_pop, mismatches_pop

if __name__ == "__main__":
    df_gdp, df_pop = loading_2021_files()

    # Run cleaning
    df_gdp_clean, mismatches_gdp = clean_gdp(df_gdp)
    df_pop_clean, mismatches_pop = clean_pop(df_pop)

    df_gdp_clean.to_csv("../output/cleaned_gdp.csv")
    df_pop_clean.to_csv("../output/cleaned_pop.csv")

    # Save mismatches for record
    all_mismatches = pd.concat([mismatches_gdp, mismatches_pop])
    all_mismatches.to_csv("../output/name_mismatches.csv", index=False)