import streamlit as st
import pandas as pd
import io

# Initialize coded_df
if "coded_df" not in st.session_state:
    st.session_state.coded_df = pd.DataFrame()  # or any default value

st.title("Variable Coding App")

# Sidebar navigation
nav = st.sidebar.radio("Go to", ["Upload File", "Variable Coding", "Reset Coding"])

if nav == "Upload File":
    st.subheader("Upload File")
    uploaded_file = st.file_uploader(
        "Upload an Excel or CSV file", type=["xlsx", "csv"]
    )

    if uploaded_file:
        # Read the file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Initialize session state variables
        st.session_state.original_df = df.copy()
        st.session_state.coded_df = df.copy()
        st.session_state.modified_columns = []

        st.success("File uploaded successfully!")
        st.dataframe(st.session_state.coded_df.style.hide_index())

elif nav == "Variable Coding":
    st.subheader("Variable Coding")
    if "coded_df" not in st.session_state:
        st.warning("Please upload a file in the 'Upload File' section.")
    else:
        columns = st.session_state.coded_df.columns.tolist()
        default_idx = 1 if len(columns) > 1 else 0
        col_to_code = st.selectbox(
            "Select a column to code", columns, index=default_idx
        )

        if col_to_code:
            # Get unique values (preserving order)
            unique_vals = list(
                dict.fromkeys(st.session_state.coded_df[col_to_code].dropna())
            )

            st.subheader("Unique values in the column")
            display_data = [
                {"s.no": idx + 1, "value": val} for idx, val in enumerate(unique_vals)
            ]
            display_data = pd.DataFrame(display_data).to_html(index=False)
            st.markdown(display_data, unsafe_allow_html=True)

            # Input field for numeric mapping
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
                            f"Number of mapping values ({len(mapping_numbers)}) does not match number of unique items ({len(unique_vals)})."
                        )
                    else:
                        # Create and apply the mapping
                        mapping_dict = {
                            orig: num for orig, num in zip(unique_vals, mapping_numbers)
                        }
                        st.session_state.coded_df[col_to_code] = (
                            st.session_state.coded_df[col_to_code].map(mapping_dict)
                        )

                        # Track modified columns
                        if col_to_code not in st.session_state.modified_columns:
                            st.session_state.modified_columns.append(col_to_code)

                        # Prepare mapping summary sorted in ascending order
                        sorted_mapping = sorted(
                            mapping_dict.items(), key=lambda x: x[1]
                        )
                        summary_data = [
                            {"s.no": idx + 1, "value": orig, "code": num}
                            for idx, (orig, num) in enumerate(sorted_mapping)
                        ]

                        st.success("Success! Variable coding completed.")
                        st.subheader("Mapping Summary (sorted by code)")
                        summary_html = pd.DataFrame(summary_data).to_html(index=False)
                        st.markdown(summary_html, unsafe_allow_html=True)

                        st.subheader("Coded Data")
                        st.dataframe(st.session_state.coded_df.style.hide_index())
                except ValueError:
                    st.error(
                        "Please ensure you enter only numeric values separated by spaces."
                    )

        # Download button for the coded file
        csv_buffer = io.StringIO()
        st.session_state.coded_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="Download Coded File",
            data=csv_buffer.getvalue(),
            file_name="coded_file.csv",
            mime="text/csv",
        )

elif nav == "Reset Coding":
    st.subheader("Reset Coding")
    if "coded_df" not in st.session_state:
        st.warning("Please upload a file in the 'Upload File' section.")
    elif not st.session_state.modified_columns:
        st.info("No columns have been coded yet.")
    else:
        col_to_reset = st.selectbox(
            "Select a modified column to reset", st.session_state.modified_columns
        )
        if st.button("Reset Coding"):
            # Reset the column and update the tracking
            st.session_state.coded_df[col_to_reset] = st.session_state.original_df[
                col_to_reset
            ]
            st.session_state.modified_columns.remove(col_to_reset)
            st.success(f"Coding for column '{col_to_reset}' has been reset.")
            st.subheader("Coded Data")
            st.dataframe(st.session_state.coded_df.style.hide_index())
