import pandas as pd
from functools import reduce

def LoadDemocracyIndex():
    df = pd.read_csv("EIU_DI.csv")
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

    cpi_2024 = cpi_map[2024]

    df['cpi_for_year'] = df['year'].map(cpi_map)
    df['inflation_multiplier'] = cpi_2024 / df['cpi_for_year']

    df['price_adjusted'] = df['price'] * df['inflation_multiplier']

    return df

def LoadGDPCountry():
    df = pd.read_csv("GDP_1975_2025.csv")

    # Melt the dataframe — convert year columns into rows to convert from wide format to long format
    df_long = df.melt(id_vars=["Country"], 
                    var_name="year", 
                    value_name="Value")
    # Remove entries without a value


    df_long["year"] = pd.to_numeric(df_long["year"], errors="coerce").astype("Int64")
    df_long = df_long.dropna(subset=["Value"])

    # Filter out values before 2000
    df_long = df_long[df_long["year"] >= 2000]

    df_long.rename(columns={"Country": "country", "Value": "GDPValue"}, inplace=True)
    df_long['GDPValue'] = pd.to_numeric(df_long['GDPValue'], errors='coerce')

    df_long = df_long.sort_values(["country", "year"]).reset_index(drop=True)

    return df_long

def LoadGDPCapita():
    # Read the dataset
    df = pd.read_csv("GDPCapita_2000_2024.csv")

    # Strip column names just in case
    df.columns = df.columns.str.strip()

    # Identify year columns (numeric column names)
    year_cols = [col for col in df.columns if col.isdigit()]

    # Melt into long format
    df_long = df.melt(
        id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'],
        value_vars=year_cols,
        var_name='year',
        value_name='value'
    )

    # Convert year to integer and value to numeric
    df_long['year'] = pd.to_numeric(df_long['year'], errors='coerce').astype('Int64')
    df_long['value'] = pd.to_numeric(df_long['value'], errors='coerce')
    df_long = df_long.dropna(subset=['value'])

    df_long = df_long[df_long["year"] >= 2000]
    df_long.rename(columns={"Country Name": "country", "value": "GDPCapitaValue"}, inplace=True)

    df_long = df_long.sort_values(["country", "year"]).reset_index(drop=True)

    return df_long

def MergeDataFrames(dfs):
    merged_df = reduce(lambda left, right: pd.merge(left, right, on=['country', 'year'], how='outer'), dfs )
    return merged_df

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
    print (F"{MergedIndex[['country', 'year',"GDPValue", "DIIndex", "price_adjusted", "GDPCapitaValue"]].head(5)}")

test()