import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract
import pandas as pd
import re
from io import BytesIO

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Invoice OCR Processing",
    layout="wide"
)

# =========================================================
# PROCESS PDFs
# =========================================================

def process_invoice_pdfs(invoice_files):

    results = {}

    progress_bar = st.progress(0)

    for idx, file in enumerate(invoice_files):

        try:

            st.write(
                f"📄 Processing: {file.name}"
            )

            # file.seek(0)
            pdf_bytes = file.getvalue()
            results[idx] = check_file(pdf_bytes)

            results[idx]["File Name"] = file.name

        except Exception as e:

            st.error(
                f"❌ Failed: {file.name}"
            )

            st.exception(e)

        progress_bar.progress(
            (idx + 1) / len(invoice_files)
        )
    st.success("✅ Completed: All PDFs Processed")

    df = pd.DataFrame.from_dict(results, orient='index')

    df=col_normalize(df)
    return df

# =========================================================
# OCR FUNCTION
# =========================================================

def check_file(path):
    POPPLER_PATH = r"C:\poppler-24.08.0\Library\bin"
    
    custom_config = r'--oem 3 --psm 4'

    # Convert PDF pages to images  poppler_path=poppler_path
    images = convert_from_bytes(path, poppler_path=poppler_path)

    text = pytesseract.image_to_string(images[0], config=custom_config)
    
    if 'madison' in text.lower():
        return data_formating_Madison(Extract_Data_Madison(path))
    elif 'meta' in text.lower():
        return data_formating_Meta(Extract_Data_Meta(path))
    elif 'google' in text.lower():
        return data_formating_Google(Extract_Data_Google(path))
    elif 'lokmat' in text.lower():
        return data_formating_Lokmat(Extract_Data_Lokmat(path))

def Extract_Data_Madison(path):
    # Specify Poppler path directly
    poppler_path = r"C:\poppler-24.08.0\Library\bin"
    
    custom_config = r'--oem 3 --psm 4'

    # Convert PDF pages to images  poppler_path=poppler_path
    images = convert_from_bytes(path, poppler_path=poppler_path)
    
    invoice_details = (50,300,1050,650)
    amount_details = (1000,1300,1640,1790)
    
    invoice_details_img = images[0].crop(invoice_details)
    amount_img = images[0].crop(amount_details)

    invoice_details_text = pytesseract.image_to_string(invoice_details_img, config = r'--oem 3 --psm 3' )#config=custom_config
    invoice_details_text_2 = pytesseract.image_to_string(invoice_details_img, config = r'--oem 3 --psm 11' )
    amount_text = pytesseract.image_to_string(amount_img, config=custom_config)

    text = '\n'.join(invoice_details_text.replace('\n\n','\n').split('Campaign')[:1]) + "\n" +"\n".join(invoice_details_text_2.replace('\n\n','\n').split('\n')[2:]) + "\n\n" + amount_text.replace('\n\n','\n')

    return text

def data_formating_Madison(text):
    # Required fields only
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
    
            # Keep only required fields
            if key in required_fields:
    
                # Remove leading "-"
                if value.startswith("—"):
                    value = value.lstrip("—").strip()
    
                temp[key] = value
    return temp

def Extract_Data_Meta(path):
    # Specify Poppler path directly
    poppler_path = r"C:\poppler-24.08.0\Library\bin"
    
    custom_config = r'--oem 3 --psm 4'

    # Convert PDF pages to images  poppler_path=poppler_path
    images = convert_from_bytes(path, poppler_path=poppler_path)
    
    invoice_details = (1040,165,1600,390)
    amount_details =  (1125,1730,1650,1970)
    
    invoice_details_img = images[0].crop(invoice_details)
    amount_img = images[0].crop(amount_details)

    
    invoice_details_text = pytesseract.image_to_string(invoice_details_img, config = r'--oem 3 --psm 4' )#config=custom_config
    amount_text = pytesseract.image_to_string(amount_img, config=r'--oem 3 --psm 6')

    text = invoice_details_text.replace('\n\n','\n')+amount_text.replace('\n\n','\n')
    return text

def data_formating_Meta(text):
    # Required fields only
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
    
            # Keep only required fields
            if key in required_fields:
    
                # Remove leading "-"
                if value.startswith("—"):
                    value = value.lstrip("—").strip()
    
                temp[key] = value
            
    return temp

def Extract_Data_Google(path):
    # Specify Poppler path directly
    poppler_path = r"C:\poppler-24.08.0\Library\bin"
    
    custom_config = r'--oem 3 --psm 4'

    # Convert PDF pages to images  poppler_path=poppler_path
    images = convert_from_bytes(path, poppler_path=poppler_path)
    
    invoice_details = (90,900,750,1050)
    amount_details = (800,1250,1600,1450)

    invoice_details_img = images[0].crop(invoice_details)
    amount_img = images[0].crop(amount_details)
    
    invoice_details_text = pytesseract.image_to_string(invoice_details_img, config = r'--oem 3 --psm 6' )
    amount_text = pytesseract.image_to_string(amount_img, config = r'--oem 3 --psm 6')
    
    text ="\n".join([re.sub(r'\s*\.+\s*', ': ', i) for i in invoice_details_text.split("\n")]) + amount_text.replace('\n\n','\n')
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
    
        # Normal key:value lines
        if ':' in line:
            key, value = line.split(':', 1)
        
            if value.strip():  # Skip empty values like "Pay in INR:"
                if key in required_fields:
                    temp[key.strip()] = value.strip()
    
        # Amount lines
        else:
            m = re.search(r'^(.*?)\s*%?([\d,]+\.\d+)', line)
    
            if m:
                key = m.group(1).strip()
                value = m.group(2)
        
                key = re.sub(r'\s+in\s+INR$', '', key, flags=re.I)
                key = re.sub(r'\s+due$', '', key, flags=re.I)
                if key in required_fields:    
                    temp[key] = value
    return temp

def Extract_Data_Lokmat(path):
    # Specify Poppler path directly
    poppler_path = r"C:\poppler-24.08.0\Library\bin"
    
    custom_config = r'--oem 3 --psm 4'

    # Convert PDF pages to images  poppler_path=poppler_path
    images = convert_from_bytes(path, poppler_path=poppler_path)
    
    invoice_details = (150,200,700,290)
    amount_details = (940,1260,1490,1480)

    invoice_details_img = images[0].crop(invoice_details)
    amount_img = images[0].crop(amount_details)
    
    invoice_details_text = pytesseract.image_to_string(invoice_details_img, config = custom_config )
    amount_text = pytesseract.image_to_string(amount_img, config = custom_config)
    
    text ="\n".join([re.sub(r'\s*\.+\s*', ': ', i) for i in invoice_details_text.split("\n")]) + amount_text.replace('\n\n','\n')
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
    
        # Normal key:value lines
        if ':' in line:
            key, value = line.split(':', 1)
            if value.strip():  # Skip empty values like "Pay in INR:"
                if key.strip() in required_fields:
                    temp[key.strip()] = value.strip()
        # Amount lines
        else:
            m = re.search(r'^(.*?)\s*%?([\d,]+\.\d+)', line)
            if m:
                key = m.group(1).strip()
                value = m.group(2)
                
                key = key = re.sub(r'\s*\([^)]*\)', '', key)
                if key.strip() in required_fields:    
                    temp[key] = value
    return temp

def col_normalize(df):
    # df["Invoice Number"] = df[
    #     ["Invoice Num", "Invoice #", "Invoice number", "Invoice No"]
    # ].bfill(axis=1).iloc[:, 0]
    
    # # Taxable Amount
    # df["Taxable Amount"] = df[
    #     ["Taxable Amount", "Subtotal", "Taxable Value"]
    # ].bfill(axis=1).iloc[:, 0]
    
    # # Total Amount
    # df["Total Amount"] = df[
    #     ["Total Payable (A+B)", "Invoice Total", "Total amount", "Total Invoice Value"]
    # ].bfill(axis=1).iloc[:, 0]

    # cols_to_drop = [
    #     "Invoice Num", "Invoice #", "Invoice number", "Invoice No", "Subtotal", "Taxable Value",
    #     "Total Payable (A+B)", "Invoice Total", "Total amount", "Total Invoice Value"
    # ]
    
    # df = df.drop(columns=cols_to_drop, errors="ignore")
    # df = df[["File Name","Invoice Number", "PO Num", "Taxable Amount", "Total Amount"]]
    invoice_cols = ["Invoice Num", "Invoice #", "Invoice number", "Invoice No"]
    taxable_cols = ["Taxable Amount", "Subtotal", "Taxable Value"]
    total_cols = ["Total Payable (A+B)", "Invoice Total", "Total amount", "Total Invoice Value"]

    # Invoice Number
    existing_invoice_cols = [col for col in invoice_cols if col in df.columns]
    if existing_invoice_cols:
        df["Invoice Number"] = df[existing_invoice_cols].bfill(axis=1).iloc[:, 0]
    else:
        df["Invoice Number"] = pd.NA

    # Taxable Amount
    existing_taxable_cols = [col for col in taxable_cols if col in df.columns]
    if existing_taxable_cols:
        df["Taxable Amount"] = df[existing_taxable_cols].bfill(axis=1).iloc[:, 0]
    else:
        df["Taxable Amount"] = pd.NA

    # Total Amount
    existing_total_cols = [col for col in total_cols if col in df.columns]
    if existing_total_cols:
        df["Total Amount"] = df[existing_total_cols].bfill(axis=1).iloc[:, 0]
    else:
        df["Total Amount"] = pd.NA


    # Keep only columns that exist
    final_cols = [
        "File Name",
        "Invoice Number",
        "PO Num",
        "Taxable Amount",
        "Total Amount"
    ]

    df = df.reindex(columns=final_cols)
    return df

# =========================================================
# EXCEL DOWNLOAD
# =========================================================

def get_excel_download(df):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Invoices"
        )

    output.seek(0)

    return output

# =========================================================
# UI
# =========================================================

st.title("📄 Invoice OCR Processing")

st.markdown("---")

uploaded_pdfs = st.file_uploader(
    "Upload Invoice PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_pdfs:

    st.success(
        f"{len(uploaded_pdfs)} PDF(s) Uploaded"
    )

    if st.button(
        "🚀 Process Invoices",
        use_container_width=True
    ):

        with st.spinner(
            "Processing PDFs..."
        ):

            df = process_invoice_pdfs(
                uploaded_pdfs
            )

        st.markdown("---")

        if df.empty:

            st.error(
                "No data extracted."
            )

        else:

            st.success(
                "✅ Invoice Extraction Completed"
            )

            st.dataframe(
                df,
                use_container_width=True
            )

            excel_file = get_excel_download(
                df
            )

            st.download_button(
                label="📥 Download Excel",
                data=excel_file,
                file_name="invoice_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
