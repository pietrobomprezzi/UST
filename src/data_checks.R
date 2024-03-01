#checking the links are still working
library(readxl)
library(dplyr)
library(httr)
library(openxlsx)

# insert the path to the dataset we want to check
filepath <- 'C:/Users/pietr/Downloads/Ukraine_Support_Tracker_Release_13.xlsx'

# read the Excel file
df <- read_excel(filepath, sheet = 'Bilateral Assistance, MAIN DATA')

# for now checking only source 1
colchecklist <- c('Source of Aid 1', 'Source of Aid 2', 'Source of Aid 3', 'Source of Aid 4')

# define the requester function
requester <- function(string, identifier) {
  tryCatch({
    resp <- HEAD(string)
    if (resp$status_code < 400) {
      output <- list('error' = 'no', 'id' = identifier, 'link' = string)
    } else {
      output <- list('error' = 'YES', 'id' = identifier, 'link' = string)
      # to do: more detailed errors
    }
  }, error = function(e) {
    output <- list('error' = 'some other error', 'id' = identifier, 'link' = string)
  })
  return(output)
}

# check
sources_by_date <- df %>% 
  group_by(ID, `Announcement Date`) %>%
  summarise(n_sources = n_distinct(`Source of Aid 1`))

# collapse at the ID-date level
df <- df %>% 
  distinct(ID, `Announcement Date`, .keep_all = TRUE)

# loopity-loop
dict_list <- lapply(1:nrow(df), function(i) {
  requester(df$`Source of Aid 1`[i], df$ID[i])
})

finaldf <- do.call(rbind, dict_list)

write.xlsx(finaldf, 'output/check_pdfs.xlsx')



library(readxl)
library(dplyr)

# Read the Excel file
df_refugee <- read_excel('Refugee data.xlsx', sheet = 'release 14 refugee recorded tab')

# Define function to check months
check_months <- function(df) {
  # Convert 'Data Date' column to datetime format
  df$Data.Date <- as.Date(df$Data.Date)
  
  # Filter data for the year 2022 and 2023
  df_2022 <- df[df$Data.Date >= as.Date("2022-01-01") & df$Data.Date <= as.Date("2022-12-31"), ]
  df_2023 <- df[df$Data.Date >= as.Date("2023-01-01") & df$Data.Date <= as.Date("2023-12-31"), ]
  
  # Group by country and calculate distinct months for each year
  result_2022 <- df_2022 %>% 
    group_by(Country) %>%
    summarise(Distinct.Months.2022 = n_distinct(Month))
  
  result_2023 <- df_2023 %>% 
    group_by(Country) %>%
    summarise(Distinct.Months.2023 = n_distinct(Month))
  
  # Merge results on the 'Country' column
  result <- full_join(result_2022, result_2023, by = "Country")
  
  # Fill NA values with 0
  result[is.na(result)] <- 0
  
  return(result)
}

result_df <- check_months(df_refugee)
print(result_df)
