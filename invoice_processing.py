# invoice_processing.py

from pdf2image import convert_from_bytes
import pytesseract
import pandas as pd
import re

CUSTOM_CONFIG = r'--oem 3 --psm 4'

# =========================================================
# OCR FUNCTION
# =========================================================

def Extract_Data(uploaded_file):

    pdf_bytes = uploaded_file.read()

    images = convert_from_bytes(pdf_bytes)

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
        config=CUSTOM_CONFIG
    )

    text = (
        '\n'.join(
            invoice_details_text
            .replace('\n\n', '\n')
            .split('Campaign')[:1]
        )
        + "\n"
        + "\n".join(
            invoice_details_text_2
            .replace('\n\n', '\n')
            .split('\n')[2:]
        )
        + "\n\n"
        + amount_text.replace('\n\n', '\n')
    )

    return text

# =========================================================
# FORMAT DATA
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

            if key in required_fields:

                if value.startswith("—"):
                    value = value.lstrip("—").strip()

                temp[key] = value

    return temp

# =========================================================
# PROCESS PDFS
# =========================================================

def process_invoice_pdfs(invoice_files):

    text_list = []

    data = {}

    count = 1

    for file in invoice_files:

        try:

            file.seek(0)

            text = Extract_Data(file)

            text_list.append(text)

        except Exception as e:

            print(f"Error processing file {file.name}: {e}")

    for text in text_list:

        data[count] = data_formating(text)

        count += 1

    df = pd.DataFrame.from_dict(
        data,
        orient="index"
    )

    df.reset_index(
        drop=True,
        inplace=True
    )

    if not df.empty:

        df.columns = df.columns.str.strip()

    return df
