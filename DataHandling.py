import numpy as np
import pandas as pd
from functools import reduce

class DataHandler:
    def __init__(self):
        self.all_indexes = ["BMI", "DIIndex", "GDPValue", "GDPCapitaValue"]
        self.data = {
            "BMI": LoadBigMacIndex(),
            "DIIndex": LoadDemocracyIndex(),
            "GDPValue": LoadGDPCountry(),
            "GDPCapitaValue": LoadGDPCapita(),
            "all": None
        }
        all_dfs = self.get_merged_df(df_names = self.all_indexes, how="outer")
        self.data["all"] = all_dfs
        self.all_year = sorted(all_dfs["year"].astype(int).unique())

    def get_merged_df(self, df_names = [], how="inner"):
        dfs_to_merge = [self.get_df_by_name(df_name) for df_name in df_names]
        return MergeDataFrames(dfs_to_merge, how=how)

    def get_df_by_name(self, name):
        return self.data[name]

    def get_all_indexes(self):
        return self.all_indexes

    def get_all_years(self):
        return self.all_year


def LoadDemocracyIndex():
    df = pd.read_csv("DemocracyIndex.csv")
    df = df.rename(columns={"REF_AREA_LABEL": "country", "OBS_VALUE": "DIIndex", "TIME_PERIOD": "year"})
    return df[['country', 'year',"DIIndex"]]

def LoadBigMacIndex():
    #Calculate prices after inflation
    df = pd.read_csv("BigmacPrice.csv")
    df = df.rename(columns={"name": "country", "dollar_price": "price"})
    df["year"] = pd.to_datetime(df["date"]).dt.year
    df = df.groupby(["country", "year"], as_index=False)["price"].mean()

    cpi_data = {
        'year': [
            2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007,
            2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016,
            2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024
        ],
        'avg_cpi': [
            195.3, 201.6, 207.3, 215.3, 214.5, 218.1, 224.9, 229.6,
            233.0, 237.0, 240.0, 245.1, 251.1, 255.7, 258.8, 264.9, 
            271.0, 276.7,281.9, 287.5, 292.7, 296.8, 300.8, 306.0, 313.7
        ]
    }

    cpi_df = pd.DataFrame(cpi_data)

    cpi_map = dict(zip(cpi_df['year'], cpi_df['avg_cpi']))

    cpi_2024 = cpi_map[2024] #using 2024 as baseline for inflation

    df['cpi_for_year'] = df['year'].map(cpi_map)
    df['inflation_multiplier'] = cpi_2024 / df['cpi_for_year']

    df['BMI'] = df['price'] * df['inflation_multiplier']

    df["BMI"] = 10 * (np.log(df["BMI"]) / np.log(df["BMI"]).max())

    return df[["country", "year", "BMI"]]

def LoadGDPCountry():
    df = pd.read_csv("GDP.csv")

    # Melt the dataframe — convert year columns into rows to convert from wide format to long format
    df = df.melt(id_vars=["Country"],
                    var_name="year", 
                    value_name="Value")

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["Value"])

    # Filter out values before 2000
    df = df[df["year"] >= 2000]

    df.rename(columns={"Country": "country", "Value": "GDPValue"}, inplace=True)
    df['GDPValue'] = pd.to_numeric(df['GDPValue'], errors='coerce')

    df = df.sort_values(["country", "year"]).reset_index(drop=True)
    df["GDPValue"] = 10 * (np.log(df["GDPValue"]) / np.log(df["GDPValue"]).max()) # map the values between 0 and 10
    return df

def LoadGDPCapita():
    # Read the dataset
    df = pd.read_csv("GDPCapita.csv")

    # Strip column names just in case
    df.columns = df.columns.str.strip()

    # Identify year columns (numeric column names)
    year_cols = [col for col in df.columns if col.isdigit()]

    # Melt into long format
    df = df.melt(
        id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'],
        value_vars=year_cols,
        var_name='year',
        value_name='value'
    )

    # Convert year to integer and value to numeric
    df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df = df.dropna(subset=['value'])

    df = df[df["year"] >= 2000]
    df.rename(columns={"Country Name": "country", "value": "GDPCapitaValue"}, inplace=True)

    df = df.sort_values(["country", "year"]).reset_index(drop=True)

    df["GDPCapitaValue"] = 10 * (np.log(df["GDPCapitaValue"]) / np.log(df["GDPCapitaValue"]).max()) # map the values between 0 and 10

    return df

def MergeDataFrames(dfs, how="inner"):
    if len(dfs) != 0:
        return reduce(lambda left, right: pd.merge(left, right, on=['country', 'year'], how=how), dfs )
    else:
        return pd.DataFrame()

def test():
    DemocracyIndex = LoadDemocracyIndex()
    print (F"DemocracyIndex.columns")
    print (F"{DemocracyIndex.columns}")
    BigmacIndex = LoadBigMacIndex()
    print (F"BigmacIndex.columns")
    print (F"{BigmacIndex.columns}")
    GDPData = LoadGDPCountry()
    print (F"GDPData.columns")
    print (F"{GDPData.columns}")
    GDPCapita = LoadGDPCapita()
    print (F"GDPCapita.columns")
    print (F"{GDPCapita.columns}")


    dataframes = [DemocracyIndex, BigmacIndex, GDPData, GDPCapita]

    MergedIndex = MergeDataFrames (dataframes)
    print (F"MergedIndex.columns")
    print (F"{MergedIndex.columns}")
    print (F"{MergedIndex[['country', 'year',"GDPValue", "DIIndex", "BMI", "GDPCapitaValue"]].head(5)}")

test()