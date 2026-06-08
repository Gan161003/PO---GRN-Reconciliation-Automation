# # invoice_processing.py

# import streamlit as st
# from pdf2image import convert_from_bytes
# import pytesseract
# import pandas as pd
# import re
# from io import BytesIO


# # =========================================================
# # OCR FUNCTION
# # =========================================================

# def Extract_Data(uploaded_file):

#     custom_config = r'--oem 3 --psm 4'

#     # =====================================================
#     # READ PDF BYTES
#     # =====================================================

#     pdf_bytes = uploaded_file.read()

#     # =====================================================
#     # CONVERT PDF TO IMAGE
#     # =====================================================

#     # images = convert_from_bytes(pdf_bytes)
#     images = convert_from_bytes(pdf_bytes)

#     # =====================================================
#     # CROP COORDINATES
#     # =====================================================

#     invoice_details = (50,300,1050,650)

#     amount_details = (1000,1300,1640,1790)

#     # =====================================================
#     # CROP IMAGES
#     # =====================================================

#     invoice_details_img = images[0].crop(invoice_details)

#     amount_img = images[0].crop(amount_details)
#     # invoice_details_img = invoice_details_img.convert("L")
    
#     amount_img = amount_img.convert("L")
#     # st.image(amount_img, caption="Amount Crop")

#     # =====================================================
#     # OCR
#     # =====================================================

#     invoice_details_text = pytesseract.image_to_string(
#         invoice_details_img,
#         config = r'--oem 3 --psm 3'
#     )

#     invoice_details_text_2 = pytesseract.image_to_string(
#         invoice_details_img,
#         config = r'--oem 3 --psm 11'
#     )

#     amount_text = pytesseract.image_to_string(
#         amount_img,
#         config = custom_config
#     )

#     # =====================================================
#     # FINAL TEXT
#     # =====================================================

#     text = (
#         '\n'.join(
#             invoice_details_text
#             .replace('\n\n','\n')
#             .split('Campaign')[:1]
#         )
#         + "\n"
#         + "\n".join(
#             invoice_details_text_2
#             .replace('\n\n','\n')
#             .split('\n')[2:]
#         )
#         + "\n\n"
#         + amount_text.replace('\n\n','\n')
#     )

#     return text

# # =========================================================
# # DATA FORMATTING
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

#             # =================================================
#             # KEEP ONLY REQUIRED FIELDS
#             # =================================================

#             if key in required_fields:

#                 # # REMOVE LEADING DASH
#                 # if value.startswith("—"):

#                 #     value = value.lstrip("—").strip()

#                 # temp[key] = value

#                 if value.startswith("—"):

#                     value = value.lstrip("—").strip()
                
#                 # CLEAN OCR GARBAGE
#                 value = re.sub(r'[^0-9A-Za-z,./()-]', '', value)
                
#                 # FIX AMOUNT FIELDS
#                 if key in ["Taxable Amount", "Total Payable (A+B)"]:
                
#                     value = re.sub(r'[^0-9,.]', '', value)
                
#                 temp[key] = value

#     return temp

# # =========================================================
# # MAIN PROCESS FUNCTION
# # =========================================================

# def process_invoice_pdfs(invoice_files):

#     text_list = []

#     data = {}

#     count = 1

#     # =====================================================
#     # OCR EXTRACTION
#     # =====================================================

#     for file in invoice_files:

#         try:

#             st.write(f"📄 Processing: {file.name}")

#             file.seek(0)

#             text = Extract_Data(file)

#             text_list.append(text)

#             st.success(f"✅ OCR Completed: {file.name}")

#         except Exception as e:

#             st.error(f"❌ Error Processing {file.name}")

#             st.exception(e)

#     # =====================================================
#     # FORMAT DATA
#     # =====================================================

#     for text in text_list:

#         data[count] = data_formating(text)

#         count += 1

#     # =====================================================
#     # DATAFRAME
#     # =====================================================

#     df = pd.DataFrame.from_dict(
#         data,
#         orient="index"
#     )

#     # =====================================================
#     # RESET INDEX
#     # =====================================================

#     df.reset_index(
#         drop=True,
#         inplace=True
#     )

#     # =====================================================
#     # CLEAN COLUMN NAMES
#     # =====================================================

#     if not df.empty:

#         df.columns = df.columns.str.strip()

#     # =====================================================
#     # SHOW DATA
#     # =====================================================

#     st.success("✅ Invoice Data Extracted Successfully")

#     st.dataframe(df)

#     return df





# # =========================================================
# # PAGE UI
# # =========================================================

# st.set_page_config(
#     page_title="Invoice OCR Processing",
#     layout="wide"
# )

# st.title("📄 Invoice OCR Processing")

# st.markdown("---")

# uploaded_pdfs = st.file_uploader(
#     "Upload Invoice PDFs",
#     type=["pdf"],
#     accept_multiple_files=True
# )

# if uploaded_pdfs:

#     st.success(f"{len(uploaded_pdfs)} PDFs Uploaded")

#     if st.button("🚀 Process Invoice PDFs"):

#         with st.spinner("Processing PDFs..."):

#             df = process_invoice_pdfs(uploaded_pdfs)

#         if df.empty:

#             st.error("No data extracted")

#         else:

#             st.success("✅ Invoice Extraction Completed")

#             st.dataframe(
#                 df,
#                 use_container_width=True
#             )
#             output = BytesIO()

#             with pd.ExcelWriter(
#                 output,
#                 engine="xlsxwriter"
#             ) as writer:
            
#                 df.to_excel(
#                     writer,
#                     index=False,
#                     sheet_name="Invoices"
#                 )
            
#             output.seek(0)
            
#             st.download_button(
#                 label="📥 Download Invoice Excel",
#                 data=output,
#                 file_name="invoice_data.xlsx",
#                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#             )










import streamlit as st
import pandas as pd
import pytesseract
import re
from pdf2image import convert_from_bytes
from io import BytesIO

# ==========================================
# CONFIG
# ==========================================

POPPLER_PATH = r"C:\poppler-24.08.0\Library\bin"

# ==========================================
# MADISON
# ==========================================

def Extract_Data_Madison(pdf_bytes):

    images = convert_from_bytes(
        pdf_bytes,
        poppler_path=POPPLER_PATH
    )

    invoice_details = (50, 300, 1050, 650)
    amount_details = (1000, 1300, 1640, 1790)

    invoice_details_img = images[0].crop(invoice_details)
    amount_img = images[0].crop(amount_details)

    invoice_details_text = pytesseract.image_to_string(
        invoice_details_img,
        config=r'--oem 3 --psm 3'
    )

    invoice_details_text_2 = pytesseract.image_to_string(
        invoice_details_img,
        config=r'--oem 3 --psm 11'
    )

    amount_text = pytesseract.image_to_string(
        amount_img,
        config=r'--oem 3 --psm 4'
    )

    text = (
        '\n'.join(
            invoice_details_text.replace('\n\n', '\n')
            .split('Campaign')[:1]
        )
        + "\n"
        + "\n".join(
            invoice_details_text_2.replace('\n\n', '\n')
            .split('\n')[2:]
        )
        + "\n\n"
        + amount_text.replace('\n\n', '\n')
    )

    return text


def data_formating_Madison(text):

    required_fields = [
        "Invoice Num",
        "PO Num",
        "Taxable Amount",
        "Total Payable (A+B)"
    ]

    temp = {}

    for line in text.strip().split("\n"):

        match = re.match(r"^(.*?)\s*:\s*(.*)$", line)

        if match:

            key = match.group(1).strip()
            value = match.group(2).strip()

            if key in required_fields:

                if value.startswith("—"):
                    value = value.lstrip("—").strip()

                temp[key] = value

    return temp


# ==========================================
# META
# ==========================================

def Extract_Data_Meta(pdf_bytes):

    images = convert_from_bytes(
        pdf_bytes,
        poppler_path=POPPLER_PATH
    )

    invoice_details = (1040, 165, 1600, 390)
    amount_details = (1125, 1730, 1650, 1970)

    invoice_details_img = images[0].crop(invoice_details)
    amount_img = images[0].crop(amount_details)

    invoice_details_text = pytesseract.image_to_string(
        invoice_details_img,
        config=r'--oem 3 --psm 4'
    )

    amount_text = pytesseract.image_to_string(
        amount_img,
        config=r'--oem 3 --psm 6'
    )

    text = (
        invoice_details_text.replace('\n\n', '\n')
        + amount_text.replace('\n\n', '\n')
    )

    return text


def data_formating_Meta(text):

    required_fields = [
        "Invoice #",
        "PO Num",
        "Subtotal",
        "Invoice Total"
    ]

    temp = {}

    for line in text.strip().split("\n"):

        match = re.match(r"^(.*?)\s*:\s*(.*)$", line)

        if match:

            key = match.group(1).strip()
            value = match.group(2).strip()

            if key in required_fields:

                if value.startswith("—"):
                    value = value.lstrip("—").strip()

                temp[key] = value

    return temp


# ==========================================
# GOOGLE
# ==========================================

def Extract_Data_Google(pdf_bytes):

    images = convert_from_bytes(
        pdf_bytes,
        poppler_path=POPPLER_PATH
    )

    invoice_details = (90, 900, 750, 1050)
    amount_details = (800, 1250, 1600, 1450)

    invoice_details_img = images[0].crop(invoice_details)
    amount_img = images[0].crop(amount_details)

    invoice_details_text = pytesseract.image_to_string(
        invoice_details_img,
        config=r'--oem 3 --psm 6'
    )

    amount_text = pytesseract.image_to_string(
        amount_img,
        config=r'--oem 3 --psm 6'
    )

    text = (
        "\n".join([
            re.sub(r'\s*\.+\s*', ': ', i)
            for i in invoice_details_text.split("\n")
        ])
        + amount_text.replace('\n\n', '\n')
    )

    return text


def data_formating_Google(text):

    required_fields = [
        "Invoice number",
        "PO Num",
        "Subtotal",
        "Total amount"
    ]

    temp = {}

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if ':' in line:

            key, value = line.split(':', 1)

            if value.strip():

                if key.strip() in required_fields:
                    temp[key.strip()] = value.strip()

        else:

            m = re.search(r'^(.*?)\s*%?([\d,]+\.\d+)', line)

            if m:

                key = m.group(1).strip()
                value = m.group(2)

                key = re.sub(
                    r'\s+in\s+INR$',
                    '',
                    key,
                    flags=re.I
                )

                key = re.sub(
                    r'\s+due$',
                    '',
                    key,
                    flags=re.I
                )

                if key in required_fields:
                    temp[key] = value

    return temp


# ==========================================
# LOKMAT
# ==========================================

def Extract_Data_Lokmat(pdf_bytes):

    images = convert_from_bytes(
        pdf_bytes,
        poppler_path=POPPLER_PATH
    )

    invoice_details = (150, 200, 700, 290)
    amount_details = (940, 1260, 1490, 1480)

    invoice_details_img = images[0].crop(invoice_details)
    amount_img = images[0].crop(amount_details)

    invoice_details_text = pytesseract.image_to_string(
        invoice_details_img,
        config=r'--oem 3 --psm 4'
    )

    amount_text = pytesseract.image_to_string(
        amount_img,
        config=r'--oem 3 --psm 4'
    )

    text = (
        "\n".join([
            re.sub(r'\s*\.+\s*', ': ', i)
            for i in invoice_details_text.split("\n")
        ])
        + amount_text.replace('\n\n', '\n')
    )

    return text


def data_formating_Lokmat(text):

    required_fields = [
        "Invoice No",
        "PO Num",
        "Taxable Value",
        "Total Invoice Value"
    ]

    temp = {}

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if ':' in line:

            key, value = line.split(':', 1)

            if value.strip():

                if key.strip() in required_fields:
                    temp[key.strip()] = value.strip()

        else:

            m = re.search(r'^(.*?)\s*%?([\d,]+\.\d+)', line)

            if m:

                key = m.group(1).strip()
                value = m.group(2)

                key = re.sub(
                    r'\s*\([^)]*\)',
                    '',
                    key
                )

                if key.strip() in required_fields:
                    temp[key] = value

    return temp


# ==========================================
# DETECT FILE TYPE
# ==========================================

def check_file(pdf_bytes):

    images = convert_from_bytes(
        pdf_bytes,
        poppler_path=POPPLER_PATH
    )

    text = pytesseract.image_to_string(
        images[0],
        config=r'--oem 3 --psm 4'
    )

    if 'madison' in text.lower():
        return data_formating_Madison(
            Extract_Data_Madison(pdf_bytes)
        )

    elif 'meta' in text.lower():
        return data_formating_Meta(
            Extract_Data_Meta(pdf_bytes)
        )

    elif 'google' in text.lower():
        return data_formating_Google(
            Extract_Data_Google(pdf_bytes)
        )

    elif 'lokmat' in text.lower():
        return data_formating_Lokmat(
            Extract_Data_Lokmat(pdf_bytes)
        )

    return {}


# ==========================================
# NORMALIZE COLUMNS
# ==========================================

def col_normalize(df):

    df["Invoice Number"] = df[
        ["Invoice Num",
         "Invoice #",
         "Invoice number",
         "Invoice No"]
    ].bfill(axis=1).iloc[:, 0]

    df["Taxable Amount"] = df[
        ["Taxable Amount",
         "Subtotal",
         "Taxable Value"]
    ].bfill(axis=1).iloc[:, 0]

    df["Total Amount"] = df[
        ["Total Payable (A+B)",
         "Invoice Total",
         "Total amount",
         "Total Invoice Value"]
    ].bfill(axis=1).iloc[:, 0]

    cols_to_drop = [
        "Invoice Num",
        "Invoice #",
        "Invoice number",
        "Invoice No",
        "Subtotal",
        "Taxable Value",
        "Total Payable (A+B)",
        "Invoice Total",
        "Total amount",
        "Total Invoice Value"
    ]

    df = df.drop(
        columns=cols_to_drop,
        errors="ignore"
    )

    return df[
        [
            "Invoice Number",
            "PO Num",
            "Taxable Amount",
            "Total Amount"
        ]
    ]


# ==========================================
# STREAMLIT UI
# ==========================================

st.set_page_config(
    page_title="Invoice OCR Extractor",
    layout="wide"
)

st.title("📄 Invoice OCR Extractor")

uploaded_files = st.file_uploader(
    "Upload PDF Files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:

    results = {}
    count = 1

    with st.spinner("Processing PDFs..."):

        for file in uploaded_files:

            pdf_bytes = file.read()

            results[count] = check_file(pdf_bytes)

            results[count]["File Name"] = file.name

            count += 1

    df = pd.DataFrame.from_dict(
        results,
        orient="index"
    )

    df.reset_index(
        drop=True,
        inplace=True
    )

    df = col_normalize(df)

    cols = [
        "File Name",
        "Invoice Number",
        "PO Num",
        "Taxable Amount",
        "Total Amount"
    ]

    df = df[cols]

    st.success("Processing Completed")

    st.dataframe(
        df,
        use_container_width=True
    )

    excel_buffer = BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False
        )

    st.download_button(
        label="📥 Download Excel",
        data=excel_buffer.getvalue(),
        file_name="invoice_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
