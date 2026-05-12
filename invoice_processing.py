# # invoice_processing.py

# from pdf2image import convert_from_bytes
# import pytesseract
# import pandas as pd
# import re

# CUSTOM_CONFIG = r'--oem 3 --psm 4'

# # =========================================================
# # OCR FUNCTION
# # =========================================================

# def Extract_Data(uploaded_file):

#     pdf_bytes = uploaded_file.read()

#     images = convert_from_bytes(pdf_bytes)

#     invoice_details = (50, 300, 1050, 650)
#     amount_details = (1000, 1300, 1640, 1790)

#     invoice_details_img = images[0].crop(invoice_details)
#     amount_img = images[0].crop(amount_details)

#     invoice_details_text = pytesseract.image_to_string(
#         invoice_details_img,
#         config=r'--oem 3 --psm 3'
#     )

#     invoice_details_text_2 = pytesseract.image_to_string(
#         invoice_details_img,
#         config=r'--oem 3 --psm 11'
#     )

#     amount_text = pytesseract.image_to_string(
#         amount_img,
#         config=CUSTOM_CONFIG
#     )

#     text = (
#         '\n'.join(
#             invoice_details_text
#             .replace('\n\n', '\n')
#             .split('Campaign')[:1]
#         )
#         + "\n"
#         + "\n".join(
#             invoice_details_text_2
#             .replace('\n\n', '\n')
#             .split('\n')[2:]
#         )
#         + "\n\n"
#         + amount_text.replace('\n\n', '\n')
#     )

#     return text

# # =========================================================
# # FORMAT DATA
# # =========================================================

# def data_formating(text):

#     required_fields = [
#         "Invoice Num",
#         "PO Num",
#         "Taxable Amount",
#         "Total Payable (A+B)"
#     ]

#     temp = {}

#     for line in text.strip().split("\n"):

#         match = re.match(
#             r"^(.*?)\s*:\s*(.*)$",
#             line
#         )

#         if match:

#             key = match.group(1).strip()
#             value = match.group(2).strip()

#             if key in required_fields:

#                 if value.startswith("—"):
#                     value = value.lstrip("—").strip()

#                 temp[key] = value

#     return temp

# # =========================================================
# # PROCESS PDFS
# # =========================================================

# def process_invoice_pdfs(invoice_files):

#     text_list = []

#     data = {}

#     count = 1

#     for file in invoice_files:

#         try:

#             file.seek(0)

#             text = Extract_Data(file)

#             text_list.append(text)

#         except Exception as e:

#             print(f"Error processing file {file.name}: {e}")

#     for text in text_list:

#         data[count] = data_formating(text)

#         count += 1

#     df = pd.DataFrame.from_dict(
#         data,
#         orient="index"
#     )

#     df.reset_index(
#         drop=True,
#         inplace=True
#     )

#     if not df.empty:

#         df.columns = df.columns.str.strip()

#     return df













# invoice_processing.py

import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract
import pandas as pd
import re

# =========================================================
# OCR CONFIG
# =========================================================

CUSTOM_CONFIG = r'--oem 3 --psm 4'

# =========================================================
# EXTRACT DATA FROM PDF
# =========================================================

def extract_data(uploaded_file):

    try:

        st.write(f"📄 Reading PDF: {uploaded_file.name}")

        pdf_bytes = uploaded_file.read()

        images = convert_from_bytes(pdf_bytes)

        st.success("✅ PDF Converted to Image")

        invoice_details = (50, 300, 1050, 650)

        amount_details = (1000, 1300, 1640, 1790)

        invoice_img = images[0].crop(invoice_details)

        amount_img = images[0].crop(amount_details)

        st.success("✅ Image Cropping Done")

        # =================================================
        # OCR
        # =================================================

        invoice_text_1 = pytesseract.image_to_string(
            invoice_img,
            config=r'--oem 3 --psm 3'
        )

        invoice_text_2 = pytesseract.image_to_string(
            invoice_img,
            config=r'--oem 3 --psm 11'
        )

        amount_text = pytesseract.image_to_string(
            amount_img,
            config=r'--oem 3 --psm 4'
        )

        # =================================================
        # IMPORTANT
        # USE OLD WORKING LOGIC
        # =================================================

        final_text = (
            '\n'.join(
                invoice_text_1
                .replace('\n\n', '\n')
                .split('Campaign')[:1]
            )
            + "\n"
            + "\n".join(
                invoice_text_2
                .replace('\n\n', '\n')
                .split('\n')[2:]
            )
            + "\n\n"
            + amount_text.replace('\n\n', '\n')
        )

        st.success("✅ OCR Extraction Completed")

        return final_text

    except Exception as e:

        st.error(f"❌ Error in OCR Processing: {uploaded_file.name}")

        st.exception(e)

        return None

# =========================================================
# FORMAT EXTRACTED DATA
# =========================================================

def format_data(text):

    try:

        required_fields = [
            "Invoice Num",
            "PO Num",
            "Taxable Amount",
            "Total Payable (A+B)"
        ]

        row_data = {}

        lines = text.split("\n")

        for line in lines:

            match = re.match(
                r"^(.*?)\s*:\s*(.*)$",
                line
            )

            if match:

                key = match.group(1).strip()

                value = match.group(2).strip()

                if key in required_fields:

                    value = (
                        value
                        .replace("₹", "")
                        # .replace(",", "")
                        .replace("—", "")
                        .strip()
                    )

                    row_data[key] = value

        return row_data

    except Exception as e:

        st.error("❌ Error while formatting extracted data")

        st.exception(e)

        return {}

# =========================================================
# MAIN FUNCTION
# =========================================================

def process_invoice_pdfs(invoice_files):

    try:

        final_data = []

        for file in invoice_files:

            st.markdown("---")

            st.write(f"🚀 Processing File: {file.name}")

            try:

                # RESET FILE POINTER
                file.seek(0)

                # =============================================
                # OCR
                # =============================================

                text = extract_data(file)

                if not text:

                    st.warning(f"⚠ No OCR text extracted from {file.name}")

                    continue

                # =============================================
                # FORMAT DATA
                # =============================================

                row = format_data(text)

                if not row:

                    st.warning(f"⚠ No fields extracted from {file.name}")

                # =============================================
                # ADD FILE NAME
                # =============================================

                row["File Name"] = file.name

                final_data.append(row)

                st.success(f"✅ Successfully Processed: {file.name}")

            except Exception as e:

                st.error(f"❌ Failed Processing: {file.name}")

                st.exception(e)

        # =================================================
        # FINAL DATAFRAME
        # =================================================

        df = pd.DataFrame(final_data)

        # =================================================
        # SHOW FINAL RESULT
        # =================================================

        if df.empty:

            st.error("❌ No data extracted from uploaded PDFs")

        else:

            st.success("✅ Invoice Data Extracted Successfully")

            st.dataframe(df)

        return df

    except Exception as e:

        st.error("❌ Main Processing Error")

        st.exception(e)

        return pd.DataFrame()
