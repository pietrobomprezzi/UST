
#takin the data from the main dataset, Refugees Recorded sheet, checking month variation in refugees
import pandas as pd

df_refugee = pd.read_excel('Refugee data.xlsx', 'release 14 refugee recorded tab')


def check_months(df):
    # Convert 'Data Date' column to datetime format
    df['Data Date'] = pd.to_datetime(df['Data Date'])

    # Filter data for the year 2022 and 2023
    df_2022 = df[df['Data Date'].dt.year == 2022]
    df_2023 = df[df['Data Date'].dt.year == 2023]

    # Group by country and calculate distinct months for each year
    result_2022 = df_2022.groupby('Country')['Month'].nunique().reset_index()
    result_2023 = df_2023.groupby('Country')['Month'].nunique().reset_index()

    # Rename columns
    result_2022.columns = ['Country', 'Distinct Months 2022']
    result_2023.columns = ['Country', 'Distinct Months 2023']

    # Merge results on the 'Country' column
    result = pd.merge(result_2022, result_2023, on='Country', how='outer')

    # Fill NaN values with 0
    result = result.fillna(0)

    return result

result_df = check_months(df_refugee)
print(result_df)