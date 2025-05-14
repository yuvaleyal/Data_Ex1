import pandas as pd
import numpy as np


def create_feature_table():
	"""
	part 5.1 & 5.2 (Inner join of df_pop and df_gdp)
	Calculating Total GDP, LogGDPperCapita and LogPopulation
	and adding it to the new table which will look like this:
	Country ; GDP_per_capita_PPP ; Population ; TotalGDP ; LogGDPperCapita ; LogPopulation
	"""

	# Inner join on Country
	df = df_gdp.join(df_pop, how="inner")

	# Calculate Total GDP
	df["TotalGDP"] = df["GDP_per_capita_PPP"] * df["Population"]

	# Ensuring values are numeric and positive before applying log10
	df["TotalGDP"] = pd.to_numeric(df["TotalGDP"], errors="coerce")
	df = df[(df["TotalGDP"] > 0)]
	df = df[df["Population"] > 0]

	df["LogGDPperCapita"] = np.log10(df["GDP_per_capita_PPP"])
	df["LogPopulation"] = np.log10(df["Population"])

	# only if we want to view the table
	# df = df.reset_index()

	df.to_csv("../output/combined.csv", index=False)

	return df

def scaling(df_gdp_pop, df_demo):
	"""
	part 5.3
	Normalizing Life Expectancy Both, LogGDPperCapita and LogPopulation
	and saving it in X.npy
	"""
	# Ensure they have the same countries (and aligned)
	common_countries = df_demo.index.intersection(df_gdp_pop.index)
	df_demo = df_demo.loc[common_countries]
	df_gdp_pop = df_gdp_pop.loc[common_countries]

	# Getting relevant columns
	le = df_demo["Life Expectancy Both"]
	log_gdp = df_gdp_pop["LogGDPperCapita"]
	log_pop = df_gdp_pop["LogPopulation"]

	# Combine into a DataFrame
	X = pd.concat([le, log_gdp, log_pop], axis=1)
	X.columns = ["Life Expectancy Both", "LogGDPperCapita", "LogPopulation"]
	X = X.dropna()

	# Z-score normalization
	X_normalized = (X - X.mean()) / X.std()

	X_normalized = X_normalized.sort_index()

	print(X_normalized)
	np.save("../output/X.npy", X_normalized.to_numpy())

def Data_Integration(df_gdp_pop, df_demo):
	"""
	part 5.4
	a) Ensuring the dfs are indexed by country
	b) Performing inner join
	c) Reporting how many countries remain
	d) Saving lost countries
	e) Handling missing values
	f) Saving final feature matrix (LifeExpectancy Both, LogGDPperCapita, LogPopulation)
	"""
	# a) no need to check we loaded the dfs indexed by country in the main
	# b)
	df_final = df_demo.join(df_gdp_pop, how="inner")

	# c)
	print(f"Number of countries after inner join: {df_final.shape[0]}")

	# d)
	all_countries = set(df_demo.index) | set(df_gdp.index) | set(df_pop.index)
	merged_countries = set(df_final.index)
	lost_countries = sorted(all_countries - merged_countries)
	pd.DataFrame(lost_countries, columns=["Country"]).to_csv(
		"../output/lost_countries.csv", index=False)

	# e)
	numeric_cols = df_final.select_dtypes(include=[np.number]).columns
	df_final[numeric_cols] = df_final[numeric_cols].apply(
		lambda col: col.fillna(col.mean()))

	df_final = df_final.dropna()

	# f)
	selected_features = ["Life Expectancy Both", "LogGDPperCapita",
						 "LogPopulation"]

	# Normalize (z-score)
	X = (df_final[selected_features] - df_final[selected_features].mean()) / \
		df_final[selected_features].std()

	X = X.loc[sorted(X.index)]

	np.save("../output/X.npy", X.to_numpy())
	print(X)

	df_final.to_csv("../output/merged_final.csv")


if __name__ == "__main__":
	# Load cleaned dfs
	df_gdp = pd.read_csv("../output/cleaned_gdp.csv", index_col="Country")
	df_pop = pd.read_csv("../output/cleaned_pop.csv", index_col="Country")
	df_demo = pd.read_csv("../output/demographics_data.csv", index_col="Country")

	# Inner join of df_pop and df_gdp
	df_gdp_pop = create_feature_table()

	# Creating X.npy
	scaling(df_gdp_pop, df_demo)

	Data_Integration(df_demo, df_gdp_pop)

