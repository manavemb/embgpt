import streamlit as st
from streamlit_lottie import st_lottie
import requests
import time
from anthropic import Anthropic
import yaml
import markdown2
from io import BytesIO
from datetime import datetime, date
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from bs4 import BeautifulSoup
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.shared import OxmlElement, qn
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
import re
from typing import Optional
import base64

# Set up the Anthropic client
client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# Force light theme and set page config
st.set_page_config(page_title="EMB-AI BRD Generator", layout="wide", initial_sidebar_state="collapsed")

st.header("EMB-AI BRD Studio")

# Register Poppins fonts
pdfmetrics.registerFont(TTFont('Poppins', 'assets/Poppins-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Poppins-SemiBold', 'assets/Poppins-SemiBold.ttf'))

# Initialize session state for form fields
if 'form_fields' not in st.session_state:
    st.session_state.form_fields = {
        'client_name': '',
        'project_description': '',
        'user_types': '',
        'deliverables': '',
        'prepared_by': '',
        'document_date': date.today(),
        'version_number': 'v1'
    }

# Function to load and encode the local image
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Load the local watermark image
watermark_base64 = get_base64_of_bin_file('watermark.png')

# Load Lottie animations
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

lottie_writing = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_41X1Rp.json")
lottie_completed = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_j3yeurta.json")

def display_lottie_or_text(lottie_data, fallback_text, height=200):
    if lottie_data is not None:
        st_lottie(lottie_data, height=height)
    else:
        st.info(fallback_text)

# Load confidentiality agreement
def load_confidentiality_agreement():
    try:
        with open('confidentiality_agreement.yaml', 'r') as file:
            agreement = yaml.safe_load(file)
        return agreement.get('Confidentiality Agreement', {}).get('content', '')
    except:
        return "Confidentiality agreement not found or invalid."

confidentiality_agreement = load_confidentiality_agreement()

# Version number handling functions
def format_version_number(version_input):
    """Format the version number to ensure it starts with 'v'"""
    if not version_input:
        return 'v1'
    version = version_input.lower().strip().replace('v', '')
    return f'v{version}' if version else 'v1'

def validate_version_number(version_input):
    """Validate the version number format"""
    try:
        formatted_version = format_version_number(version_input)
        version_num = formatted_version[1:]
        if not version_num:
            return 'v1'
        float(version_num)
        return formatted_version
    except ValueError:
        return 'v1'

# Function to update session state
def update_form_field():
    for field in st.session_state.form_fields.keys():
        if field in st.session_state:
            st.session_state.form_fields[field] = st.session_state[field]

# Custom CSS
st.markdown("""
    <style>
    .stTextInput[data-baseweb="input"] {
        width: 100%;
    }
    .stTextInput input {
        font-family: "Source Sans Pro", sans-serif;
        border: 1px solid #ccc;
        border-radius: 4px;
    }
    .stTextInput input:focus {
        border-color: #11A64A;
        box-shadow: 0 0 0 1px #11A64A;
    }
    .stDateInput {
        width: 100%;
    }
    .stDateInput > div {
        width: 100%;
    }
    .company-info {
        text-align: center;
        margin-top: 20px;
    }
    .company-name {
        color: #11A64A;
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .contact-info {
        font-size: 10px;
        line-height: 1.4;
        color: #333;
    }
    </style>
""", unsafe_allow_html=True)

# Main content
st.markdown("""
This app generates a comprehensive Business Requirements Document (BRD) based on your inputs.
Fill in the fields below and click 'Generate BRD' to create your document.
""")

# Progress bar
total_fields = len(st.session_state.form_fields)
filled_fields = sum(1 for value in st.session_state.form_fields.values() if value)
progress = filled_fields / total_fields
st.progress(progress)
st.write(f"Form Completion: {filled_fields}/{total_fields} fields")

# Create first page content
def create_first_page_content(client_name, prepared_by, input_date, version_number):
    formatted_date = input_date.strftime("%B %d, %Y") if isinstance(input_date, (date, datetime)) else date.today().strftime("%B %d, %Y")
    formatted_version = validate_version_number(version_number)
    
    return f"""
# Business Requirements Document

## {client_name}

**Date:** {formatted_date}
**Prepared By:** {prepared_by}
**Document Version:** {formatted_version}

---

**CONFIDENTIAL**

This document contains confidential and proprietary information. It is shared under the terms of the confidentiality agreement included within this document. Unauthorized distribution or copying is prohibited.

---

**EMB-AI**

**Address:** Plot No. 17, Phase-4, Maruti Udyog, Sector 18, Gurugram, HR
**Phone:** +91-8882102246
**Email:** contact@exmyb.com
**Website:** www.emb.global
"""

# Document Information expander
with st.expander("Document Information", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        prepared_by = st.text_input(
            "Prepared By",
            placeholder="Enter name of preparer",
            value=st.session_state.form_fields['prepared_by'],
            key='prepared_by',
            help="Enter the name of the person preparing this document",
            on_change=update_form_field
        )

    with col2:
        selected_date = st.date_input(
            "Document Date",
            value=date.today(),
            min_value=date(2000, 1, 1),
            max_value=date(2100, 12, 31),
            key='document_date',
            help="Select the document date",
            on_change=update_form_field
        )
        st.session_state.form_fields['document_date'] = selected_date

    with col3:
        version_input = st.text_input(
            "Version Number",
            placeholder="Enter version (default: v1)",
            value=st.session_state.form_fields['version_number'],
            key='version_number',
            help="Enter version number (e.g., v1, v2, etc.)",
            on_change=update_form_field
        )

# Client and Project Information expander
with st.expander("Client and Project Information", expanded=True):
    client_name = st.text_input(
        "Client Name",
        placeholder="Enter the client's name",
        value=st.session_state.form_fields['client_name'],
        key='client_name',
        help="Enter the name of the client",
        on_change=update_form_field
    )
    
    project_description = st.text_area(
        "Project Description and Requirements",
        placeholder="Provide a detailed description of the project and list the main requirements.",
        height=200,
        value=st.session_state.form_fields['project_description'],
        key='project_description',
        help="Describe the project and its requirements in detail",
        on_change=update_form_field
    )

# Project Details expander
with st.expander("Project Details", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        user_types = st.text_area(
            "Types of Users",
            placeholder="List the different types of users who will interact with the system, one per line",
            height=150,
            value=st.session_state.form_fields['user_types'],
            key='user_types',
            help="Enter each user type on a new line (Admin will be automatically added)",
            on_change=update_form_field
        )
        st.caption("Note: Admin user type will be automatically added")
    
    with col2:
        deliverables = st.text_area(
            "Project Deliverables",
            placeholder="List the main deliverables or components of the project, one per line",
            height=150,
            value=st.session_state.form_fields['deliverables'],
            key='deliverables',
            help="Enter each deliverable on a new line (Admin Panel will be automatically added)",
            on_change=update_form_field
        )
        st.caption("Note: Admin Panel will be automatically added")

# Add some spacing after the inputs
st.markdown("<br>", unsafe_allow_html=True)

# Set fixed temperatures for each part
temp_part1 = 0.2
temp_part2 = 0.5
temp_part3 = 0.3
temp_part4 = 0.0

# Function to determine model
def get_model(part):
    return "claude-3-5-sonnet-20240620"

# Function to generate BRD part
@st.fragment
def generate_brd_part(prompt, placeholder, model, temperature):
    response = ""
    with client.messages.stream(
        model=model,
        max_tokens=8192,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            response += text
            placeholder.markdown(response)
    return response

# Prompt generation functions
def get_prompt_part1():
    return f"""
    Create the first part of a detailed Business Requirements Document (BRD) for the following project: (Numbering, heading, sub headings and paragraph should be properly formatted and don't write keyword like description or module while writing description, text sizes should be appropriate.)

    Client Name: {st.session_state.form_fields['client_name']}
    Project Description and Requirements:
    {st.session_state.form_fields['project_description']}
    Types of Users:
    {st.session_state.form_fields['user_types']}
    Project Deliverables:
    {st.session_state.form_fields['deliverables']}

    Include the following sections:
    1. Confidentiality Agreement: Use the following agreement:
    {confidentiality_agreement}

    2. Executive Summary: 
    - Provide a brief overview of the project, its objectives, key stakeholders & deliverables.

    3. Project Approach: 
    - Describe the methodology, timeline, and key milestones based on the deliverables of the project in a table.
    - Add a note mentioning that they are just for references only, final milestones will be provided in further discussions.

    Provide detailed and professional content for each section, incorporating all the provided information.
    Use Markdown formatting for proper structure.
    Do not include a title for the BRD itself, as it will be added separately.
    """
def get_prompt_part2(response_part1):
    return f"""
    Create the second part of a detailed Business Requirements Document (BRD) for the following project: (Numbering, heading, sub headings and paragraph should be properly formatted and don't write keyword like description or module while writing description, text sizes should be appropriate.)

    Client Name: {st.session_state.form_fields['client_name']}
    Project Description and Requirements:
    {st.session_state.form_fields['project_description']}
    Types of Users:
    {st.session_state.form_fields['user_types']}
    Project Deliverables:
    {st.session_state.form_fields['deliverables']}

    Previously generated content:
    {response_part1}

    Now, include the following sections:
    1. Functional Requirements:
    - For each deliverable, create at least 48 detailed modules as per requirement.
    - Structure each requirement as: Module, Sub - Module (Optional), Description.
    - Ensure the requirements are comprehensive and cover all aspects of the project.
    - Write description of each module in 3 or more lines respectively.
    - Descripton must be present against each module.
    - For each user-side module, include a corresponding management module in the admin panel.
    - Don't use any keywords like Module & Description in output.

    2. 3rd Party Integrations and API Suggestions:
    - Based on the functional requirements, suggest potential 3rd party integrations or APIs that could be used.
    - For each suggestion, provide:
      a. Name of the 3rd party service or API
      b. Brief description of its functionality or requirement it can address
      c. Try to suggest API or services specifically for Indian region & Mention their international alternatives too.

    Provide detailed and professional content, incorporating all the provided information.
    Use Markdown formatting for proper structure.
    """

def get_prompt_part3(response_part1, response_part2):
    return f"""
    Create the third part of a detailed Business Requirements Document (BRD) for the following project: (Numbering, heading, sub headings and paragraph should be properly formatted and don't write keyword like description or module while writing description, text sizes should be appropriate.)

    Client Name: {st.session_state.form_fields['client_name']}
    Project Description and Requirements:
    {st.session_state.form_fields['project_description']}
    Types of Users:
    {st.session_state.form_fields['user_types']}
    Project Deliverables:
    {st.session_state.form_fields['deliverables']}

    Previously generated content:
    {response_part1}
    {response_part2}

    Now, include the following sections:
    1. Continue the functional requirements if it's absolute necessary or continue to non functional requirements.

    2. Non-Functional Requirements: 
    Specify performance, security, scalability, and other non-functional aspects of the system.
    Include:
    - Performance Requirements
    - Security Requirements
    - Scalability and Availability
    - Usability Requirements
    - Browser Compatibility
    - Mobile Responsiveness
    - Data Backup and Recovery
    - Monitoring and Logging
    - Compliance Requirements
    - Integration Standards

    Provide detailed and professional content for each section, incorporating all the provided information.
    Use Markdown formatting for proper structure, including tables where specified.
    """

def get_prompt_part4(response_part1, response_part2, response_part3):
    return f"""
    Create the fourth part of a detailed Business Requirements Document (BRD) for the following project: (Numbering, heading, sub headings and paragraph should be properly formatted and don't write keyword like description or module while writing description, text sizes should be appropriate.)

    Client Name: {st.session_state.form_fields['client_name']}
    Project Description and Requirements:
    {st.session_state.form_fields['project_description']}
    Types of Users:
    {st.session_state.form_fields['user_types']}
    Project Deliverables:
    {st.session_state.form_fields['deliverables']}

    Previously generated content:
    {response_part1}
    {response_part2}
    {response_part3}

    Now, include the following section:
    Annexure: 
    a. Functional Requirements: Create a separate table for each deliverable in the Functional Requirements. Each table should have the following columns:
    - Requirement ID (Format: REQ-[Deliverable Initial]-[Number], e.g., REQ-UP-001 for User Panel requirement 1)
    - Module/Feature
    - Description (Detailed 3-4 line description)

    b. 3rd Party Services and APIs: Create a table summarizing all suggested 3rd party services and APIs. This table should have the following columns:
    - Service/API Name
    - Functional Area
    - Description
    - Region (Indian/International)

    Ensure all tables are properly formatted in Markdown and contain comprehensive information from the previous sections.
    Each requirement should have a unique ID and detailed description.
    """

def convert_markdown_to_pdf(markdown_content):
    # First, explicitly process markdown headers
    def process_markdown_headers(content):
        # Replace markdown headers with HTML headers
        content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        content = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)
        return content

    # Process headers before converting to HTML
    processed_content = process_markdown_headers(markdown_content)
    content_html = markdown2.markdown(processed_content, extras=["tables", "fenced-code-blocks"])
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                          topMargin=2.5 * cm, bottomMargin=1.5 * cm, 
                          leftMargin=2 * cm, rightMargin=2 * cm)

    # Define styles
    custom_styles = {
        'CoverTitle': ParagraphStyle(
            name='CoverTitle',
            fontName='Poppins-SemiBold',
            fontSize=28,
            leading=34,
            alignment=TA_CENTER,
            spaceAfter=30
        ),
        'CoverSubTitle': ParagraphStyle(
            name='CoverSubTitle',
            fontName='Poppins-SemiBold',
            fontSize=24,
            leading=28,
            alignment=TA_CENTER,
            spaceAfter=40
        ),
        'CoverInfo': ParagraphStyle(
            name='CoverInfo',
            fontName='Poppins',
            fontSize=12,
            leading=16,
            alignment=TA_CENTER,
            spaceAfter=12
        ),
        'CustomHeading1': ParagraphStyle(
            name='CustomHeading1',
            fontName='Poppins-SemiBold',
            fontSize=18,
            leading=22,
            spaceBefore=16,
            spaceAfter=10,
            textColor=colors.HexColor('#000000')
        ),
        'CustomHeading2': ParagraphStyle(
            name='CustomHeading2',
            fontName='Poppins-SemiBold',
            fontSize=16,
            leading=20,
            spaceBefore=14,
            spaceAfter=8,
            textColor=colors.HexColor('#000000')
        ),
        'CustomHeading3': ParagraphStyle(
            name='CustomHeading3',
            fontName='Poppins-SemiBold',
            fontSize=14,
            leading=18,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.HexColor('#000000')
        ),
        'CustomHeading4': ParagraphStyle(
            name='CustomHeading4',
            fontName='Poppins-SemiBold',
            fontSize=12,
            leading=16,
            spaceBefore=10,
            spaceAfter=6,
            textColor=colors.HexColor('#000000')
        ),
        'CustomBodyText': ParagraphStyle(
            name='CustomBodyText',
            fontName='Poppins',
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=8
        ),
        'ContactInfo': ParagraphStyle(
            name='ContactInfo',
            fontName='Poppins',
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            spaceAfter=4
        ),
        'CompanyName': ParagraphStyle(
            name='CompanyName',
            fontName='Poppins-SemiBold',
            fontSize=14,
            leading=16,
            alignment=TA_CENTER,
            spaceAfter=8,
            textColor=colors.HexColor('#11A64A')
        )
    }

    flowables = []

    # Add logo to cover page
    try:
        im = Image('watermark.png', width=6*cm, height=3.8*cm)
        im.hAlign = 'CENTER'
        flowables.append(Spacer(1, 20))
        flowables.append(im)
        flowables.append(Spacer(1, 20))
    except Exception as e:
        print(f"Error adding logo: {str(e)}")

    # Add document title
    flowables.append(Paragraph("Business Requirements Document", custom_styles['CoverTitle']))
    flowables.append(Spacer(1, 40))

    # Add client name
    flowables.append(Paragraph(st.session_state.form_fields['client_name'], custom_styles['CoverSubTitle']))
    flowables.append(Spacer(1, 40))

    # Add document info
    version = validate_version_number(st.session_state.form_fields['version_number'])
    formatted_date = st.session_state.form_fields['document_date'].strftime("%B %d, %Y")
    prepared_by = st.session_state.form_fields['prepared_by']

    flowables.append(Paragraph(f"Version: {version}", custom_styles['CoverInfo']))
    flowables.append(Paragraph(f"Date: {formatted_date}", custom_styles['CoverInfo']))
    flowables.append(Paragraph(f"Prepared By: {prepared_by}", custom_styles['CoverInfo']))
    flowables.append(Spacer(1, 40))

    # Add company info
    flowables.append(Paragraph("EMB-AI", custom_styles['CompanyName']))
    
    company_info = [
        "Plot No. 17, Phase-4, Maruti Udyog, Sector 18, Gurugram, HR",
        "Phone: +91-8882102246",
        "Email: contact@exmyb.com",
        "Website: www.emb.global"
    ]
    
    for info in company_info:
        flowables.append(Paragraph(info, custom_styles['ContactInfo']))

    # Add page break after cover
    flowables.append(PageBreak())

    # Function to convert HTML table to ReportLab Table
    def html_table_to_reportlab(html_table):
        soup = BeautifulSoup(html_table, 'html.parser')
        data = []
        for row in soup.find_all('tr'):
            row_data = []
            for cell in row.find_all(['td', 'th']):
                cell_content = cell.get_text(separator='\n', strip=True)
                row_data.append(Paragraph(cell_content, custom_styles['CustomBodyText']))
            if row_data:
                data.append(row_data)
        
        if not data:
            return None

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#11A64A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Poppins-SemiBold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Poppins'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        return table

    # Process main content
    soup = BeautifulSoup(content_html, 'html.parser')
    
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'pre', 'table', 'ul', 'ol']):
        try:
            if element.name == 'h1':
                flowables.append(Spacer(1, 20))
                flowables.append(Paragraph(element.text.strip(), custom_styles['CustomHeading1']))
            elif element.name == 'h2':
                flowables.append(Spacer(1, 16))
                flowables.append(Paragraph(element.text.strip(), custom_styles['CustomHeading2']))
            elif element.name == 'h3':
                flowables.append(Spacer(1, 14))
                flowables.append(Paragraph(element.text.strip(), custom_styles['CustomHeading3']))
            elif element.name == 'h4':
                flowables.append(Spacer(1, 12))
                flowables.append(Paragraph(element.text.strip(), custom_styles['CustomHeading4']))
            elif element.name == 'p':
                text = element.text.strip()
                # Check if this paragraph looks like a heading (numbered or bulleted)
                if re.match(r'^\d+\.\s+', text) or re.match(r'^[•\-\*]\s+', text):
                    flowables.append(Spacer(1, 10))
                    flowables.append(Paragraph(text, custom_styles['CustomHeading4']))
                else:
                    flowables.append(Paragraph(text, custom_styles['CustomBodyText']))
            elif element.name == 'pre':
                code_lines = element.text.split('\n')
                for line in code_lines:
                    flowables.append(Paragraph(line, custom_styles['CustomBodyText']))
            elif element.name == 'table':
                table = html_table_to_reportlab(str(element))
                if table:
                    flowables.append(table)
            elif element.name in ['ul', 'ol']:
                for li in element.find_all('li'):
                    bullet = '•' if element.name == 'ul' else f"{li.find_previous_siblings('li').__len__() + 1}."
                    text = f"{bullet} {li.text}"
                    flowables.append(Paragraph(text, custom_styles['CustomBodyText']))

            # Add some space after each element
            flowables.append(Spacer(1, 6))

        except Exception as e:
            print(f"Error processing element: {element}. Error: {str(e)}")
            flowables.append(Paragraph(str(element), custom_styles['CustomBodyText']))

    # Function to add watermark, page number, and border
    def add_watermark_and_page_number(canvas, doc):
        canvas.saveState()
        
        if canvas.getPageNumber() == 1:
            # Draw green border on first page
            canvas.setStrokeColor(colors.HexColor('#11A64A'))
            canvas.setLineWidth(2)
            margin = 30
            canvas.rect(
                margin,
                margin,
                doc.pagesize[0] - 2*margin,
                doc.pagesize[1] - 2*margin,
                stroke=1,
                fill=0
            )
        elif canvas.getPageNumber() > 1:
            # Add page number and watermark for other pages
            canvas.setFont('Poppins', 9)
            page_num = canvas.getPageNumber() - 1
            text = f"Page {page_num}"
            canvas.drawRightString(doc.width + doc.rightMargin, doc.bottomMargin, text)
            
            watermark = ImageReader('watermark.png')
            canvas.drawImage(watermark, 
                           doc.width + doc.rightMargin - 2*cm, 
                           doc.height + doc.topMargin - 1*cm, 
                           width=2*cm, height=2*cm, 
                           mask='auto', 
                           preserveAspectRatio=True)
        
        canvas.restoreState()

    # Build the PDF
    doc.build(flowables, onFirstPage=add_watermark_and_page_number, onLaterPages=add_watermark_and_page_number)
    buffer.seek(0)
    return buffer

def convert_markdown_to_docx(markdown_content):
    doc = Document()
    
    # Set up styles
    styles = doc.styles

    # Modify the Normal style
    style_normal = styles['Normal']
    style_normal.font.name = 'Poppins'
    style_normal.font.size = Pt(10)
    style_normal.paragraph_format.space_after = Pt(8)

    # Create custom styles
    def create_style(name, font_name, font_size, bold=False, italic=False, color=RGBColor(0, 0, 0), alignment=None):
        style = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        font = style.font
        font.name = font_name
        font.size = Pt(font_size)
        font.bold = bold
        font.italic = italic
        font.color.rgb = color
        if alignment:
            style.paragraph_format.alignment = alignment
        return style

    # Define document styles
    style_cover_title = create_style('CoverTitle', 'Poppins', 28, bold=True, 
                                   alignment=WD_ALIGN_PARAGRAPH.CENTER)
    style_cover_subtitle = create_style('CoverSubTitle', 'Poppins', 24, bold=True, 
                                      alignment=WD_ALIGN_PARAGRAPH.CENTER)
    style_cover_info = create_style('CoverInfo', 'Poppins', 12, 
                                  alignment=WD_ALIGN_PARAGRAPH.CENTER)
    style_company_name = create_style('CompanyName', 'Poppins', 14, bold=True,
                                    color=RGBColor(17, 166, 74), 
                                    alignment=WD_ALIGN_PARAGRAPH.CENTER)
    style_contact_info = create_style('ContactInfo', 'Poppins', 10, 
                                    alignment=WD_ALIGN_PARAGRAPH.CENTER)
    style_heading1 = create_style('CustomHeading1', 'Poppins', 16, bold=True)
    style_heading2 = create_style('CustomHeading2', 'Poppins', 14, bold=True)
    style_heading3 = create_style('CustomHeading3', 'Poppins', 12, bold=True)

    # Set up page margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(1.5)
        section.left_margin = Cm(2)
        section.right_margin = Cm(2)

    # Add border to first section only
    section = doc.sections[0]
    sect_pr = section._sectPr
    
    # Create border element
    border = OxmlElement('w:pgBorders')
    border.set(qn('w:offsetFrom'), 'page')
    
    for edge in ['top', 'left', 'bottom', 'right']:
        edge_element = OxmlElement(f'w:{edge}')
        edge_element.set(qn('w:val'), 'single')
        edge_element.set(qn('w:sz'), '24')  # 3 points
        edge_element.set(qn('w:space'), '0')
        edge_element.set(qn('w:color'), '11A64A')  # EMB green
        border.append(edge_element)
    
    sect_pr.append(border)

    # Add logo to center of cover page
    title_paragraph = doc.add_paragraph()
    title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_paragraph.add_run()
    run.add_picture("watermark.png", width=Cm(8))  # Logo size 8cm width
    
    # Add spacing after logo
    doc.add_paragraph()

    # Add document title
    title = doc.add_paragraph("Business Requirements Document", style=style_cover_title)
    doc.add_paragraph()

    # Add client name
    client = doc.add_paragraph(st.session_state.form_fields['client_name'], style=style_cover_subtitle)
    doc.add_paragraph()

    # Add document info
    version = validate_version_number(st.session_state.form_fields['version_number'])
    formatted_date = st.session_state.form_fields['document_date'].strftime("%B %d, %Y")
    prepared_by = st.session_state.form_fields['prepared_by']

    info_items = [
        f"Version: {version}",
        f"Date: {formatted_date}",
        f"Prepared By: {prepared_by}"
    ]

    for item in info_items:
        p = doc.add_paragraph(item, style=style_cover_info)
    
    doc.add_paragraph()

    # Add company info
    company = doc.add_paragraph("EMB-AI", style=style_company_name)
    
    company_info = [
        "Plot No. 17, Phase-4, Maruti Udyog, Sector 18, Gurugram, HR",
        "Phone: +91-8882102246",
        "Email: contact@exmyb.com",
        "Website: www.emb.global"
    ]
    
    for info in company_info:
        p = doc.add_paragraph(info, style=style_contact_info)

    # Add page break after cover page
    doc.add_page_break()

    # Add watermark to header (for all pages except cover)
    def add_header_with_watermark(section):
        header = section.header
        paragraph = header.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = paragraph.add_run()
        run.add_picture("watermark.png", width=Cm(2))
        return header

    # Add page numbers to footer (for all pages)
    def add_footer_with_page_number(section):
        footer = section.footer
        paragraph = footer.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = paragraph.add_run()
        
        fldChar1 = OxmlElement('w:fldChar')
        fldChar1.set(qn('w:fldCharType'), 'begin')
        instrText = OxmlElement('w:instrText')
        instrText.set(qn('xml:space'), 'preserve')
        instrText.text = 'PAGE'
        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(qn('w:fldCharType'), 'end')

        run._element.append(fldChar1)
        run._element.append(instrText)
        run._element.append(fldChar2)
        
        return footer

    # Add headers and footers to all sections except first
    for i, section in enumerate(doc.sections):
        if i > 0:  # Skip first section (cover page)
            add_header_with_watermark(section)
            add_footer_with_page_number(section)
                # Convert markdown to HTML and process content
    html_content = markdown2.markdown(markdown_content, extras=["tables", "fenced-code-blocks"])
    soup = BeautifulSoup(html_content, 'html.parser')

    # Process main content
    for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'pre', 'table', 'ul', 'ol']):
        try:
            if element.name == 'h1':
                doc.add_paragraph(element.text, style=style_heading1)
            elif element.name == 'h2':
                doc.add_paragraph(element.text, style=style_heading2)
            elif element.name == 'h3':
                doc.add_paragraph(element.text, style=style_heading3)
            elif element.name == 'p':
                doc.add_paragraph(element.text, style=style_normal)
            elif element.name == 'pre':
                for line in element.text.split('\n'):
                    p = doc.add_paragraph(line, style=style_normal)
                    p.paragraph_format.left_indent = Inches(0.5)
            elif element.name == 'table':
                # Create and style table
                table_data = []
                for row in element.find_all('tr'):
                    row_data = [cell.text.strip() for cell in row.find_all(['th', 'td'])]
                    table_data.append(row_data)
                
                if table_data:
                    num_rows = len(table_data)
                    num_cols = len(table_data[0])
                    table = doc.add_table(rows=num_rows, cols=num_cols)
                    table.style = 'Table Grid'
                    
                    for i, row in enumerate(table_data):
                        for j, cell in enumerate(row):
                            table.cell(i, j).text = cell
                            paragraph = table.cell(i, j).paragraphs[0]
                            
                            if i == 0:  # Header row
                                run = paragraph.runs[0]
                                run.font.bold = True
                                run.font.name = 'Poppins'
                                run.font.size = Pt(10)
                                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                                
                                # Apply EMB green background
                                shading_elm = parse_xml(r'<w:shd {} w:fill="11A64A"/>'.format(nsdecls('w')))
                                table.cell(i, j)._element.get_or_add_tcPr().append(shading_elm)
                                run.font.color.rgb = RGBColor(255, 255, 255)
                            else:
                                run = paragraph.runs[0]
                                run.font.name = 'Poppins'
                                run.font.size = Pt(9)
                    
                    doc.add_paragraph()  # Add space after table
            elif element.name in ['ul', 'ol']:
                for li in element.find_all('li'):
                    paragraph = doc.add_paragraph(li.text, style=style_normal)
                    paragraph.style = 'List Bullet' if element.name == 'ul' else 'List Number'

        except Exception as e:
            print(f"Error processing element: {element}. Error: {str(e)}")
            doc.add_paragraph(str(element), style=style_normal)

    # Save to BytesIO
    docx_buffer = BytesIO()
    doc.save(docx_buffer)
    docx_buffer.seek(0)
    return docx_buffer

@st.fragment
def markdown_download(content: str, client_name: str, version: str):
    """Fragment for Markdown download"""
    st.download_button(
        label="📄 Download as Markdown",
        data=content,
        file_name=f"BRD_{client_name}_{version}.md",
        mime="text/markdown",
        help="Download the BRD in Markdown format"
    )

@st.fragment
def pdf_download(content: str, client_name: str, version: str):
    """Fragment for PDF download"""
    pdf_buffer = convert_markdown_to_pdf(content)
    st.download_button(
        label="📑 Download as PDF",
        data=pdf_buffer,
        file_name=f"BRD_{client_name}_{version}.pdf",
        mime="application/pdf",
        help="Download the BRD in PDF format"
    )

@st.fragment
def docx_download(content: str, client_name: str, version: str):
    """Fragment for DOCX download"""
    docx_buffer = convert_markdown_to_docx(content)
    st.download_button(
        label="📝 Download as DOCX",
        data=docx_buffer,
        file_name=f"BRD_{client_name}_{version}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        help="Download the BRD in DOCX format"
    )

# Generate BRD button
if st.button("Generate BRD", key="generate_brd"):
    # Validate all required fields
    validation_errors = []
    required_fields = {
        'client_name': 'Client Name',
        'project_description': 'Project Description',
        'user_types': 'Types of Users',
        'deliverables': 'Project Deliverables',
        'prepared_by': 'Prepared By'
    }
    
    for field, field_name in required_fields.items():
        if not st.session_state.form_fields[field]:
            validation_errors.append(f"{field_name} is required")
    
    if validation_errors:
        st.error("\n".join(validation_errors))
    else:
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Process user types (ensure Admin is included)
            user_types_list = st.session_state.form_fields['user_types'].split('\n')
            user_types_list = [ut.strip() for ut in user_types_list if ut.strip()]
            if 'Admin' not in user_types_list:
                user_types_list.append('Admin')
            user_types_str = '\n'.join(user_types_list)

            # Process deliverables (ensure Admin Panel is included)
            deliverables_list = st.session_state.form_fields['deliverables'].split('\n')
            deliverables_list = [d.strip() for d in deliverables_list if d.strip()]
            if 'Admin Panel' not in deliverables_list:
                deliverables_list.append('Admin Panel')
            deliverables_str = '\n'.join(deliverables_list)

            # Create containers for each part
            part1_container = st.container()
            part2_container = st.container()
            part3_container = st.container()
            part4_container = st.container()

            # Display Lottie animation
            with st.spinner("Generating your BRD..."):
                display_lottie_or_text(lottie_writing, "Generating BRD...", height=200)

            # Generate Part 1
            with st.spinner('Generating Part 1: Executive Summary and Project Approach...'):
                with part1_container:
                    model = get_model(1)
                    response_part1 = generate_brd_part(get_prompt_part1(), st.empty(), model, temp_part1)
            
            progress_bar.progress(0.25)
            status_text.text("Part 1 completed. Generating Part 2...")

            # Generate Part 2
            with st.spinner('Generating Part 2: Functional Requirements and Integrations...'):
                with part2_container:
                    model = get_model(2)
                    response_part2 = generate_brd_part(get_prompt_part2(response_part1), st.empty(), model, temp_part2)

            progress_bar.progress(0.5)
            status_text.text("Part 2 completed. Generating Part 3...")

            # Generate Part 3
            with st.spinner('Generating Part 3: Non-Functional Requirements...'):
                with part3_container:
                    model = get_model(3)
                    response_part3 = generate_brd_part(
                        get_prompt_part3(response_part1, response_part2),
                        st.empty(),
                        model,
                        temp_part3
                    )

            progress_bar.progress(0.75)
            status_text.text("Part 3 completed. Generating Part 4...")

            # Generate Part 4
            with st.spinner('Generating Part 4: Annexure and Tables...'):
                with part4_container:
                    model = get_model(4)
                    response_part4 = generate_brd_part(
                        get_prompt_part4(response_part1, response_part2, response_part3),
                        st.empty(),
                        model,
                        temp_part4
                    )

            progress_bar.progress(1.0)
            status_text.text("BRD Generation Completed!")

            # Combine all parts into final document
            full_brd = f"""

{response_part1}

{response_part2}

{response_part3}

{response_part4}
"""

            # Success message and completion animation
            st.success("BRD Generated Successfully!")
            display_lottie_or_text(lottie_completed, "BRD Generation Completed!", height=200)

            # Download options
            st.markdown("### Download Options")
            st.markdown("Choose your preferred format to download the BRD:")
            
            client_name = st.session_state.form_fields['client_name']
            version = st.session_state.form_fields['version_number']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                markdown_download(full_brd, client_name, version)
            
            with col2:
                pdf_download(full_brd, client_name, version)
            
            with col3:
                docx_download(full_brd, client_name, version)

            # Footer
            st.markdown("---")
            st.markdown("""
            <div style='text-align: center;'>
                <p>© 2024 EMB-AI. All rights reserved.</p>
                <p style='font-size: 0.8em;'>Plot No. 17, Phase-4, Maruti Udyog, Sector 18, Gurugram, HR</p>
                <p style='font-size: 0.8em;'>Phone: +91-8882102246 | Email: contact@exmyb.com | Website: www.emb.global</p>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"An error occurred during BRD generation: {str(e)}")
            st.error("Please try again or contact support if the issue persists.")

if __name__ == "__main__":
    pass
