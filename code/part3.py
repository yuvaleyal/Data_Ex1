import pandas as pd
import os

OUTPUT_FOLDER = r"C:/Users/Yuval/Desktop/CS/thirdyear/secondsemester/Data/Ex1/Repo/Data_Ex1/output"

def total_gdp(df_population: pd.DataFrame, df_gdp_per_capita: pd.DataFrame) -> pd.DataFrame:
    df_gdp = pd.DataFrame(columns=df_population.columns)
    for country in df_population['Country']:
            df_gdp[country] = df_population[country] * df_gdp_per_capita[country]
    return df_gdp

if __name__ == "__main__":
    df_population = pd.read_csv(os.path.join(OUTPUT_FOLDER, r"population_2021.csv"))
    df_gdp_per_capita = pd.read_csv(os.path.join(OUTPUT_FOLDER, r"gdp_per_capita.csv"))
    df_gdp = total_gdp(df_population, df_gdp_per_capita)
    df_gdp.to_csv('gdp.csv', index=False)