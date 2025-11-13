import pandas as pd

def LoadDemocracyIndex():
    df = pd.read_csv("EIU_DI.csv")
    df = df.rename(columns={"REF_AREA_LABEL": "country", "OBS_VALUE": "DIIndex", "TIME_PERIOD": "year"})  
    return df

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

    df['price_adjusted'] = df['price'] * df['inflation_multiplier']

    return df

def MergeDataFrames(df1, df2):
    merged_df = pd.merge(df1, df2, on=['country', 'year'], how='inner')
    return merged_df

def get_merged_df():
    return MergeDataFrames(LoadDemocracyIndex(), LoadBigMacIndex())