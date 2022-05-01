import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


# STREAMLIT-AGGRID
# https://streamlit.io/gallery
# CSV WRANGLER
# https://github.com/streamlit/example-app-csv-wrangler/blob/main/app.py

# ===========================================


# input widgets
# https://docs.streamlit.io/library/api-reference/widgets



# st.markdown(
#     """
#     <style>
#     [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
#         width: 500px;
#     }
#     [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
#         width: 500px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# ======================== Header ========================

st.markdown("## Data Visualization")
st.markdown("##### Generate executable Python code for Matplotlib plots")
st.markdown("""---""")

# ======================== File chooser ========================

uploaded_file = st.file_uploader("Choose a CSV file (otherwise, a default one is loaded for you - Sample-Superstore-Subset-Excel.csv)")

if uploaded_file is not None:
    file_to_use = uploaded_file
    file_name = uploaded_file.name
else:
    file_to_use = "Sample-Superstore-Subset-Excel.csv"
    file_name = file_to_use

raw_data = pd.read_csv(file_to_use, encoding = "unicode_escape")

st.markdown("""---""")

# ======================== File display ========================

st.markdown(f"### {file_name}")
st.dataframe(raw_data)  # just displays table

# To allow editing
categorical_cols_guess = raw_data.select_dtypes("object").columns.tolist()
numerical_cols_guess = raw_data.select_dtypes(np.number).columns.tolist()

categorical_cols = st.multiselect("Categorical", options = raw_data.columns, default = categorical_cols_guess)
numerical_cols = st.multiselect("Numerical", options = raw_data.columns, default = numerical_cols_guess)

st.markdown("""---""")

# ======================== Data axes options ========================

st.sidebar.markdown(f"#### Axes")
x_vars = st.sidebar.multiselect("X-axis", categorical_cols, default = categorical_cols[0])
y_vars = st.sidebar.multiselect("Y-axis", numerical_cols, default = numerical_cols[0])

agg_boolean_choice = st.sidebar.radio("Aggregate?", ["Yes", "No"])
is_agg = agg_boolean_choice == "Yes"

aggregation_options = {
    "Sum": "sum",
    "Average": "mean",
    "Count": "count",
    "Median": "median",
    "Minimum": "min",
    "Maximum": "max",
    "Standard Deviation": "std",
    "Variance": "var"
}

y_vars_aggfn_mappings = {}
if is_agg:
    for y_var in y_vars:
        aggregation_choice = st.sidebar.selectbox(f"Aggregation for {y_var}", aggregation_options.keys(), key = y_var)
        y_vars_aggfn_mappings[y_var] = aggregation_options[aggregation_choice]

st.sidebar.markdown("""---""")

# ======================== Chart options ========================

st.sidebar.markdown(f"#### Chart Options")

# ======= Bar/Plot/Scatter =======

if is_agg:
    chart_type_options = {
        "Bar Chart": "bar",
        "Line Plot": "plot",
        "Scatter Plot": "scatter"
    }
    chart_type_choice = st.sidebar.radio("Graph type", chart_type_options.keys())
    chart_type = chart_type_options[chart_type_choice]
else:
    chart_type = "scatter"


# ======= Chart color =======

chart_color = st.sidebar.color_picker("Chart color", value = "#00E1FF")

fig_width = st.sidebar.slider("Figure width", min_value = 0, max_value = 12, value = 8, step = 1)
fig_height = st.sidebar.slider("Figure height", min_value = 0, max_value = 12, value = 6, step = 1)

# bar: width
# plot: linewidth, linestyle, marker
# scatter: size, alpha

st.sidebar.markdown("""---""")

# ======================== Axes options ========================

st.sidebar.markdown(f"#### Axes Options")


# change labels and title (textboxes)
# options for tick marks???


# ======================== Display ========================

if len(x_vars) == 0 or len(y_vars) == 0:
    st.stop()
    
input_vars_code = f"""
x_vars = {x_vars}
y_vars = {y_vars}
{f"is_agg = {is_agg}" if is_agg else ""}
{f"y_vars_aggfn_mappings = {y_vars_aggfn_mappings}" if is_agg else ""}
fig_width = {fig_width}
fig_height = {fig_height}
chart_color = "{chart_color}"
"""

remove_raw_data_code = """
# removes rows where relevant columns are NA
for var in x_vars + y_vars:
    raw_data = raw_data[raw_data[var].notna()]"""
exec(remove_raw_data_code)


get_rows_and_cols_code = f"""
# each row has a unique aggregation of each y_var
num_rows = len(y_vars)

# recursively get unique categories for each column
def split_x_vars(depth, data, x_vars_to_split):
    if depth == len(x_vars_to_split): 
        return None, 1

    all_split_data = {{}}

    x_var = x_vars_to_split[depth]
    unique_vals = data[x_var].unique()

    num_cols = 0
    for unique_val in unique_vals:
        splitted_data = data[data[x_var] == unique_val]
        all_split_data[unique_val], inner_num_cols = split_x_vars(depth + 1, splitted_data, x_vars_to_split)

        num_cols += inner_num_cols
    
    return all_split_data, num_cols


unique_sep = ">>"  # hopefully this is not in any column name
if len(x_vars) == 1:
    flattened_x_vars = raw_data["{x_vars[0]}"].unique()
    num_cols = len(flattened_x_vars)
else:
    # each column is based on "{x_vars[-1]}"
    splitted_x_vars, num_cols = split_x_vars(0, raw_data, x_vars[:-1])
    flattened_x_vars = pd.json_normalize(splitted_x_vars, sep = unique_sep).columns.tolist()"""
exec(get_rows_and_cols_code)


plot_code = f"""
overall_title = " / ".join(x_vars)
sub_titles = []

fig, axes = plt.subplots(num_rows, num_cols, sharex = "col", sharey = "row", figsize = (fig_width, fig_height))

# plots:
# (0, 0), (0, 1), ...
# (1, 0), (1, 1), ...
for j in range(num_cols):

    # each col is a unique combination of x_vars[:-1]
    col_details = flattened_x_vars[j].split(unique_sep)

    # split the data into the unique combination of values
    filtered_data = raw_data
    for k in range(len(col_details)):
        category_name = x_vars[k]
        sub_detail = col_details[k]
        filtered_data = filtered_data[filtered_data[category_name] == sub_detail]
        if len(sub_titles) == k:
            sub_titles.append([])
        
        if sub_detail not in sub_titles[k]:
            sub_titles[k].append(sub_detail)

    # break the chart into unique values of "{x_vars[-1]}"
    x = filtered_data["{x_vars[-1]}"].unique()

    final_data = {"filtered_data.groupby(x_vars[-1], as_index = False).agg(y_vars_aggfn_mappings)" if is_agg else "filtered_data"}
    
    for i, y in enumerate(y_vars):

        if num_rows == 1:
            specific_plot = axes[j]
        else:
            specific_plot = axes[i, j]

        specific_plot.{chart_type if is_agg else "scatter"}(final_data["{x_vars[-1]}"], final_data[y], color = chart_color)
        specific_plot.tick_params("x", labelrotation = 90)
        specific_plot.grid(axis = "y", linewidth = 0.3)  # https://www.w3schools.com/python/matplotlib_grid.asp
        specific_plot.set_axisbelow(True)

        if i == 0:
            specific_plot.set_title(col_details[-1])
        if j == 0:
            specific_plot.set_ylabel(f"{{y}}{" ({y_vars_aggfn_mappings[y]})" if is_agg else ""}")

sub_titles.pop()
final_title = [overall_title] + ["               |               ".join(i) for i in sub_titles]
fig.suptitle("\\n".join(final_title))
"""
exec(plot_code)

# # group raw_data by "Order Priority", for each unique value of "Order Priority", calculate the sum of "Row ID"
# data = raw_data.groupby("Order Priority", as_index = False).agg({"Row ID": "sum"})

# axes.plot(data["Order Priority"], data["Row ID"], color = "#00E1FF")

# axes.set_xlabel("Order Priority")
# axes.set_ylabel("Row ID (sum)")
# axes.set_ylim([32788252.0, 43926232.0])

import_code = """
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd"""

read_data_code = f"""
raw_data = pd.read_csv("{file_name}", encoding = "unicode_escape")"""

explanation_code = f"""
# flattened_x_vars: {flattened_x_vars}"""


code = f"""
{import_code}
{read_data_code}
{input_vars_code}
{remove_raw_data_code}
{get_rows_and_cols_code}
{explanation_code}
{plot_code}
plt.show()
"""


st.markdown("### Results")
st.pyplot(fig)
st.code(code, language = "python")
