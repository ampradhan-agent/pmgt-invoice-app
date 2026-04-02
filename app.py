import streamlit as st
from fpdf import FPDF
from datetime import date
import pandas as pd

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Pradhan Management Invoice Generator", layout="centered")

# Company Constants
COMPANY_NAME = "Pradhan Management LLC"
COMPANY_ADDRESS = "4800 Heritage Oaks Drive, Frisco, TX 75034"
COMPANY_PHONE = "972-712-1077"
COMPANY_EMAIL = "contact@pradhanmanagement.com"

# --- PDF GENERATION FUNCTION ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, COMPANY_NAME, ln=True, align='L')
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, f"{COMPANY_ADDRESS}\nPhone: {COMPANY_PHONE}\nEmail: {COMPANY_EMAIL}")
        self.ln(10)

def generate_pdf(recipient, property_addr, invoice_no, due_date, items):
    pdf = PDF()
    pdf.add_page()
    
    # Invoice Header
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 10, "INVOICE", ln=True, align='R')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Invoice #: {invoice_no}", ln=True, align='R')
    pdf.cell(0, 10, f"Date: {date.today()}", ln=True, align='R')
    pdf.cell(0, 10, f"Due Date: {due_date}", ln=True, align='R')
    
    # Bill To
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "BILL TO:", ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 5, f"{recipient}\nProperty: {property_addr}")
    pdf.ln(10)
    
    # Table Header
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(140, 10, "Description", 1, 0, 'L', True)
    pdf.cell(50, 10, "Amount", 1, 1, 'C', True)
    
    # Table Content
    pdf.set_font('Arial', '', 12)
    total = 0
    for item in items:
        pdf.cell(140, 10, item['desc'], 1)
        pdf.cell(50, 10, f"${item['amount']:,.2f}", 1, 1, 'R')
        total += item['amount']
        
    # Total
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(140, 10, "TOTAL DUE", 1, 0, 'R')
    pdf.cell(50, 10, f"${total:,.2f}", 1, 1, 'R')
    
    return pdf.output(dest='S').encode('latin-1')

# --- USER INTERFACE ---
st.title("📄 Invoice Generator")
st.subheader(f"{COMPANY_NAME} Portal")

with st.form("invoice_form"):
    col1, col2 = st.columns(2)
    with col1:
        invoice_no = st.text_input("Invoice Number", value="INV-1001")
        tenant_name = st.text_input("Tenant Name")
    with col2:
        due_date = st.date_input("Due Date")
        property_addr = st.text_input("Property Address")

    st.write("---")
    st.write("### Charges")
    
    # Dynamic Item list using a Dataframe approach
    items_df = st.data_editor(
        pd.DataFrame([{"Description": "Monthly Rent", "Amount": 0.0}]),
        num_rows="dynamic",
        use_container_width=True
    )
    
    submitted = st.form_submit_button("Generate Invoice")

if submitted:
    # Process data
    charge_list = []
    for index, row in items_df.iterrows():
        charge_list.append({"desc": row["Description"], "amount": row["Amount"]})
        
    pdf_bytes = generate_pdf(tenant_name, property_addr, invoice_no, due_date, charge_list)
    
    st.success("Invoice Created Successfully!")
    st.download_button(
        label="Download PDF Invoice",
        data=pdf_bytes,
        file_name=f"Invoice_{invoice_no}.pdf",
        mime="application/pdf"
    )