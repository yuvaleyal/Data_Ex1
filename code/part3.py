import pandas as pd
import os

# Load cleaned GDP and Population DataFrames
df_gdp = pd.read_csv("../output/cleaned_gdp.csv", index_col="Country")
df_pop = pd.read_csv("../output/cleaned_pop.csv", index_col="Country")

# Ensure numeric types
df_gdp["GDP_per_capita_PPP"] = pd.to_numeric(df_gdp["GDP_per_capita_PPP"],
											 errors="coerce")
df_pop["Population"] = pd.to_numeric(df_pop["Population"], errors="coerce")

# Inner join on Country
df_combined = df_gdp.join(df_pop, how="inner")

# Calculate Total GDP
df_combined["TotalGDP"] = df_combined["GDP_per_capita_PPP"] * df_combined[
	"Population"]

# Optional: Save for validation
os.makedirs("../output", exist_ok=True)
df_combined[["GDP_per_capita_PPP", "Population", "TotalGDP"]].to_csv(
	"../output/total_gdp_feature.csv")

# Preview
print(df_combined[["GDP_per_capita_PPP", "Population", "TotalGDP"]].head())
