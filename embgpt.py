import streamlit as st
from anthropic import Anthropic
import time
from datetime import datetime
import yaml

# Set up the Anthropic client
client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# Page configuration
st.set_page_config(page_title="EMB-AI", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS
st.markdown("""
    <style>
    .main .block-container {padding-top: 1rem;}
    .stTitle {font-size: 3rem; color: #0066cc;}
    .stSubheader {font-size: 1.5rem; color: #4d4d4d;}
    .stButton>button {background-color: #0066cc; color: white;}
    .stTextInput>div>div>input {background-color: #f0f2f6;}
    .stTextArea>div>div>textarea {background-color: #f0f2f6;}
    </style>
    """, unsafe_allow_html=True)

# Load confidentiality agreement
try:
    with open('confidentiality_agreement.yaml', 'r') as file:
        confidentiality_agreement = yaml.safe_load(file)
except FileNotFoundError:
    st.error("Confidentiality agreement file not found. Please ensure 'confidentiality_agreement.yaml' is in the same directory as the app.")
    confidentiality_agreement = "Confidentiality agreement not available."

# Sidebar for user onboarding
with st.sidebar:
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

# Main header
st.title("EMB-AI")
st.subheader("Your Business Analyst in your Pocket")

# Main content
st.markdown("""
This app generates a comprehensive Business Requirements Document (BRD) based on your inputs.
Fill in the fields below and click 'Generate BRD' to create your document.
""")

# Initialize session state for form fields
if 'form_fields' not in st.session_state:
    st.session_state.form_fields = {
        'client_name': '',
        'project_date': datetime.now().date(),
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
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Name", placeholder="e.g., Acme Corporation", 
                                    value=st.session_state.form_fields['client_name'], 
                                    key='client_name', on_change=update_form_field)
    with col2:
        project_date = st.date_input("Project Date", 
                                     value=st.session_state.form_fields['project_date'], 
                                     key='project_date', on_change=update_form_field)
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

        # Ensure admin user and admin panel are included
        user_types_list = st.session_state.form_fields['user_types'].split('\n')
        if 'Admin' not in user_types_list:
            user_types_list.append('Admin')
        user_types_str = '\n'.join(user_types_list)

        deliverables_list = st.session_state.form_fields['deliverables'].split('\n')
        if 'Admin Panel' not in deliverables_list:
            deliverables_list.append('Admin Panel')
        deliverables_str = '\n'.join(deliverables_list)

        # Create placeholders for each part
        part1_placeholder = st.empty()
        part2_placeholder = st.empty()
        part3_placeholder = st.empty()

        # Part 1: Confidentiality Agreement, Executive Summary, and Project Approach
        prompt_part1 = f"""
        Create the first part of a detailed Business Requirements Document (BRD) for the following project:

        Client Name: {st.session_state.form_fields['client_name']}
        Project Date: {st.session_state.form_fields['project_date']}
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
        Outline the methodology, timeline, and key milestones for the project. Structure this section as follows:

        # Project Approach
        Provide an introductory paragraph explaining the overall approach to the project.

        ## Stages of Development
        List and briefly introduce the main stages of the project (e.g., Requirement Analysis, System Design and Architecture, etc.).

        Then, for each stage, create a subsection like this:

        ### [Stage Name]
        Detailed description of the stage, including:
        - Key activities and objectives
        - Methodologies or tools used
        - Deliverables or outcomes
        - Importance in the overall project lifecycle

        Repeat this structure for each stage of the project.

        Provide detailed and professional content for each section, incorporating all the provided information.
        Use Markdown formatting for proper structure:
        - Use # for main headings (e.g., # 1. Confidentiality Agreement)
        - Use ## for subheadings (e.g., ## 1.1 Scope of Confidentiality)
        - Use ### for sub-subheadings where necessary
        - Use regular text for content
        - Use bullet points or numbered lists where appropriate
        """


        with st.spinner('Generating Part 1: Confidentiality Agreement, Executive Summary, and Project Approach...'):
            response_part1 = generate_brd_part(prompt_part1, part1_placeholder)
        
        progress_bar.progress(33)
        status_text.text("Part 1 completed. Generating Part 2...")

        # Part 2: Functional Requirements
        prompt_part2 = f"""
        Create the second part of a detailed Business Requirements Document (BRD) for the following project:

        Client Name: {st.session_state.form_fields['client_name']}
        Project Date: {st.session_state.form_fields['project_date']}
        Project Description and Requirements:
        {st.session_state.form_fields['project_description']}
        Types of Users:
        {user_types_str}
        Project Deliverables:
        {deliverables_str}

        Previously generated content:
        {response_part1}

        Now, include the Functional Requirements section:
        - For each deliverable, create at least 20 detailed modules.
        - Structure each requirement as: Deliverable, Module, Detailed Description of Module.
        - Ensure the requirements are comprehensive and cover all aspects of the project.
        - For each user-side module, include a corresponding management module in the admin panel.
        - Example format:
          # 4. Functional Requirements
          ## 4.1 User Management
          ### 4.1.1 User Registration
          Detailed description of the user registration process, including steps, data collected, and any validation or verification procedures.
          ### 4.1.2 User Profile Management
          Comprehensive explanation of user profile features, including editable fields, privacy settings, and any integration with other system components.
          ...

        Provide detailed and professional content, incorporating all the provided information and ensuring consistency with the previously generated sections.
        Use Markdown formatting for proper structure:
        - Use # for main headings (e.g., # 4. Functional Requirements)
        - Use ## for subheadings (e.g., ## 4.1 User Management)
        - Use ### for modules (e.g., ### 4.1.1 User Registration)
        - Use regular text for detailed descriptions
        - Use bullet points or numbered lists where appropriate
        """

        with st.spinner('Generating Part 2: Functional Requirements...'):
            response_part2 = generate_brd_part(prompt_part2, part2_placeholder)
        
        progress_bar.progress(66)
        status_text.text("Part 2 completed. Generating Part 3...")

        # Part 3: Non-Functional Requirements and Annexure
        prompt_part3 = f"""
        Create the third part of a detailed Business Requirements Document (BRD) for the following project:

        Client Name: {st.session_state.form_fields['client_name']}
        Project Date: {st.session_state.form_fields['project_date']}
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
        1. Non-Functional Requirements: Specify performance, security, scalability, and other non-functional aspects.
        2. Annexure: Create a separate table for each deliverable in the Functional Requirements. Each table should have the following columns:
           a. Requirement ID
           b. Module
           c. Description

        Provide detailed and professional content for each section, incorporating all the provided information and ensuring consistency with the previously generated sections. In the Annexure, make sure to create a distinct table for each deliverable, including the Admin Panel.
        Use Markdown formatting for proper structure:
        - Use # for main headings (e.g., # 5. Non-Functional Requirements)
        - Use ## for subheadings (e.g., ## 5.1 Performance Requirements)
        - Use regular text for content
        - Use bullet points or numbered lists where appropriate
        - For tables in the Annexure, use Markdown table syntax:
          | Requirement ID | Module | Description |
          |----------------|--------|-------------|
          | REQ-001        | ...    | ...         |
        """

        with st.spinner('Generating Part 3: Non-Functional Requirements and Annexure...'):
            response_part3 = generate_brd_part(prompt_part3, part3_placeholder)
        
        progress_bar.progress(100)
        status_text.text("BRD Generation Completed!")

        # Combine all parts
        full_brd = f"""
        # Business Requirements Document (BRD)

        **Client Name:** {st.session_state.form_fields['client_name']}
        **Project Date:** {st.session_state.form_fields['project_date']}

        {response_part1}

        {response_part2}

        {response_part3}
        """

        st.success("BRD Generated Successfully!")

        # Download option
        st.download_button(
            label="Download BRD as Markdown",
            data=full_brd,
            file_name=f"BRD_{st.session_state.form_fields['client_name']}_{st.session_state.form_fields['project_date']}.md",
            mime="text/markdown"
        )
    else:
        st.error("Please fill in all fields before generating the BRD.")