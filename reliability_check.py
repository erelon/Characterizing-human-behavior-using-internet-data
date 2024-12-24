import pandas as pd
import pingouin as pg

# Load your data
file_name = "labeled_depression.csv"
df = pd.read_csv(file_name)

# Prepare data for ICC calculation
# Melt the DataFrame into long format required for ICC calculation
df_long = pd.melt(df, id_vars=['comment'], 
                  value_vars=['depression score', 'well_being score'],
                  var_name='question', 
                  value_name='rating')

# Calculate ICC(2,1)
icc = pg.intraclass_corr(data=df_long, 
                         targets='comment',   # Individual items (comments)
                         raters='question',   # Raters (questions)
                         ratings='rating')    # Ratings column

# Filter for ICC(2,1) row and display results
icc_2_1 = icc[icc['Type'] == 'ICC2']
print(icc_2_1)

