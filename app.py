import pandas as pd
import plotly.express as px
import streamlit as st
from ollama import chat

st.set_page_config(
    page_title="Local Data Analysis Agent",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Local Data Analysis Agent")
st.write(
    "Upload a CSV or Excel file and analyze it with a free local AI model."
)

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx"],
)

try:
    if uploaded_file is not None:
        if uploaded_file.name.lower().endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)

        st.success("Your file was uploaded successfully!")
    else:
        data = pd.read_csv("sales.csv")
        st.info("Currently using the sample sales.csv file.")

except Exception as error:
    st.error(f"Could not read the file: {error}")
    st.stop()
# Data cleaning controls
st.subheader("Data Cleaning Options")
st.caption(
    "Cleaning is optional. Select only the changes you want to apply."
)

clean_col1, clean_col2, clean_col3 = st.columns(3)

with clean_col1:
    remove_duplicates = st.checkbox(
        "Remove duplicate rows"
    )

with clean_col2:
    fill_numeric_missing = st.checkbox(
        "Fill missing numeric values"
    )

with clean_col3:
    fill_text_missing = st.checkbox(
        "Fill missing text values"
    )

cleaned_data = data.copy()
cleaning_messages = []

if remove_duplicates:
    rows_before = len(cleaned_data)
    cleaned_data = cleaned_data.drop_duplicates()
    removed_rows = rows_before - len(cleaned_data)

    cleaning_messages.append(
        f"Removed {removed_rows} duplicate rows"
    )

if fill_numeric_missing:
    numeric_cleaning_columns = cleaned_data.select_dtypes(
        include="number"
    ).columns

    numeric_values_filled = 0

    for column in numeric_cleaning_columns:
        missing_count = int(cleaned_data[column].isnull().sum())

        if missing_count > 0:
            median_value = cleaned_data[column].median()

            if pd.isna(median_value):
                median_value = 0

            cleaned_data[column] = cleaned_data[column].fillna(
                median_value
            )

            numeric_values_filled += missing_count

    cleaning_messages.append(
        f"Filled {numeric_values_filled} missing numeric values"
    )

if fill_text_missing:
    text_cleaning_columns = cleaned_data.select_dtypes(
        include=["object", "string"]
    ).columns

    text_values_filled = 0

    for column in text_cleaning_columns:
        missing_count = int(cleaned_data[column].isnull().sum())

        if missing_count > 0:
            available_modes = cleaned_data[column].mode(
                dropna=True
            )

            if available_modes.empty:
                replacement_value = "Unknown"
            else:
                replacement_value = available_modes.iloc[0]

            cleaned_data[column] = cleaned_data[column].fillna(
                replacement_value
            )

            text_values_filled += missing_count

    cleaning_messages.append(
        f"Filled {text_values_filled} missing text values"
    )

data = cleaned_data

if cleaning_messages:
    st.success(" | ".join(cleaning_messages))
# Dynamic data filter
st.subheader("Filter Data")

filter_columns = data.select_dtypes(
    include=["object", "string", "category"]
).columns.tolist()

if filter_columns:
    filter_column = st.selectbox(
        "Choose a column to filter",
        filter_columns,
    )

    filter_options = (
        data[filter_column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    filter_options = sorted(filter_options)

    selected_values = st.multiselect(
        f"Select {filter_column} values",
        filter_options,
        default=filter_options,
    )

    if selected_values:
        data = data[
            data[filter_column]
            .astype(str)
            .isin(selected_values)
        ]

        st.caption(
            f"Showing {len(data)} rows after filtering."
        )
    else:
        st.warning(
            "Select at least one value to continue."
        )
        st.stop()

else:
    st.info(
        "No text columns are available for filtering."
    )
# Data preview
st.subheader("Data Preview")
st.dataframe(data, width="stretch")

# Dataset overview
st.subheader("Dataset Overview")

row_count = len(data)
column_count = len(data.columns)
missing_values = int(data.isnull().sum().sum())
duplicate_rows = int(data.duplicated().sum())

overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)

overview_col1.metric("Rows", row_count)
overview_col2.metric("Columns", column_count)
overview_col3.metric("Missing Values", missing_values)
overview_col4.metric("Duplicate Rows", duplicate_rows)

column_details = pd.DataFrame(
    {
        "Column": data.columns,
        "Data Type": data.dtypes.astype(str).values,
        "Missing Values": data.isnull().sum().values,
        "Unique Values": data.nunique(dropna=True).values,
    }
)

with st.expander("View Column Details"):
    st.dataframe(column_details, width="stretch")
# Exact analysis tool
st.subheader("Exact Analysis Tool")
st.caption(
    "These results are calculated directly with Pandas, "
    "not estimated by the AI."
)

exact_numeric_columns = data.select_dtypes(
    include="number"
).columns.tolist()

if exact_numeric_columns:
    exact_col1, exact_col2, exact_col3 = st.columns(3)

    with exact_col1:
        exact_operation = st.selectbox(
            "Select operation",
            [
                "Sum",
                "Average",
                "Minimum",
                "Maximum",
                "Count",
            ],
            key="exact_operation",
        )

    with exact_col2:
        exact_value_column = st.selectbox(
            "Select numeric column",
            exact_numeric_columns,
            key="exact_value_column",
        )

    with exact_col3:
        exact_group_column = st.selectbox(
            "Group results by",
            ["No grouping"] + data.columns.tolist(),
            key="exact_group_column",
        )

    aggregation_methods = {
        "Sum": "sum",
        "Average": "mean",
        "Minimum": "min",
        "Maximum": "max",
        "Count": "count",
    }

    selected_aggregation = aggregation_methods[
        exact_operation
    ]

    if exact_group_column == "No grouping":
        exact_series = data[
            exact_value_column
        ].dropna()

        exact_result = exact_series.agg(
            selected_aggregation
        )

        if exact_operation == "Count":
            displayed_result = f"{exact_result:,.0f}"
        else:
            displayed_result = f"{exact_result:,.2f}"

        st.metric(
            f"{exact_operation} of {exact_value_column}",
            displayed_result,
        )

        exact_result_table = pd.DataFrame(
            {
                "Operation": [exact_operation],
                "Column": [exact_value_column],
                "Result": [exact_result],
            }
        )

    else:
        result_column_name = (
            f"{exact_operation.lower()}_"
            f"{exact_value_column}"
        )

        exact_result_table = (
            data.groupby(
                exact_group_column,
                dropna=False,
            )[exact_value_column]
            .agg(selected_aggregation)
            .reset_index(name=result_column_name)
        )

        st.dataframe(
            exact_result_table,
            width="stretch",
        )

    st.download_button(
        label="Download Exact Analysis",
        data=exact_result_table.to_csv(
            index=False
        ).encode("utf-8"),
        file_name="exact_analysis.csv",
        mime="text/csv",
    )

else:
    st.info(
        "No numeric columns are available "
        "for exact analysis."
    )
# Interactive chart builder
st.subheader("Interactive Chart Builder")

all_columns = data.columns.tolist()
numeric_columns = data.select_dtypes(include="number").columns.tolist()

if numeric_columns:
    chart_col1, chart_col2, chart_col3 = st.columns(3)

    with chart_col1:
        x_axis = st.selectbox(
            "Select X-axis",
            all_columns,
        )

    with chart_col2:
        y_axis = st.selectbox(
            "Select Y-axis",
            numeric_columns,
        )

    with chart_col3:
        chart_type = st.selectbox(
            "Select chart type",
            ["Bar Chart", "Line Chart", "Scatter Plot"],
        )

    if chart_type == "Bar Chart":
        custom_chart = px.bar(
            data,
            x=x_axis,
            y=y_axis,
            title=f"{y_axis} by {x_axis}",
        )

    elif chart_type == "Line Chart":
        custom_chart = px.line(
            data,
            x=x_axis,
            y=y_axis,
            markers=True,
            title=f"{y_axis} by {x_axis}",
        )

    else:
        custom_chart = px.scatter(
            data,
            x=x_axis,
            y=y_axis,
            title=f"{y_axis} by {x_axis}",
        )

    st.plotly_chart(
        custom_chart,
        width="stretch",
        config={
            "displaylogo": False,
            "toImageButtonOptions": {
                "format": "png",
                "filename": "analysis_chart",
                "width": 1200,
                "height": 700,
                "scale": 2,
            },
        },
    )

    st.caption(
        "To download the chart as an image, "
        "click the camera icon above the chart."
    )

else:
    st.warning(
        "A chart cannot be created because no numeric columns were found."
    )

# Sales-specific analysis
required_columns = {
    "product",
    "category",
    "quantity",
    "unit_price",
}

if required_columns.issubset(data.columns):
    data["quantity"] = pd.to_numeric(
        data["quantity"],
        errors="coerce",
    )

    data["unit_price"] = pd.to_numeric(
        data["unit_price"],
        errors="coerce",
    )

    data["total_sales"] = data["quantity"] * data["unit_price"]

    total_sales = data["total_sales"].sum()
    total_quantity = data["quantity"].sum()
    total_products = data["product"].nunique()

    sales_col1, sales_col2, sales_col3 = st.columns(3)

    sales_col1.metric(
        "Total Sales",
        f"{total_sales:,.0f} BDT",
    )

    sales_col2.metric(
        "Items Sold",
        f"{total_quantity:,.0f}",
    )

    sales_col3.metric(
        "Unique Products",
        total_products,
    )

    category_sales = (
        data.groupby(
            "category",
            as_index=False,
        )["total_sales"]
        .sum()
    )

    st.subheader("Sales by Category")

    sales_chart = px.bar(
        category_sales,
        x="category",
        y="total_sales",
        color="category",
        text_auto=True,
        title="Category-wise Sales",
    )

    st.plotly_chart(
        sales_chart,
        width="stretch",
    )

    best_category = category_sales.loc[
        category_sales["total_sales"].idxmax()
    ]

    st.success(
        f"The highest sales came from the "
        f"{best_category['category']} category: "
        f"{best_category['total_sales']:,.0f} BDT"
    )

else:
    st.info(
        "The sales dashboard requires product, category, "
        "quantity, and unit_price columns."
    )
# Correlation analysis
st.subheader("Correlation Analysis")

correlation_data = data.select_dtypes(
    include="number"
)

if len(correlation_data.columns) >= 2:
    correlation_matrix = correlation_data.corr()

    correlation_chart = px.imshow(
        correlation_matrix,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Correlation Between Numeric Columns",
    )

    st.plotly_chart(
        correlation_chart,
        width="stretch",
    )

    with st.expander("How to Read Correlation"):
        st.write(
            """
            - A value close to **1** means a strong positive relationship.
            - A value close to **-1** means a strong negative relationship.
            - A value close to **0** means little or no linear relationship.
            - Correlation does not automatically mean that one variable
              causes the other.
            """
        )

else:
    st.info(
        "At least two numeric columns are required "
        "to calculate correlation."
    )
# Time-series trend analysis
st.subheader("Time-Series Trend Analysis")

date_columns = [
    column
    for column in data.columns
    if "date" in column.lower() or "time" in column.lower()
]

trend_numeric_columns = data.select_dtypes(
    include="number"
).columns.tolist()

if date_columns and trend_numeric_columns:
    trend_col1, trend_col2, trend_col3 = st.columns(3)

    with trend_col1:
        selected_date_column = st.selectbox(
            "Select date column",
            date_columns,
            key="trend_date_column",
        )

    with trend_col2:
        selected_trend_metric = st.selectbox(
            "Select metric",
            trend_numeric_columns,
            key="trend_metric",
        )

    with trend_col3:
        selected_frequency = st.selectbox(
            "Select time frequency",
            ["Daily", "Monthly", "Yearly"],
            key="trend_frequency",
        )

    trend_data = data.copy()

    trend_data[selected_date_column] = pd.to_datetime(
        trend_data[selected_date_column],
        errors="coerce",
    )

    trend_data = trend_data.dropna(
        subset=[selected_date_column]
    )

    if not trend_data.empty:
        if selected_frequency == "Daily":
            trend_data["time_period"] = (
                trend_data[selected_date_column].dt.date
            )

        elif selected_frequency == "Monthly":
            trend_data["time_period"] = (
                trend_data[selected_date_column]
                .dt.to_period("M")
                .dt.to_timestamp()
            )

        else:
            trend_data["time_period"] = (
                trend_data[selected_date_column]
                .dt.to_period("Y")
                .dt.to_timestamp()
            )

        trend_summary = (
            trend_data.groupby(
                "time_period",
                as_index=False,
            )[selected_trend_metric]
            .sum()
        )

        trend_chart = px.line(
            trend_summary,
            x="time_period",
            y=selected_trend_metric,
            markers=True,
            title=(
                f"{selected_trend_metric} "
                f"{selected_frequency} Trend"
            ),
        )

        st.plotly_chart(
            trend_chart,
            width="stretch",
        )

    else:
        st.warning(
            "No valid dates were found in the selected column."
        )

else:
    st.info(
        "A date column and at least one numeric column "
        "are required for trend analysis."
    )
# Outlier detection
st.subheader("Outlier Detection")

outlier_numeric_columns = data.select_dtypes(
    include="number"
).columns.tolist()

if outlier_numeric_columns:
    selected_outlier_column = st.selectbox(
        "Select a numeric column",
        outlier_numeric_columns,
        key="outlier_column",
    )

    outlier_series = data[
        selected_outlier_column
    ].dropna()

    if not outlier_series.empty:
        first_quartile = outlier_series.quantile(0.25)
        third_quartile = outlier_series.quantile(0.75)
        interquartile_range = third_quartile - first_quartile

        lower_limit = first_quartile - (
            1.5 * interquartile_range
        )

        upper_limit = third_quartile + (
            1.5 * interquartile_range
        )

        outlier_rows = data[
            (
                data[selected_outlier_column] < lower_limit
            )
            | (
                data[selected_outlier_column] > upper_limit
            )
        ]

        outlier_col1, outlier_col2, outlier_col3 = st.columns(3)

        outlier_col1.metric(
            "Detected Outliers",
            len(outlier_rows),
        )

        outlier_col2.metric(
            "Lower Limit",
            f"{lower_limit:,.2f}",
        )

        outlier_col3.metric(
            "Upper Limit",
            f"{upper_limit:,.2f}",
        )

        outlier_chart = px.box(
            data,
            y=selected_outlier_column,
            points="outliers",
            title=f"Outliers in {selected_outlier_column}",
        )

        st.plotly_chart(
            outlier_chart,
            width="stretch",
            config={
                "displaylogo": False,
                "toImageButtonOptions": {
                    "format": "png",
                    "filename": "outlier_chart",
                    "width": 1000,
                    "height": 700,
                    "scale": 2,
                },
            },
        )

        st.caption(
            "Click the camera icon above the chart "
            "to download it as a PNG image."
        )

        if not outlier_rows.empty:
            with st.expander("View Detected Outlier Rows"):
                st.dataframe(
                    outlier_rows,
                    width="stretch",
                )

            st.download_button(
                label="Download Outlier Rows",
                data=outlier_rows.to_csv(
                    index=False
                ).encode("utf-8"),
                file_name="outlier_rows.csv",
                mime="text/csv",
            )

        else:
            st.success(
                "No outliers were detected in this column."
            )

else:
    st.info(
        "No numeric columns are available "
        "for outlier detection."
    )
# Text report download
st.subheader("Download Text Report")

report_numeric_data = data.select_dtypes(include="number")

if report_numeric_data.empty:
    report_summary = "No numeric columns were found."
else:
    report_summary = report_numeric_data.describe().to_string()

report_content = f"""
DATA ANALYSIS REPORT
====================

DATASET OVERVIEW
----------------
Rows: {len(data)}
Columns: {len(data.columns)}
Missing Values: {int(data.isnull().sum().sum())}
Duplicate Rows: {int(data.duplicated().sum())}

COLUMN NAMES
------------
{", ".join(data.columns)}

DATA TYPES
----------
{data.dtypes.astype(str).to_string()}

MISSING VALUES BY COLUMN
------------------------
{data.isnull().sum().to_string()}

NUMERIC SUMMARY
---------------
{report_summary}
"""

download_col1, download_col2 = st.columns(2)

with download_col1:
    st.download_button(
        label="Download Analysis Report as Text",
        data=report_content,
        file_name="data_analysis_report.txt",
        mime="text/plain",
    )

with download_col2:
    st.download_button(
        label="Download Processed Data",
        data=data.to_csv(index=False).encode("utf-8"),
        file_name="processed_data.csv",
        mime="text/csv",
    )

# Local AI analysis
# Local AI chat
st.divider()
st.subheader("Chat With Your Local Data Analysis Agent")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

title_col, clear_col = st.columns([4, 1])

with title_col:
    st.caption(
        "Ask questions about the uploaded dataset. "
        "The conversation stays available during this session."
    )

with clear_col:
    if st.button(
        "Clear Chat",
        width="stretch",
    ):
        st.session_state.chat_history = []
        st.rerun()

# Display previous questions and answers
for chat_item in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat_item["question"])

    with st.chat_message("assistant"):
        st.write(chat_item["answer"])
response_language = st.selectbox(
    "Choose AI response language",
    ["English", "Bangla"],
    key="response_language",
)
question = st.chat_input(
    "Ask a question about your data"
)

if question:
    with st.chat_message("user"):
        st.write(question)

    numeric_data = data.select_dtypes(include="number")

    if numeric_data.empty:
        numeric_summary = "No numeric columns were found."
        numeric_totals = "No numeric totals were calculated."
    else:
        numeric_summary = numeric_data.describe().to_string()
        numeric_totals = numeric_data.sum().to_string()

    dataset_sample = data.head(100).to_csv(index=False)
    if exact_numeric_columns:
        exact_analysis_context = f"""
Selected operation: {exact_operation}
Selected numeric column: {exact_value_column}
Selected group column: {exact_group_column}

Exact Pandas result:
{exact_result_table.to_string(index=False)}
"""
    else:
        exact_analysis_context = (
            "No exact numeric analysis is available."
        )

    prompt = f"""
Answer the user's question using only the supplied dataset information.

Rules:
- Do not invent values.
- Do not show internal reasoning.
- Give a concise and clear final answer.
- Answer in {response_language}.
- If the available information is insufficient, say so.
- Mention relevant numbers when possible.

Dataset row count:
{len(data)}

Dataset columns and data types:
{data.dtypes.astype(str).to_dict()}

Missing values:
{data.isnull().sum().to_dict()}

Numeric totals:
{numeric_totals}

Numeric summary:
{numeric_summary}

Exact analysis selected by the user:
{exact_analysis_context}

First 100 rows:
{dataset_sample}

Current user question:
{question}
"""

    conversation_messages = [
        {
            "role": "system",
            "content": (
                "You are an accurate data analysis assistant. "
                "Use only the supplied dataset information."
            ),
        }
    ]

    # Give the model recent conversation memory
    for chat_item in st.session_state.chat_history[-5:]:
        conversation_messages.append(
            {
                "role": "user",
                "content": chat_item["question"],
            }
        )

        conversation_messages.append(
            {
                "role": "assistant",
                "content": chat_item["answer"],
            }
        )

    conversation_messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    try:
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your data..."):
                response = chat(
                    model="qwen3:4b",
                    messages=conversation_messages,
                )

                answer = response.message.content

            st.write(answer)

        st.session_state.chat_history.append(
            {
                "question": question,
                "answer": answer,
            }
        )

    except Exception as error:
        with st.chat_message("assistant"):
            st.error(
                "Could not connect to the local AI. "
                f"Make sure Ollama is running. Details: {error}"
            )
            # Download chat history
if st.session_state.chat_history:
    chat_export_parts = []

    for chat_number, chat_item in enumerate(
        st.session_state.chat_history,
        start=1,
    ):
        chat_export_parts.append(
            f"""
QUESTION {chat_number}
--------------------
{chat_item["question"]}

ANSWER {chat_number}
------------------
{chat_item["answer"]}
"""
        )

    chat_export_content = "\n".join(
        chat_export_parts
    )

    st.download_button(
        label="Download Chat History",
        data=chat_export_content,
        file_name="data_analysis_chat_history.txt",
        mime="text/plain",
    )