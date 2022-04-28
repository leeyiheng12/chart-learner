import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.markdown(
        """
<style>
    .reportview-container .main .block-container {
        min-width: 75%;
    }
</style>
""",
        unsafe_allow_html=True,
    )


# STREAMLIT-AGGRID
# https://streamlit.io/gallery
# CSV WRANGLER
# https://github.com/streamlit/example-app-csv-wrangler/blob/main/app.py

# ===========================================


# input widgets
# https://docs.streamlit.io/library/api-reference/widgets


st.markdown("## Learn matplotlib!")
st.markdown("""---""")

uploaded_file = st.file_uploader("Choose a CSV file (otherwise, a default one is loaded for you)")

st.markdown("""---""")


if uploaded_file is not None:
    file_to_use = uploaded_file
    file_name = uploaded_file.name
else:
    file_to_use = "Sample-Superstore-Subset-Excel.csv"
    file_name = file_to_use

raw_data = pd.read_csv(file_to_use, encoding = "unicode_escape")

st.markdown(f"#### {file_name}")
st.dataframe(raw_data)  # just displays table

# To allow editing
numerical_cols = raw_data.select_dtypes(np.number).columns.tolist()
categorical_cols = raw_data.select_dtypes("object").columns.tolist()


st.markdown("""---""")

# ======================== data options ========================
x_var = st.selectbox("X-axis", categorical_cols, key = 2)
y_var = st.selectbox("Y-axis", numerical_cols, key = 3)

agg_boolean_choice = st.radio("Aggregate?", ["Yes", "No"])
agg_boolean = agg_boolean_choice == "Yes"

aggregation_options = {
    "Sum": "sum",
    "Average": "mean",
    "Median": "median",
    "Minimum": "min",
    "Maximum": "max",
    "Standard Deviation": "std",
    "Variance": "var",
    "Mad": "mad",
    "Prod": "prod",
}

aggregation_choice = agg_fn_name = None
if agg_boolean:
    aggregation_choice = st.selectbox("Aggregation", aggregation_options.keys(), disabled = not agg_boolean)
    agg_fn_name = aggregation_options[aggregation_choice]

st.markdown("""---""")

# ======================== graph options ========================


graph_type_options = {
    "Bar Chart": "bar",
    "Line Plot": "plot",
    "Scatter Plot": "scatter"
}
graph_type_choice = st.radio("Graph type", graph_type_options.keys())
graph_type = graph_type_options[graph_type_choice]

graph_color_choice = st.color_picker("Graph color", value = "#00E1FF")

if agg_boolean:
    data = raw_data[raw_data[x_var].notna() & raw_data[y_var].notna()]
    y_vals = data.groupby(x_var, as_index = False).agg({y_var: agg_fn_name})[y_var]
else:
    data = raw_data[raw_data[x_var].notna() & raw_data[y_var].notna()]
    y_vals = data[y_var]

y_vals = sorted(y_vals.to_list())
lowest_y = y_vals[0]
highest_y = y_vals[-1]
diff = highest_y - lowest_y
step = (highest_y - lowest_y) / 10
upper = highest_y * 1.5

st.markdown("y-axis range:")
graph_lower_y_lim = st.number_input("From", min_value = 0.0, max_value = upper, value = max(0.0, float(lowest_y - diff)), step = step)
graph_upper_y_lim = st.number_input("To", min_value = 0.0, max_value = upper, value = min(upper, float(highest_y + diff)), step = step)


# bar: width
# plot: linewidth, linestyle, marker
# scatter: size, alpha


st.markdown("""---""")

fig, axes = plt.subplots()

aggregated_code = f"""
# removes rows where "{x_var}" or "{y_var}" is NaN
raw_data = raw_data[raw_data["{x_var}"].notna() & raw_data["{y_var}"].notna()]  

# group raw_data by "{x_var}", for each unique value of "{x_var}", calculate the {agg_fn_name} of "{y_var}"
data = raw_data.groupby("{x_var}", as_index = False).agg({{"{y_var}": "{agg_fn_name}"}})

fig, axes = plt.subplots()
axes.{graph_type}(data["{x_var}"], data["{y_var}"], color = "{graph_color_choice}")

axes.set_xlabel("{x_var}")
axes.set_ylabel("{y_var} ({agg_fn_name})")
axes.set_ylim([{graph_lower_y_lim}, {graph_upper_y_lim}])
axes.set_title("{aggregation_choice} of {y_var} across {x_var}")
"""

non_aggregated_code = f"""

# removes rows where "{x_var}" or "{y_var}" is NaN
data = raw_data[raw_data["{x_var}"].notna() & raw_data["{y_var}"].notna()]  

fig, axes = plt.subplots()
axes.{graph_type}(data["{x_var}"], data["{y_var}"], color = "{graph_color_choice}")

axes.set_xlabel("{x_var}")
axes.set_ylabel("{y_var}")
axes.set_ylim([{graph_lower_y_lim}, {graph_upper_y_lim}])
axes.set_title(f"{y_var} across {x_var}")
"""


code_to_run = aggregated_code if agg_boolean else non_aggregated_code

exec(code_to_run)

st.markdown("### Results")
st.pyplot(fig)


import_statements = f"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd"""

read_data_statements = f"""
raw_data = pd.read_csv("{file_name}", encoding = "unicode_escape")"""

agg_code = f"""
{import_statements}
{read_data_statements}
{code_to_run}
plt.show()

"""
st.code(agg_code, language = "python")




