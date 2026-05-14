# # import streamlit as st
# # import pandas as pd
# # from io import BytesIO

# # # =========================================================
# # # IMPORT INVOICE MODULE
# # # =========================================================

# # from invoice_processing import process_invoice_pdfs

# # # =========================================================
# # # PAGE CONFIG
# # # =========================================================

# # st.set_page_config(
# #     page_title="PO GRN Invoice Automation",
# #     layout="wide"
# # )

# # # =========================================================
# # # SIDEBAR MENU
# # # =========================================================

# # tool = st.sidebar.selectbox(
# #     "Select Tool",
# #     [
# #         "PO GRN Reconciliation",
# #         "Invoice OCR Processing"
# #     ]
# # )

# # # =========================================================
# # # TOOL 1
# # # PO GRN RECONCILIATION
# # # =========================================================

# # def run_po_grn():

# #     st.title("📊 PO - GRN Reconciliation Automation")

# #     st.markdown("---")

# #     # =====================================================
# #     # BULK FILE UPLOAD
# #     # =====================================================

# #     uploaded_files = st.file_uploader(
# #         "Upload All Excel Files Together",
# #         type=["xlsx", "xls"],
# #         accept_multiple_files=True
# #     )

# #     # =====================================================
# #     # MAIN LOGIC
# #     # =====================================================

# #     if uploaded_files:

# #         file_names = [file.name for file in uploaded_files]

# #         st.success(f"{len(uploaded_files)} Files Uploaded Successfully")

# #         # =================================================
# #         # FILE SELECTION
# #         # =================================================

# #         col1, col2 = st.columns(2)

# #         with col1:
# #             po_selected = st.selectbox(
# #                 "Select PO File",
# #                 file_names
# #             )

# #         with col2:
# #             grn_selected = st.selectbox(
# #                 "Select GRN File",
# #                 file_names
# #             )

# #         st.markdown("---")

# #         # =================================================
# #         # PROCESS BUTTON
# #         # =================================================

# #         if st.button("🚀 Generate Final Report"):

# #             try:

# #                 po_file = None
# #                 grn_file = None

# #                 for file in uploaded_files:

# #                     if file.name == po_selected:
# #                         po_file = file

# #                     elif file.name == grn_selected:
# #                         grn_file = file

# #                 # =================================================
# #                 # READ FILES
# #                 # =================================================

# #                 po_df = pd.read_excel(po_file)
# #                 grn_df = pd.read_excel(grn_file)

# #                 # =================================================
# #                 # CLEAN COLUMN NAMES
# #                 # =================================================

# #                 po_df.columns = po_df.columns.str.strip()
# #                 grn_df.columns = grn_df.columns.str.strip()

# #                 # =================================================
# #                 # PREVIEW
# #                 # =================================================

# #                 st.subheader("📁 File Preview")

# #                 tab1, tab2 = st.tabs(["PO File", "GRN File"])

# #                 with tab1:
# #                     st.dataframe(po_df.head())

# #                 with tab2:
# #                     st.dataframe(grn_df.head())

# #                 # =================================================
# #                 # REQUIRED COLUMNS
# #                 # =================================================

# #                 po_required_columns = [
# #                     'Vendor Name',
# #                     'Transaction No',
# #                     'Total Value',
# #                     'Basic Value'
# #                 ]

# #                 grn_required_columns = [
# #                     'PO',
# #                     'GR No.',
# #                     'GrandTotal'
# #                 ]

# #                 for col in po_required_columns:

# #                     if col not in po_df.columns:
# #                         st.error(f"PO File Missing Column: {col}")
# #                         st.stop()

# #                 for col in grn_required_columns:

# #                     if col not in grn_df.columns:
# #                         st.error(f"GRN File Missing Column: {col}")
# #                         st.stop()

# #                 # =================================================
# #                 # PREPARE PO DATA
# #                 # =================================================

# #                 po_data = po_df[[
# #                     'Vendor Name',
# #                     'Transaction No',
# #                     'Total Value',
# #                     'Basic Value'
# #                 ]].copy()

# #                 po_data.columns = [
# #                     'Vendor',
# #                     'PO number',
# #                     'PO amount in PO Dump',
# #                     'Invoice Amount (Does not include tax)'
# #                 ]

# #                 po_data[
# #                     'Invoice amount in Payment Compliance sheet'
# #                 ] = po_data['PO amount in PO Dump']

# #                 # =================================================
# #                 # PREPARE GRN DATA
# #                 # =================================================

# #                 grn_data = grn_df[[
# #                     'PO',
# #                     'GR No.',
# #                     'GrandTotal'
# #                 ]].copy()

# #                 grn_data.columns = [
# #                     'PO number',
# #                     'GRN number',
# #                     'GRN amount in GRN working sheet'
# #                 ]

# #                 # =================================================
# #                 # REMOVE DUPLICATES
# #                 # =================================================

# #                 po_data = po_data.drop_duplicates()
# #                 grn_data = grn_data.drop_duplicates()

# #                 # =================================================
# #                 # CONVERT TYPES
# #                 # =================================================

# #                 po_data['PO number'] = po_data['PO number'].astype(str)
# #                 grn_data['PO number'] = grn_data['PO number'].astype(str)

# #                 # =================================================
# #                 # MERGE
# #                 # =================================================

# #                 final_df = pd.merge(
# #                     po_data,
# #                     grn_data,
# #                     on='PO number',
# #                     how='left'
# #                 )

# #                 # =================================================
# #                 # NUMERIC CONVERSION
# #                 # =================================================

# #                 numeric_cols = [
# #                     'PO amount in PO Dump',
# #                     'Invoice amount in Payment Compliance sheet',
# #                     'Invoice Amount (Does not include tax)',
# #                     'GRN amount in GRN working sheet'
# #                 ]

# #                 for col in numeric_cols:

# #                     final_df[col] = pd.to_numeric(
# #                         final_df[col],
# #                         errors='coerce'
# #                     )

# #                 # =================================================
# #                 # MATCH CALCULATIONS
# #                 # =================================================

# #                 final_df['PO to GRN Match'] = (
# #                     final_df['PO amount in PO Dump']
# #                     -
# #                     final_df['GRN amount in GRN working sheet']
# #                 )

# #                 final_df['Invoice to GRN match'] = (
# #                     final_df['Invoice Amount (Does not include tax)']
# #                     -
# #                     final_df['GRN amount in GRN working sheet']
# #                 )

# #                 # =================================================
# #                 # FINAL COLUMN ORDER
# #                 # =================================================

# #                 final_columns = [
# #                     'Vendor',
# #                     'PO number',
# #                     'PO amount in PO Dump',
# #                     'Invoice amount in Payment Compliance sheet',
# #                     'Invoice Amount (Does not include tax)',
# #                     'GRN number',
# #                     'GRN amount in GRN working sheet',
# #                     'PO to GRN Match',
# #                     'Invoice to GRN match'
# #                 ]

# #                 final_df = final_df[final_columns]

# #                 # =================================================
# #                 # SUMMARY
# #                 # =================================================

# #                 st.markdown("---")

# #                 st.subheader("📈 Summary")

# #                 c1, c2, c3 = st.columns(3)

# #                 with c1:
# #                     st.metric(
# #                         "Total PO Amount",
# #                         f"{final_df['PO amount in PO Dump'].sum():,.2f}"
# #                     )

# #                 with c2:
# #                     st.metric(
# #                         "Total Invoice Amount",
# #                         f"{final_df['Invoice amount in Payment Compliance sheet'].sum():,.2f}"
# #                     )

# #                 with c3:
# #                     st.metric(
# #                         "Total GRN Amount",
# #                         f"{final_df['GRN amount in GRN working sheet'].sum():,.2f}"
# #                     )

# #                 # =================================================
# #                 # OUTPUT
# #                 # =================================================

# #                 st.markdown("---")

# #                 st.subheader("✅ Final Reconciliation Output")

# #                 st.dataframe(
# #                     final_df,
# #                     use_container_width=True
# #                 )

# #                 # =================================================
# #                 # DOWNLOAD
# #                 # =================================================

# #                 output = BytesIO()

# #                 with pd.ExcelWriter(
# #                     output,
# #                     engine='xlsxwriter'
# #                 ) as writer:

# #                     final_df.to_excel(
# #                         writer,
# #                         index=False,
# #                         sheet_name='Final Output'
# #                     )

# #                     worksheet = writer.sheets['Final Output']

# #                     for i, col in enumerate(final_df.columns):

# #                         column_len = max(
# #                             final_df[col].astype(str).map(len).max(),
# #                             len(col)
# #                         ) + 5

# #                         worksheet.set_column(i, i, column_len)

# #                 output.seek(0)

# #                 st.download_button(
# #                     label="📥 Download Final Excel",
# #                     data=output,
# #                     file_name="PO_GRN_Reconciliation_Output.xlsx",
# #                     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
# #                 )

# #             except Exception as e:

# #                 st.error(f"Error: {str(e)}")

# # # =========================================================
# # # TOOL 2
# # # INVOICE OCR
# # # =========================================================

# # def run_invoice_ocr():

# #     st.title("📄 Invoice OCR Processing")

# #     st.markdown("---")

# #     uploaded_pdfs = st.file_uploader(
# #         "Upload Invoice PDFs",
# #         type=["pdf"],
# #         accept_multiple_files=True
# #     )

# #     if uploaded_pdfs:

# #         st.success(f"{len(uploaded_pdfs)} PDFs Uploaded")

# #         if st.button("🚀 Process Invoice PDFs"):

# #             with st.spinner("Processing PDFs..."):

# #                 df = process_invoice_pdfs(uploaded_pdfs)

# #             if df.empty:

# #                 st.error("No data extracted")

# #                 return

# #             st.success("✅ Invoice Extraction Completed")

# #             st.dataframe(
# #                 df,
# #                 use_container_width=True
# #             )

# #             output = BytesIO()

# #             with pd.ExcelWriter(
# #                 output,
# #                 engine="xlsxwriter"
# #             ) as writer:

# #                 df.to_excel(
# #                     writer,
# #                     index=False,
# #                     sheet_name="Invoices"
# #                 )

# #             output.seek(0)

# #             st.download_button(
# #                 "📥 Download Invoice Excel",
# #                 data=output,
# #                 file_name="invoice_data.xlsx",
# #                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
# #             )

# # # =========================================================
# # # MAIN
# # # =========================================================

# # if tool == "PO GRN Reconciliation":

# #     run_po_grn()

# # elif tool == "Invoice OCR Processing":

# #     run_invoice_ocr()




# import streamlit as st
# import pandas as pd
# from io import BytesIO

# # =========================================================
# # IMPORT INVOICE OCR MODULE
# # =========================================================

# from invoice_processing import process_invoice_pdfs

# # =========================================================
# # PAGE CONFIG
# # =========================================================

# st.set_page_config(
#     page_title="PO GRN Invoice Automation",
#     layout="wide"
# )

# # =========================================================
# # TITLE
# # =========================================================

# st.title("📊 PO - GRN - Invoice Reconciliation Automation")

# st.markdown("---")

# # =========================================================
# # FILE UPLOADS
# # =========================================================

# col1, col2, col3 = st.columns(3)

# with col1:

#     po_file = st.file_uploader(
#         "Upload PO File",
#         type=["xlsx", "xls"]
#     )

# with col2:

#     grn_file = st.file_uploader(
#         "Upload GRN File",
#         type=["xlsx", "xls"]
#     )

# with col3:

#     invoice_files = st.file_uploader(
#         "Upload Invoice PDFs",
#         type=["pdf"],
#         accept_multiple_files=True
#     )

# # =========================================================
# # PROCESS BUTTON
# # =========================================================

# if st.button("🚀 Generate Final Report"):

#     try:

#         # =====================================================
#         # VALIDATIONS
#         # =====================================================

#         if po_file is None:

#             st.error("Please upload PO File")
#             st.stop()

#         if grn_file is None:

#             st.error("Please upload GRN File")
#             st.stop()

#         if not invoice_files:

#             st.error("Please upload Invoice PDFs")
#             st.stop()

#         # =====================================================
#         # READ PO + GRN FILES
#         # =====================================================

#         po_df = pd.read_excel(po_file)

#         grn_df = pd.read_excel(grn_file)

#         # =====================================================
#         # CLEAN COLUMN NAMES
#         # =====================================================

#         po_df.columns = po_df.columns.str.strip()

#         grn_df.columns = grn_df.columns.str.strip()

#         # =====================================================
#         # REQUIRED COLUMNS CHECK
#         # =====================================================

#         po_required_columns = [
#             'Vendor Name',
#             'Transaction No',
#             'Basic Value'
#         ]

#         grn_required_columns = [
#             'PO',
#             'GR No.',
#             'GrandTotal'
#         ]

#         for col in po_required_columns:

#             if col not in po_df.columns:

#                 st.error(f"PO File Missing Column: {col}")
#                 st.stop()

#         for col in grn_required_columns:

#             if col not in grn_df.columns:

#                 st.error(f"GRN File Missing Column: {col}")
#                 st.stop()

#         # =====================================================
#         # PROCESS INVOICE PDFs
#         # =====================================================

#         st.markdown("---")

#         st.subheader("📄 Processing Invoice PDFs")

#         invoice_df = process_invoice_pdfs(invoice_files)

#         if invoice_df.empty:

#             st.error("No invoice data extracted")
#             st.stop()

#         # =====================================================
#         # CLEAN INVOICE COLUMN NAMES
#         # =====================================================

#         invoice_df.columns = invoice_df.columns.str.strip()

#         # =====================================================
#         # CLEAN PO NUMBERS
#         # =====================================================

#         po_df['Transaction No'] = (
#             po_df['Transaction No']
#             .astype(str)
#             .str.strip()
#             .str.upper()
#         )

#         grn_df['PO'] = (
#             grn_df['PO']
#             .astype(str)
#             .str.strip()
#             .str.upper()
#         )

#         invoice_df['PO Num'] = (
#             invoice_df['PO Num']
#             .astype(str)
#             .str.strip()
#             .str.upper()
#         )

#         # =====================================================
#         # PREPARE PO DATA
#         # =====================================================

#         po_data = po_df[[
#             'Vendor Name',
#             'Transaction No',
#             'Basic Value'
#         ]].copy()

#         po_data.columns = [
#             'Vendor',
#             'PO number',
#             'PO amount in PO Dump'
#         ]

#         # =====================================================
#         # PREPARE INVOICE DATA
#         # =====================================================

#         invoice_data = invoice_df[[
#             'Invoice Num',
#             'PO Num',
#             'Taxable Amount',
#             'Total Payable (A+B)'
#         ]].copy()

#         invoice_data.columns = [
#             'invoice number',
#             'PO number',
#             'Invoice Amount (Does not include tax)',
#             'Invoice amount in Payment Compliance sheet'
#         ]

#         # =====================================================
#         # PREPARE GRN DATA
#         # =====================================================

#         grn_data = grn_df[[
#             'PO',
#             'GR No.',
#             'GrandTotal'
#         ]].copy()

#         grn_data.columns = [
#             'PO number',
#             'GRN number',
#             'GRN amount in GRN working sheet'
#         ]

#         # =====================================================
#         # REMOVE DUPLICATES
#         # =====================================================

#         po_data = po_data.drop_duplicates()

#         invoice_data = invoice_data.drop_duplicates()

#         grn_data = grn_data.drop_duplicates()

#         # =====================================================
#         # MERGE PO + INVOICE
#         # =====================================================

#         final_df = pd.merge(
#             po_data,
#             invoice_data,
#             on='PO number',
#             how='left'
#         )

#         # =====================================================
#         # MERGE WITH GRN
#         # =====================================================

#         final_df = pd.merge(
#             final_df,
#             grn_data,
#             on='PO number',
#             how='left'
#         )

#         # =====================================================
#         # NUMERIC CONVERSION
#         # =====================================================

#         numeric_cols = [
#             'PO amount in PO Dump',
#             'Invoice amount in Payment Compliance sheet',
#             'Invoice Amount (Does not include tax)',
#             'GRN amount in GRN working sheet'
#         ]

#         for col in numeric_cols:

#             final_df[col] = (
#                 final_df[col]
#                 .astype(str)
#                 .str.replace(',', '', regex=False)
#             )

#             final_df[col] = pd.to_numeric(
#                 final_df[col],
#                 errors='coerce'
#             )

#         # =====================================================
#         # CALCULATIONS
#         # =====================================================

#         final_df['PO to GRN Match'] = (
#             final_df['PO amount in PO Dump']
#             -
#             final_df['GRN amount in GRN working sheet']
#         )

#         final_df['Invoice to GRN match'] = (
#             final_df['Invoice Amount (Does not include tax)']
#             -
#             final_df['GRN amount in GRN working sheet']
#         )

#         # =====================================================
#         # FINAL COLUMN ORDER
#         # =====================================================

#         final_columns = [
#             'Vendor',
#             'PO number',
#             'invoice number',
#             'PO amount in PO Dump',
#             'Invoice amount in Payment Compliance sheet',
#             'Invoice Amount (Does not include tax)',
#             'GRN number',
#             'GRN amount in GRN working sheet',
#             'PO to GRN Match',
#             'Invoice to GRN match'
#         ]

#         final_df = final_df[final_columns]

#         # =====================================================
#         # SUMMARY
#         # =====================================================

#         st.markdown("---")

#         st.subheader("📈 Summary")

#         c1, c2, c3 = st.columns(3)

#         with c1:

#             st.metric(
#                 "Total PO Amount",
#                 f"{final_df['PO amount in PO Dump'].sum():,.2f}"
#             )

#         with c2:

#             st.metric(
#                 "Total Invoice Amount",
#                 f"{final_df['Invoice amount in Payment Compliance sheet'].sum():,.2f}"
#             )

#         with c3:

#             st.metric(
#                 "Total GRN Amount",
#                 f"{final_df['GRN amount in GRN working sheet'].sum():,.2f}"
#             )

#         # =====================================================
#         # FINAL OUTPUT
#         # =====================================================

#         st.markdown("---")

#         st.subheader("✅ Final Reconciliation Output")

#         st.dataframe(
#             final_df,
#             use_container_width=True
#         )

#         # =====================================================
#         # DOWNLOAD EXCEL
#         # =====================================================

#         output = BytesIO()

#         with pd.ExcelWriter(
#             output,
#             engine='xlsxwriter'
#         ) as writer:

#             final_df.to_excel(
#                 writer,
#                 index=False,
#                 sheet_name='Final Output'
#             )

#             worksheet = writer.sheets['Final Output']

#             for i, col in enumerate(final_df.columns):

#                 column_len = max(
#                     final_df[col]
#                     .astype(str)
#                     .map(len)
#                     .max(),
#                     len(col)
#                 ) + 5

#                 worksheet.set_column(i, i, column_len)

#         output.seek(0)

#         st.download_button(
#             label="📥 Download Final Excel",
#             data=output,
#             file_name="PO_GRN_Invoice_Reconciliation.xlsx",
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )

#     except Exception as e:

#         st.error(f"Error: {str(e)}")

























import streamlit as st
import pandas as pd
from io import BytesIO

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="PO GRN Invoice Automation",
    layout="wide"
)

# =========================================================
# SIDEBAR MENU
# =========================================================

# tool = st.sidebar.selectbox(
#     "Select Tool",
#     [
#         "PO GRN Reconciliation"
#     ]
# )

# # # =========================================================
# # # SIDEBAR MENU
# # # =========================================================

# tool = st.sidebar.selectbox(
#     "Select Tool",
#     [
#         "PO GRN Reconciliation",
#         "Invoice OCR Processing"
#     ]
# )

# =========================================================
# TOOL 1
# PO GRN RECONCILIATION
# =========================================================

def run_po_grn():

    st.title("📊 PO - GRN - Invoice Reconciliation")

    st.markdown("---")

    # =====================================================
    # BULK FILE UPLOAD
    # =====================================================

    uploaded_files = st.file_uploader(
        "Upload All Excel Files Together",
        type=["xlsx", "xls"],
        accept_multiple_files=True
    )

    # =====================================================
    # MAIN LOGIC
    # =====================================================

    if uploaded_files:

        file_names = [file.name for file in uploaded_files]

        st.success(f"{len(uploaded_files)} Files Uploaded Successfully")

        # =================================================
        # FILE SELECTION
        # =================================================

        col1, col2, col3 = st.columns(3)

        with col1:

            po_selected = st.selectbox(
                "Select PO File",
                file_names
            )

        with col2:

            grn_selected = st.selectbox(
                "Select GRN File",
                file_names
            )

        with col3:

            invoice_selected = st.selectbox(
                "Select Invoice File",
                file_names
            )

        st.markdown("---")

        # =================================================
        # PROCESS BUTTON
        # =================================================

        if st.button("🚀 Generate Final Report"):

            try:

                po_file = None
                grn_file = None
                invoice_file = None

                # =================================================
                # GET SELECTED FILES
                # =================================================

                for file in uploaded_files:

                    if file.name == po_selected:

                        po_file = file

                    elif file.name == grn_selected:

                        grn_file = file

                    elif file.name == invoice_selected:

                        invoice_file = file

                # =================================================
                # READ FILES
                # =================================================

                po_df = pd.read_excel(po_file)

                grn_df = pd.read_excel(grn_file)

                invoice_df = pd.read_excel(invoice_file)

                # =================================================
                # CLEAN COLUMN NAMES
                # =================================================

                po_df.columns = po_df.columns.str.strip()

                grn_df.columns = grn_df.columns.str.strip()

                invoice_df.columns = invoice_df.columns.str.strip()

                # =================================================
                # PREVIEW
                # =================================================

                st.subheader("📁 File Preview")

                tab1, tab2, tab3 = st.tabs([
                    "PO File",
                    "GRN File",
                    "Invoice File"
                ])

                with tab1:

                    st.dataframe(po_df.head())

                with tab2:

                    st.dataframe(grn_df.head())

                with tab3:

                    st.dataframe(invoice_df.head())

                # =================================================
                # REQUIRED COLUMNS
                # =================================================

                po_required_columns = [
                    'Vendor Name',
                    'Transaction No',
                    'Basic Value'
                ]

                grn_required_columns = [
                    'PO',
                    'GR No.',
                    'GrandTotal'
                ]

                invoice_required_columns = [
                    'Invoice Num',
                    'PO Num',
                    'Taxable Amount',
                    'Total Payable (A+B)'
                ]

                # =================================================
                # VALIDATE PO COLUMNS
                # =================================================

                for col in po_required_columns:

                    if col not in po_df.columns:

                        st.error(f"PO File Missing Column: {col}")

                        st.stop()

                # =================================================
                # VALIDATE GRN COLUMNS
                # =================================================

                for col in grn_required_columns:

                    if col not in grn_df.columns:

                        st.error(f"GRN File Missing Column: {col}")

                        st.stop()

                # =================================================
                # VALIDATE INVOICE COLUMNS
                # =================================================

                for col in invoice_required_columns:

                    if col not in invoice_df.columns:

                        st.error(f"Invoice File Missing Column: {col}")

                        st.stop()

                # =================================================
                # PREPARE PO DATA
                # =================================================

                po_data = po_df[[
                    'Vendor Name',
                    'Transaction No',
                    'Basic Value'
                ]].copy()

                po_data.columns = [
                    'Vendor',
                    'PO number',
                    'PO amount in PO Dump'
                ]

                # =================================================
                # PREPARE INVOICE DATA
                # =================================================

                invoice_data = invoice_df[[
                    'Invoice Num',
                    'PO Num',
                    'Taxable Amount',
                    'Total Payable (A+B)'
                ]].copy()

                invoice_data.columns = [
                    'invoice number',
                    'PO number',
                    'Invoice Amount (Does not include tax)',
                    'Invoice amount in Payment Compliance sheet'
                ]

                # =================================================
                # PREPARE GRN DATA
                # =================================================

                grn_data = grn_df[[
                    'PO',
                    'GR No.',
                    'GrandTotal'
                ]].copy()

                grn_data.columns = [
                    'PO number',
                    'GRN number',
                    'GRN amount in GRN working sheet'
                ]

                # =================================================
                # CLEAN PO NUMBERS
                # =================================================

                po_data['PO number'] = (
                    po_data['PO number']
                    .astype(str)
                    .str.strip()
                )

                invoice_data['PO number'] = (
                    invoice_data['PO number']
                    .astype(str)
                    .str.strip()
                )

                grn_data['PO number'] = (
                    grn_data['PO number']
                    .astype(str)
                    .str.strip()
                )

                # =================================================
                # REMOVE DUPLICATES
                # =================================================

                po_data = po_data.drop_duplicates()

                invoice_data = invoice_data.drop_duplicates()

                grn_data = grn_data.drop_duplicates()

                # =================================================
                # MERGE PO + INVOICE
                # =================================================

                final_df = pd.merge(
                    po_data,
                    invoice_data,
                    on='PO number',
                    how='left'
                )

                # =================================================
                # MERGE WITH GRN
                # =================================================

                final_df = pd.merge(
                    final_df,
                    grn_data,
                    on='PO number',
                    how='left'
                )

                # =================================================
                # NUMERIC CONVERSION
                # =================================================

                numeric_cols = [
                    'PO amount in PO Dump',
                    'Invoice amount in Payment Compliance sheet',
                    'Invoice Amount (Does not include tax)',
                    'GRN amount in GRN working sheet'
                ]

                for col in numeric_cols:

                    final_df[col] = (
                        final_df[col]
                        .astype(str)
                        .str.replace(',', '', regex=False)
                    )

                    final_df[col] = pd.to_numeric(
                        final_df[col],
                        errors='coerce'
                    )

                # =================================================
                # MATCH CALCULATIONS
                # =================================================

                final_df['PO to GRN Match'] = (
                    final_df['PO amount in PO Dump']
                    -
                    final_df['GRN amount in GRN working sheet']
                )

                final_df['Invoice to GRN match'] = (
                    final_df['Invoice Amount (Does not include tax)']
                    -
                    final_df['GRN amount in GRN working sheet']
                )

                # =================================================
                # FINAL COLUMN ORDER
                # =================================================

                final_columns = [
                    'Vendor',
                    'PO number',
                    'invoice number',
                    'PO amount in PO Dump',
                    'Invoice amount in Payment Compliance sheet',
                    'Invoice Amount (Does not include tax)',
                    'GRN number',
                    'GRN amount in GRN working sheet',
                    'PO to GRN Match',
                    'Invoice to GRN match'
                ]

                final_df = final_df[final_columns]

                # =================================================
                # SUMMARY
                # =================================================

                st.markdown("---")

                st.subheader("📈 Summary")

                c1, c2, c3 = st.columns(3)

                with c1:

                    st.metric(
                        "Total PO Amount",
                        f"{final_df['PO amount in PO Dump'].sum():,.2f}"
                    )

                with c2:

                    st.metric(
                        "Total Invoice Amount",
                        f"{final_df['Invoice amount in Payment Compliance sheet'].sum():,.2f}"
                    )

                with c3:

                    st.metric(
                        "Total GRN Amount",
                        f"{final_df['GRN amount in GRN working sheet'].sum():,.2f}"
                    )

                # =================================================
                # OUTPUT
                # =================================================

                st.markdown("---")

                st.subheader("✅ Final Reconciliation Output")

                st.dataframe(
                    final_df,
                    use_container_width=True
                )

                # =================================================
                # DOWNLOAD
                # =================================================

                output = BytesIO()

                with pd.ExcelWriter(
                    output,
                    engine='xlsxwriter'
                ) as writer:

                    final_df.to_excel(
                        writer,
                        index=False,
                        sheet_name='Final Output'
                    )

                    worksheet = writer.sheets['Final Output']

                    for i, col in enumerate(final_df.columns):

                        column_len = max(
                            final_df[col]
                            .astype(str)
                            .map(len)
                            .max(),
                            len(col)
                        ) + 5

                        worksheet.set_column(
                            i,
                            i,
                            column_len
                        )
                
                    except:
                
                        worksheet.set_column(
                            i,
                            i,
                            20
                        )

                output.seek(0)

                st.download_button(
                    label="📥 Download Final Excel",
                    data=output,
                    file_name="PO_GRN_Invoice_Reconciliation.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:

                st.error(f"Error: {str(e)}")

# =========================================================
# MAIN
# =========================================================
run_po_grn()








