import streamlit as st
import pandas as pd
import io
from streamlit_option_menu import option_menu

# Initialize session state variables
if "coded_df" not in st.session_state:
    st.session_state.coded_df = pd.DataFrame()
if "original_df" not in st.session_state:
    st.session_state.original_df = pd.DataFrame()
if "modified_columns" not in st.session_state:
    st.session_state.modified_columns = []

st.title("Variable Coding App")

# Sidebar option menu with icons and custom styles
with st.sidebar:
    selected = option_menu(
        menu_title="Actions",  # required
        options=["Upload File", "Variable Coding", "Reset Coding"],  # required
        icons=["upload", "pencil", "arrow-counterclockwise"],  # optional
        menu_icon="cast",  # optional
        default_index=0,  # optional
    )

# Main content based on navigation
if selected == "Upload File":
    st.subheader("Upload File")
    uploaded_file = st.file_uploader(
        "Upload an Excel or CSV file", type=["xlsx", "csv"]
    )

    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error reading file: {e}")
        else:
            st.session_state.original_df = df.copy()
            st.session_state.coded_df = df.copy()
            st.session_state.modified_columns = []
            st.success("File uploaded successfully!")

            # Check before displaying the dataframe
            if not st.session_state.coded_df.empty:
                st.dataframe(st.session_state.coded_df, hide_index=True)
            else:
                st.warning("No data to display")

elif selected == "Variable Coding":
    st.subheader("Variable Coding")

    if st.session_state.coded_df.empty or st.session_state.coded_df.shape[1] == 0:
        st.warning("Please upload a file in the 'Upload File' section.")
    else:
        columns = st.session_state.coded_df.columns.tolist()
        if not columns:
            st.error("No columns found in the uploaded file.")
        else:
            default_idx = 1 if len(columns) > 1 else 0
            col_to_code = st.selectbox(
                "Select a column to code", columns, index=default_idx
            )

            if col_to_code:
                unique_vals = list(
                    dict.fromkeys(st.session_state.coded_df[col_to_code].dropna())
                )
                st.subheader("Unique values in the column")
                display_data = [
                    {"s.no": idx + 1, "value": val}
                    for idx, val in enumerate(unique_vals)
                ]
                st.markdown(
                    pd.DataFrame(display_data).to_html(index=False),
                    unsafe_allow_html=True,
                )

                mapping_input = st.text_input(
                    "Enter numeric values separated by space (e.g., 1 3 2 4)"
                )

                if st.button("Submit Mapping"):
                    try:
                        mapping_numbers = [
                            int(num) for num in mapping_input.strip().split()
                        ]
                        if len(mapping_numbers) != len(unique_vals):
                            st.error(
                                f"Number of mapping values ({len(mapping_numbers)}) does not match the number of unique items ({len(unique_vals)})."
                            )
                        else:
                            mapping_dict = {
                                orig: num
                                for orig, num in zip(unique_vals, mapping_numbers)
                            }
                            st.session_state.coded_df[col_to_code] = (
                                st.session_state.coded_df[col_to_code].map(mapping_dict)
                            )

                            if col_to_code not in st.session_state.modified_columns:
                                st.session_state.modified_columns.append(col_to_code)

                            sorted_mapping = sorted(
                                mapping_dict.items(), key=lambda x: x[1]
                            )
                            summary_data = [
                                {"s.no": idx + 1, "value": orig, "code": num}
                                for idx, (orig, num) in enumerate(sorted_mapping)
                            ]

                            st.success("Success! Variable coding completed.")
                            st.subheader("Mapping Summary (sorted by code)")
                            st.markdown(
                                pd.DataFrame(summary_data).to_html(index=False),
                                unsafe_allow_html=True,
                            )

                            st.subheader("Coded Data")
                            st.dataframe(st.session_state.coded_df, hide_index=True)

                    except ValueError:
                        st.error(
                            "Please ensure you enter only numeric values separated by spaces."
                        )

        csv_buffer = io.StringIO()
        st.session_state.coded_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="Download Coded File",
            data=csv_buffer.getvalue(),
            file_name="coded_file.csv",
            mime="text/csv",
        )

elif selected == "Reset Coding":
    st.subheader("Reset Coding")

    if st.session_state.coded_df.empty or st.session_state.coded_df.shape[1] == 0:
        st.warning("Please upload a file in the 'Upload File' section.")
    elif not st.session_state.modified_columns:
        st.info("No columns have been coded yet.")
    else:
        col_to_reset = st.selectbox(
            "Select a modified column to reset", st.session_state.modified_columns
        )
        if st.button("Reset Coding"):
            st.session_state.coded_df[col_to_reset] = st.session_state.original_df[
                col_to_reset
            ]
            st.session_state.modified_columns.remove(col_to_reset)
            st.success(f"Coding for column '{col_to_reset}' has been reset.")

            # Check before displaying the coded dataframe
            if not st.session_state.coded_df.empty:
                st.subheader("Coded Data")
                st.dataframe(st.session_state.coded_df, hide_index=True)
            else:
                st.warning("No data to display")
