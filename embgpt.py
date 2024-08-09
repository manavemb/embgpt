import streamlit as st
from streamlit_lottie import st_lottie
import requests
from anthropic import Anthropic
import yaml
import markdown2
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from streamlit.components.v1 import html
import base64

# Set up the Anthropic client
client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# Force light theme and set page config
st.set_page_config(page_title="EMB-AI BRD Generator", layout="wide", initial_sidebar_state="collapsed")

# Function to load and encode the local image
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Load the local logo image
logo_base64 = get_base64_of_bin_file('logo.png')

# Custom CSS for improved styling and dark mode support
st.markdown(f"""
    <style>
    .main .block-container {{padding-top: 1rem; padding-bottom: 0rem;}}
    .stTitle {{font-size: 2.5rem;}}
    .stSubheader {{font-size: 1.3rem;}}
    .stButton>button {{background-color: #0066cc; color: white;}}
    .stTextInput>div>div>input {{background-color: var(--input-bg);}}
    .stTextArea>div>div>textarea {{background-color: var(--input-bg);}}
    .header-container {{
        display: flex;
        align-items: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }}
    .logo-img {{
        width: 80px;
        height: 80px;
        margin-right: 1rem;
        background-image: url("data:image/png;base64,{logo_base64}");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
    }}
    .header-text {{
        flex-grow: 1;
    }}
    .header-text h1 {{
        margin: 0;
        font-size: 2.5rem;
        color: var(--text-color);
    }}
    .header-text h3 {{
        margin: 0;
        font-size: 1.3rem;
        color: var(--text-color);
    }}
    .sidebar-content {{padding: 1rem;}}
    .stExpander {{border: 1px solid var(--border-color); border-radius: 0.5rem; margin-bottom: 1rem;}}
    
    /* Dark mode adjustments */
    @media (prefers-color-scheme: dark) {{
        :root {{
            --text-color: #ffffff;
            --background-color: #0e1117;
            --input-bg: #262730;
            --border-color: #4d4d4d;
        }}
        body {{
            color: var(--text-color);
            background-color: var(--background-color);
        }}
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
            color: var(--text-color);
        }}
    }}
    
    /* Light mode */
    @media (prefers-color-scheme: light) {{
        :root {{
            --text-color: #000000;
            --background-color: #ffffff;
            --input-bg: #f0f2f6;
            --border-color: #e6e6e6;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

# Header with logo
st.markdown("""
    <div class="header-container">
        <div class="logo-img"></div>
        <div class="header-text">
            <h1>EMB-AI BRD Generator</h1>
            <h3>Your Business Analyst in Your Pocket</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
        
        if isinstance(agreement, dict):
            if 'Confidentiality Agreement' in agreement:
                agreement = agreement['Confidentiality Agreement']
            if 'content' in agreement:
                return agreement['content']
            elif 'title' in agreement and 'content' in agreement:
                return f"# {agreement['title']}\n\n{agreement['content']}"
        
        if isinstance(agreement, str):
            return agreement
        
        return "Confidentiality agreement structure is not recognized. Please check the YAML file."
    except FileNotFoundError:
        return "Confidentiality agreement file not found. Please ensure 'confidentiality_agreement.yaml' is in the same directory as the app."
    except yaml.YAMLError as e:
        return f"Error parsing confidentiality agreement YAML: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred while loading the confidentiality agreement: {str(e)}"

confidentiality_agreement = load_confidentiality_agreement()

# Sidebar for user onboarding
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.header("User Onboarding")
    st.info("Welcome! Please provide your information below.")
    
    user_name = st.text_input("Your Name", placeholder="John Doe")
    user_designation = st.selectbox(
        "Your Designation",
        ["", "Sales", "Business Analyst", "Project Manager"],
        index=0
    )
    
    if user_name or user_designation:
        welcome_message = f"Welcome, {user_name}"
        if user_designation:
            welcome_message += f" - {user_designation}"
        st.success(welcome_message)
    st.markdown('</div>', unsafe_allow_html=True)

# Main content
st.markdown("""
This app generates a comprehensive Business Requirements Document (BRD) based on your inputs.
Fill in the fields below and click 'Generate BRD' to create your document.
""")

# Initialize session state for form fields
if 'form_fields' not in st.session_state:
    st.session_state.form_fields = {
        'client_name': '',
        'project_description': '',
        'user_types': '',
        'deliverables': ''
    }

# Function to update session state
def update_form_field():
    for field in st.session_state.form_fields.keys():
        if field in st.session_state:
            st.session_state.form_fields[field] = st.session_state[field]

# Progress bar
total_fields = len(st.session_state.form_fields)
filled_fields = sum(1 for value in st.session_state.form_fields.values() if value)
progress = filled_fields / total_fields
st.progress(progress)
st.write(f"Form Completion: {filled_fields}/{total_fields} fields")

# Input fields
with st.expander("Client and Project Information", expanded=True):
    client_name = st.text_input("Client Name", placeholder="e.g., Acme Corporation", 
                                value=st.session_state.form_fields['client_name'], 
                                key='client_name', on_change=update_form_field)
    project_description = st.text_area("Project Description and Requirements", 
                                       placeholder="Describe the project and list the main requirements. You can use bullet points or numbered lists.",
                                       height=200, 
                                       value=st.session_state.form_fields['project_description'], 
                                       key='project_description', on_change=update_form_field)

with st.expander("Project Details", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        user_types = st.text_area("Types of Users", placeholder="List the types of users, one per line", 
                                  height=150, 
                                  value=st.session_state.form_fields['user_types'], 
                                  key='user_types', on_change=update_form_field)
    with col2:
        deliverables = st.text_area("Project Deliverables", placeholder="List the main deliverables, one per line", 
                                    height=150, 
                                    value=st.session_state.form_fields['deliverables'], 
                                    key='deliverables', on_change=update_form_field)

# Function to convert Markdown to PDF
def convert_markdown_to_pdf(markdown_content):
    html_content = markdown2.markdown(markdown_content, extras=["tables", "fenced-code-blocks"])
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    custom_styles = {
        'Title': ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontSize=18,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ),
        'Heading1': ParagraphStyle(
            'Heading1',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=10
        ),
        'Heading2': ParagraphStyle(
            'Heading2',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=12,
            spaceAfter=6
        ),
        'Heading3': ParagraphStyle(
            'Heading3',
            parent=styles['Heading3'],
            fontSize=12,
            spaceBefore=10,
            spaceAfter=4
        ),
        'BodyText': ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            alignment=TA_JUSTIFY
        )
    }
    
    flowables = []
    
    for element in html_content.split('\n'):
        if element.strip():
            if element.startswith('<h1>'):
                flowables.append(Paragraph(element[4:-5], custom_styles['Title']))
            elif element.startswith('<h2>'):
                flowables.append(Paragraph(element[4:-5], custom_styles['Heading1']))
            elif element.startswith('<h3>'):
                flowables.append(Paragraph(element[4:-5], custom_styles['Heading2']))
            elif element.startswith('<h4>'):
                flowables.append(Paragraph(element[4:-5], custom_styles['Heading3']))
            elif element.startswith('<p><strong>'):
                text = element[11:-13]
                flowables.append(Paragraph(f"<b>{text}</b>", custom_styles['BodyText']))
            else:
                flowables.append(Paragraph(element, custom_styles['BodyText']))
            
        flowables.append(Spacer(1, 6))
    
    # Function to add watermark with 35% opacity
    def add_watermark(canvas, doc):
        logo_path = "logo.png"  # Path to the logo file
        width, height = letter

        # Add watermark with 35% opacity
        logo = ImageReader(logo_path)
        canvas.saveState()
        canvas.setFillColorRGB(0.9, 0.9, 0.9, alpha=0.35)  # Light gray color with 35% opacity
        canvas.drawImage(logo, width / 2 - 150, height / 2 - 150, width=300, height=300, mask='auto', preserveAspectRatio=True)
        canvas.restoreState()

    # Build the PDF with the watermark on each page
    doc.build(flowables, onFirstPage=add_watermark, onLaterPages=add_watermark)
    
    buffer.seek(0)
    return buffer

# Function to generate BRD part
def generate_brd_part(prompt, placeholder):
    response = ""
    with client.messages.stream(
        model="claude-3-opus-20240229",
        max_tokens=4096,
        temperature=1,
        messages=[
                       {"role": "user", "content": prompt}
        ]
    ) as stream:
        for text in stream.text_stream:
            response += text
            placeholder.markdown(response)
    return response

# Generate BRD button
if st.button("Generate BRD", key="generate_brd"):
    if all(st.session_state.form_fields.values()):
        progress_bar = st.progress(0)
        status_text = st.empty()

        user_types_list = st.session_state.form_fields['user_types'].split('\n')
        if 'Admin' not in user_types_list:
            user_types_list.append('Admin')
        user_types_str = '\n'.join(user_types_list)

        deliverables_list = st.session_state.form_fields['deliverables'].split('\n')
        if 'Admin Panel' not in deliverables_list:
            deliverables_list.append('Admin Panel')
        deliverables_str = '\n'.join(deliverables_list)

        part1_container = st.container()
        part2_container = st.container()
        part3_container = st.container()

        # Display Lottie animation or fallback text while generating BRD
        with st.spinner("Generating your BRD..."):
            display_lottie_or_text(lottie_writing, "Generating BRD...", height=200)

        # Part 1: Confidentiality Agreement, Executive Summary, and Project Approach
        prompt_part1 = f"""
        Create the first part of a detailed Business Requirements Document (BRD) for the following project:

        Client Name: {st.session_state.form_fields['client_name']}
        Project Description and Requirements:
        {st.session_state.form_fields['project_description']}
        Types of Users:
        {user_types_str}
        Project Deliverables:
        {deliverables_str}

        Include the following sections:
        1. Confidentiality Agreement: Use the following agreement:
        {confidentiality_agreement}

        2. Executive Summary: 
        - Provide a brief overview of the project, its objectives, and key stakeholders.
        - Include a detailed list of project deliverables, explaining each one concisely.

        3. Project Approach: 
        Outline the methodology, timeline, and key milestones for the project.

        Provide detailed and professional content for each section, incorporating all the provided information.
        Use Markdown formatting for proper structure.
        """

        with st.spinner('Generating Part 1: Confidentiality Agreement, Executive Summary, and Project Approach...'):
            with part1_container:
                response_part1 = generate_brd_part(prompt_part1, st.empty())
        
        progress_bar.progress(33)
        status_text.text("Part 1 completed. Generating Part 2...")

        # Part 2: Functional Requirements and 3rd Party Integrations
        prompt_part2 = f"""
        Create the second part of a detailed Business Requirements Document (BRD) for the following project:

        Client Name: {st.session_state.form_fields['client_name']}
        Project Description and Requirements:
        {st.session_state.form_fields['project_description']}
        Types of Users:
        {user_types_str}
        Project Deliverables:
        {deliverables_str}

        Previously generated content:
        {response_part1}

        Now, include the following sections:

        1. Functional Requirements:
        - For each deliverable, create detailed modules.
        - Structure each requirement as: Deliverable, Module, Detailed Description of Module.
        - Ensure the requirements are comprehensive and cover all aspects of the project.
        - For each user-side module, include a corresponding management module in the admin panel.

        2. 3rd Party Integrations and API Suggestions:
        - Based on the functional requirements, suggest potential 3rd party integrations or APIs that could be used to implement or enhance various features of the system.
        - For each suggestion, provide:
          a. Name of the 3rd party service or API
          b. Brief description of its functionality
          c. Specific features or requirements it could address
          d. Potential benefits of using this integration

        Provide detailed and professional content, incorporating all the provided information and ensuring consistency with the previously generated sections.
        Use Markdown formatting for proper structure.
        """

        with st.spinner('Generating Part 2: Functional Requirements and 3rd Party Integrations...'):
            with part2_container:
                response_part2 = generate_brd_part(prompt_part2, st.empty())
        
        progress_bar.progress(66)
        status_text.text("Part 2 completed. Generating Part 3...")

        # Part 3: User Journey, User Stories, Non-Functional Requirements, and Annexure
        prompt_part3 = f"""
        Create the third part of a detailed Business Requirements Document (BRD) for the following project:

        Client Name: {st.session_state.form_fields['client_name']}
        Project Description and Requirements:
        {st.session_state.form_fields['project_description']}
        Types of Users:
        {user_types_str}
        Project Deliverables:
        {deliverables_str}

        Previously generated content:
        {response_part1}
        {response_part2}

        Now, include the following sections:

        1. User Journey and User Stories:
        - For each user type identified earlier, create a detailed user journey that outlines their interaction with the system from start to finish.
        - Break down each journey into individual screens or key interaction points.
        - For each screen or interaction point, provide detailed user stories in the format: "As a [user type], I want to [action] so that [benefit]."
        - Ensure that these user journeys and stories align with and reference the functional requirements generated in the previous section.

        2. Non-Functional Requirements: 
        Specify performance, security, scalability, and other non-functional aspects of the system.

        3. Annexure: 
        a. Functional Requirements: Create a separate table for each deliverable in the Functional Requirements. Each table should have the following columns:
        - Requirement ID
        - Module
        - Description

        b. 3rd Party Services and APIs: Create a table summarizing all suggested 3rd party services and APIs. This table should have the following columns:
        - Service/API Name
        - Functional Area
        - Key Features
        - Integration Benefit

        Provide detailed and professional content for each section, incorporating all the provided information and ensuring consistency with the previously generated sections.
        Use Markdown formatting for proper structure, including tables where specified.
        """

        with st.spinner('Generating Part 3: User Journey, User Stories, Non-Functional Requirements, and Annexure...'):
            with part3_container:
                response_part3 = generate_brd_part(prompt_part3, st.empty())

        progress_bar.progress(100)
        status_text.text("BRD Generation Completed!")

        # Combine all parts
        full_brd = f"""
        # Business Requirements Document (BRD)

        **Client Name:** {st.session_state.form_fields['client_name']}

        {response_part1}

        {response_part2}

        {response_part3}
        """

        st.success("BRD Generated Successfully!")
        display_lottie_or_text(lottie_completed, "BRD Generation Completed!", height=200)

        # Download options
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download BRD as Markdown",
                data=full_brd,
                file_name=f"BRD_{st.session_state.form_fields['client_name']}.md",
                mime="text/markdown"
            )
        with col2:
            pdf_buffer = convert_markdown_to_pdf(full_brd)
            st.download_button(
                label="Download BRD as PDF",
                data=pdf_buffer,
                file_name=f"BRD_{st.session_state.form_fields['client_name']}.pdf",
                mime="application/pdf"
            )

        # Display the generated BRD
        st.markdown("## Generated Business Requirements Document")
        st.markdown(full_brd)

    else:
        st.error("Please fill in all fields before generating the BRD.")

# Feedback Form in a collapsible section (open by default)
st.markdown("---")
with st.expander("We Value Your Feedback!", expanded=True):
    st.markdown("Please take a moment to provide your feedback on the BRD Generator tool.")
    
    # Embed the Tally feedback form with increased height
    tally_embed_code = """
    <iframe data-tally-src="https://tally.so/embed/mVV08g?alignLeft=1&transparentBackground=1&dynamicHeight=1" loading="lazy" width="100%" height="7200" frameborder="0" marginheight="0" marginwidth="0" title="BRD Generator Feedback Q&A"></iframe>
    <script>var d=document,w="https://tally.so/widgets/embed.js",v=function(){"undefined"!=typeof Tally?Tally.loadEmbeds():d.querySelectorAll("iframe[data-tally-src]:not([src])").forEach((function(e){e.src=e.dataset.tallySrc}))};if("undefined"!=typeof Tally)v();else if(d.querySelector('script[src="'+w+'"]')==null){var s=d.createElement("script");s.src=w,s.onload=v,s.onerror=v,d.body.appendChild(s);}</script>
    """
    
    html(tally_embed_code, height=4600)

# Add a visual representation of the BRD generation process
st.markdown("## BRD Generation Process")
process_chart = """
digraph G {
    rankdir=LR;
    node [shape=box, style=filled, color=lightblue];
    Input [label="User Input"];
    Process [label="AI Processing"];
    Output [label="Generated BRD"];
    Input -> Process -> Output;
}
"""
st.graphviz_chart(process_chart)

# Add some final instructions or information
st.markdown("""
---
### How to use this BRD Generator:
1. Fill in all the required fields in the form above.
2. Click on the "Generate BRD" button to create your Business Requirements Document.
3. The generated BRD will be displayed on this page.
4. You can download the BRD as a Markdown file or a PDF using the buttons provided.

If you need to make changes, simply update the form fields and generate the BRD again.
""")

# Footer
st.markdown("---")
st.markdown("© 2024 EMB-AI. All rights reserved.")
