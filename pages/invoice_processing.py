# invoice_processing.py

import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract
import pandas as pd
import re

# =========================================================
# OCR FUNCTION
# =========================================================

def Extract_Data(uploaded_file):

    custom_config = r'--oem 3 --psm 4'

    # =====================================================
    # READ PDF BYTES
    # =====================================================

    pdf_bytes = uploaded_file.read()

    # =====================================================
    # CONVERT PDF TO IMAGE
    # =====================================================

    # images = convert_from_bytes(pdf_bytes)
    images = convert_from_bytes(pdf_bytes)

    # =====================================================
    # CROP COORDINATES
    # =====================================================

    invoice_details = (50,300,1050,650)

    amount_details = (1000,1300,1640,1790)

    # =====================================================
    # CROP IMAGES
    # =====================================================

    invoice_details_img = images[0].crop(invoice_details)

    amount_img = images[0].crop(amount_details)
    # invoice_details_img = invoice_details_img.convert("L")
    
    amount_img = amount_img.convert("L")
    # st.image(amount_img, caption="Amount Crop")

    # =====================================================
    # OCR
    # =====================================================

    invoice_details_text = pytesseract.image_to_string(
        invoice_details_img,
        config = r'--oem 3 --psm 3'
    )

    invoice_details_text_2 = pytesseract.image_to_string(
        invoice_details_img,
        config = r'--oem 3 --psm 11'
    )

    amount_text = pytesseract.image_to_string(
        amount_img,
        config = custom_config
    )

    # =====================================================
    # FINAL TEXT
    # =====================================================

    text = (
        '\n'.join(
            invoice_details_text
            .replace('\n\n','\n')
            .split('Campaign')[:1]
        )
        + "\n"
        + "\n".join(
            invoice_details_text_2
            .replace('\n\n','\n')
            .split('\n')[2:]
        )
        + "\n\n"
        + amount_text.replace('\n\n','\n')
    )

    return text

# =========================================================
# DATA FORMATTING
# =========================================================

def data_formating(text):

    required_fields = [
        "Invoice Num",
        "PO Num",
        "Taxable Amount",
        "Total Payable (A+B)"
    ]

    temp = {}

    for line in text.strip().split("\n"):

        match = re.match(
            r"^(.*?)\s*:\s*(.*)$",
            line
        )

        if match:

            key = match.group(1).strip()

            value = match.group(2).strip()

            # =================================================
            # KEEP ONLY REQUIRED FIELDS
            # =================================================

            if key in required_fields:

                # # REMOVE LEADING DASH
                # if value.startswith("—"):

                #     value = value.lstrip("—").strip()

                # temp[key] = value

                if value.startswith("—"):

                    value = value.lstrip("—").strip()
                
                # CLEAN OCR GARBAGE
                value = re.sub(r'[^0-9A-Za-z,./()-]', '', value)
                
                # FIX AMOUNT FIELDS
                if key in ["Taxable Amount", "Total Payable (A+B)"]:
                
                    value = re.sub(r'[^0-9,.]', '', value)
                
                temp[key] = value

    return temp

# =========================================================
# MAIN PROCESS FUNCTION
# =========================================================

def process_invoice_pdfs(invoice_files):

    text_list = []

    data = {}

    count = 1

    # =====================================================
    # OCR EXTRACTION
    # =====================================================

    for file in invoice_files:

        try:

            st.write(f"📄 Processing: {file.name}")

            file.seek(0)

            text = Extract_Data(file)

            text_list.append(text)

            st.success(f"✅ OCR Completed: {file.name}")

        except Exception as e:

            st.error(f"❌ Error Processing {file.name}")

            st.exception(e)

    # =====================================================
    # FORMAT DATA
    # =====================================================

    for text in text_list:

        data[count] = data_formating(text)

        count += 1

    # =====================================================
    # DATAFRAME
    # =====================================================

    df = pd.DataFrame.from_dict(
        data,
        orient="index"
    )

    # =====================================================
    # RESET INDEX
    # =====================================================

    df.reset_index(
        drop=True,
        inplace=True
    )

    # =====================================================
    # CLEAN COLUMN NAMES
    # =====================================================

    if not df.empty:

        df.columns = df.columns.str.strip()

    # =====================================================
    # SHOW DATA
    # =====================================================

    st.success("✅ Invoice Data Extracted Successfully")

    st.dataframe(df)

    return df





# =========================================================
# PAGE UI
# =========================================================

st.set_page_config(
    page_title="Invoice OCR Processing",
    layout="wide"
)

st.title("📄 Invoice OCR Processing")

st.markdown("---")

uploaded_pdfs = st.file_uploader(
    "Upload Invoice PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_pdfs:

    st.success(f"{len(uploaded_pdfs)} PDFs Uploaded")

    if st.button("🚀 Process Invoice PDFs"):

        with st.spinner("Processing PDFs..."):

            df = process_invoice_pdfs(uploaded_pdfs)

        if df.empty:

            st.error("No data extracted")

        else:

            st.success("✅ Invoice Extraction Completed")

            st.dataframe(
                df,
                use_container_width=True
            )
