#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Streamlit web interface for CAELUS compliance checking system.
Includes document upload, compliance analysis, and chat functionality.
"""

import streamlit as st
import sys
from pathlib import Path
import os
import tempfile
import json
import time

# Add src to path
src_path = Path(__file__).parent
sys.path.append(str(src_path))

from data_ingestion import DataIngestion
from compliance_checker import ComplianceChecker
from report_generator import ReportGenerator

# Function to save uploaded files to a temporary directory
def save_uploaded_files(uploaded_files, temp_dir):
    saved_paths = []
    # Ensure uploaded_files is a list
    if not isinstance(uploaded_files, list):
        uploaded_files = [uploaded_files]
        
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved_paths.append(file_path)
    return saved_paths

def chat_with_documents(user_question, design_text, regulations_text, compliance_results):
    """
    Chat functionality to answer questions about uploaded documents and compliance results.
    """
    # Simple rule-based chat responses
    responses = {
        "compliance": "Based on the analysis, the overall compliance score is {score}%. {issues} issues were found.",
        "insulation": "The design specifies {design_thickness}mm insulation thickness, while regulations require minimum {required_thickness}mm.",
        "seismic": "The design can withstand {design_seismic}g seismic events, while regulations require minimum {required_seismic}g.",
        "emergency": "The emergency cooling system can operate for {design_hours} hours without external power, which {meets} the required {required_hours} hours.",
        "pumps": "The containment spray system has {design_pumps} pumps, while regulations require minimum {required_pumps} pumps."
    }
    
    # Extract key information from compliance results
    compliance_score = 0
    issues_count = 0
    design_thickness = "N/A"
    required_thickness = "N/A"
    design_seismic = "N/A"
    required_seismic = "N/A"
    design_hours = "N/A"
    required_hours = "N/A"
    design_pumps = "N/A"
    required_pumps = "N/A"
    
    if compliance_results:
        # Calculate compliance score
        total_checks = len(compliance_results)
        compliant_count = sum(1 for r in compliance_results if r.get('compliance_status') == 'Compliant')
        compliance_score = (compliant_count / total_checks * 100) if total_checks > 0 else 0
        issues_count = total_checks - compliant_count
        
        # Extract specific values from results
        for result in compliance_results:
            regulation_text = result.get('regulation_text', '').lower()
            design_text_lower = result.get('design_text', '').lower()
            
            if 'insulation' in regulation_text and 'thickness' in regulation_text:
                # Extract thickness values
                import re
                thickness_match = re.search(r'(\d+)\s*mm', regulation_text)
                if thickness_match:
                    required_thickness = thickness_match.group(1)
                
                thickness_match = re.search(r'(\d+)\s*mm', design_text_lower)
                if thickness_match:
                    design_thickness = thickness_match.group(1)
            
            elif 'seismic' in regulation_text:
                seismic_match = re.search(r'(\d+\.\d+)g', regulation_text)
                if seismic_match:
                    required_seismic = seismic_match.group(1)
                
                seismic_match = re.search(r'(\d+\.\d+)g', design_text_lower)
                if seismic_match:
                    design_seismic = seismic_match.group(1)
            
            elif 'hours' in regulation_text and 'emergency' in regulation_text:
                hours_match = re.search(r'(\d+)\s*hours', regulation_text)
                if hours_match:
                    required_hours = hours_match.group(1)
                
                hours_match = re.search(r'(\d+)\s*hours', design_text_lower)
                if hours_match:
                    design_hours = hours_match.group(1)
            
            elif 'pumps' in regulation_text and 'containment' in regulation_text:
                pumps_match = re.search(r'(\d+)\s*(?:independent|separate)', regulation_text)
                if pumps_match:
                    required_pumps = pumps_match.group(1)
                
                pumps_match = re.search(r'(\d+)\s*(?:independent|separate)', design_text_lower)
                if pumps_match:
                    design_pumps = pumps_match.group(1)
    
    # Generate response based on user question
    question_lower = user_question.lower()
    
    if any(word in question_lower for word in ['compliance', 'score', 'overall', 'result']):
        return responses['compliance'].format(score=f"{compliance_score:.1f}", issues=issues_count)
    
    elif any(word in question_lower for word in ['insulation', 'thickness']):
        return responses['insulation'].format(design_thickness=design_thickness, required_thickness=required_thickness)
    
    elif any(word in question_lower for word in ['seismic', 'earthquake']):
        return responses['seismic'].format(design_seismic=design_seismic, required_seismic=required_seismic)
    
    elif any(word in question_lower for word in ['emergency', 'power', 'hours']):
        meets = "meets" if design_hours != "N/A" and required_hours != "N/A" and float(design_hours) >= float(required_hours) else "does not meet"
        return responses['emergency'].format(design_hours=design_hours, required_hours=required_hours, meets=meets)
    
    elif any(word in question_lower for word in ['pumps', 'containment']):
        return responses['pumps'].format(design_pumps=design_pumps, required_pumps=required_pumps)
    
    else:
        return "I can help you with questions about compliance scores, insulation thickness, seismic resistance, emergency power requirements, and containment pumps. Please ask a specific question about these topics."

def main():
    st.set_page_config(layout="wide", page_title="CAELUS Compliance System")
    st.title("🚀 CAELUS - Compliance Assessment Engine")
    st.markdown("*Compliance Assessment Engine Leveraging Unified Semantics*")

    # Initialize session state
    if "temp_dir" not in st.session_state:
        st.session_state.temp_dir = tempfile.mkdtemp()
    if "processed" not in st.session_state:
        st.session_state.processed = False
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    if "results" not in st.session_state:
        st.session_state.results = None
    if "design_text" not in st.session_state:
        st.session_state.design_text = ""
    if "regulations_text" not in st.session_state:
        st.session_state.regulations_text = ""
    if "semantic_units_path" not in st.session_state:
        st.session_state.semantic_units_path = ""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose a page", ["Home", "1. Upload & Process", "2. Run Analysis", "3. View Results", "4. Chat with Documents"])
    
    if page == "Home":
        st.markdown("""
        ## Welcome to CAELUS
        
        CAELUS is an AI-powered system for assessing compliance of nuclear engineering designs 
        against regulatory requirements and industry standards.
        
        ### Key Features:
        - 🤖 **LLM-based Compliance Detection** (Rule-based in this demo)
        - 🔗 **Knowledge Graph Integration** (Skipped in this demo)
        - 📊 **Automated Report Generation**
        - 🎯 **High Accuracy Compliance Checking**
        - 💬 **Interactive Chat with Documents**
        
        ### How to Use:
        1.  Navigate to the **1. Upload & Process** page.
        2.  Upload your regulatory document and a design specification file (TXT format).
        3.  Click "Process Documents".
        4.  Go to the **2. Run Analysis** page to start the compliance check.
        5.  View the detailed report on the **3. View Results** page.
        6.  Chat with your documents on the **4. Chat with Documents** page.
        """)
        
    elif page == "1. Upload & Process":
        st.header("Document Upload & Processing")
        
        # For simplicity, this demo uses text files.
        regulatory_file = st.file_uploader(
            "Upload ONE Regulatory Document (TXT only)", 
            accept_multiple_files=False,
            type=['txt']
        )
        
        design_file = st.file_uploader(
            "Upload ONE Design Specification (TXT only)",
            type=['txt']
        )
        
        if st.button("Process Documents"):
            if regulatory_file and design_file:
                with st.spinner("Processing documents... This may take a moment."):
                    # Save files to temp dir
                    reg_path = save_uploaded_files(regulatory_file, st.session_state.temp_dir)[0]
                    design_path = save_uploaded_files(design_file, st.session_state.temp_dir)[0]

                    # Process regulations
                    data_ingest = DataIngestion()
                    st.session_state.regulations_text = data_ingest.text_from_file(reg_path)
                    semantic_units = data_ingest.text_to_semantic_units(st.session_state.regulations_text)
                    
                    # Save semantic units to a file in the temp dir
                    semantic_units_path = os.path.join(st.session_state.temp_dir, "semantic_units.json")
                    with open(semantic_units_path, 'w', encoding='utf-8') as f:
                        json.dump(semantic_units, f, ensure_ascii=False, indent=2)
                    
                    st.session_state.semantic_units_path = semantic_units_path
                    
                    # Process design file
                    st.session_state.design_text = data_ingest.text_from_file(design_path)

                    st.session_state.processed = True
                    st.success("✅ Documents processed successfully!")
                    st.info("Navigate to the 'Run Analysis' page to continue.")
            else:
                st.error("⚠️ Please upload both a regulatory document and a design specification.")

    elif page == "2. Run Analysis":
        st.header("Compliance Analysis")
        if not st.session_state.processed:
            st.warning("Please upload and process documents first on the '1. Upload & Process' page.")
        else:
            st.markdown("Your documents are ready for analysis.")
            if st.button("Start Compliance Check"):
                with st.spinner("Running compliance analysis... This might take some time."):
                    checker = ComplianceChecker(
                        semantic_units_path=st.session_state.semantic_units_path,
                        # Force rule-based for this demo
                        use_llm=False  
                    )
                    
                    # Batch check against all regulations
                    results = checker.batch_compliance_check(st.session_state.design_text)
                    st.session_state.results = results
                    st.session_state.analysis_complete = True
                    st.success("✅ Analysis complete!")
                    st.info("Navigate to the 'View Results' page to see the report, or try the Chat feature!")
        
    elif page == "3. View Results":
        st.header("Analysis Results")
        if not st.session_state.analysis_complete:
            st.warning("Please run the analysis first on the '2. Run Analysis' page.")
        else:
            # Instantiate a report generator to create the summary
            report_gen = ReportGenerator(output_dir=st.session_state.temp_dir)
            report_data = report_gen.generate_summary_data(st.session_state.results)
            
            # Display summary
            st.subheader("Compliance Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Overall Compliance", f"{report_data['summary']['compliance_percentage']:.1f}%")
            col2.metric("Total Checks", report_data['summary']['total_requirements'])
            col3.metric("Issues Found", report_data['summary']['status_counts'].get('Non-Compliant', 0))

            # Display status distribution
            st.subheader("Status Distribution")
            if 'status_chart_path' in report_data['summary'] and os.path.exists(report_data['summary']['status_chart_path']):
                st.image(report_data['summary']['status_chart_path'])
            else:
                st.write(report_data['summary']['status_counts'])

            # Display detailed results
            st.subheader("Detailed Compliance Results")
            for result in st.session_state.results:
                status = result.get('compliance_status', 'Unknown')
                if status == "Compliant":
                    emoji = "✅"
                elif status == "Non-Compliant":
                    emoji = "❌"
                else:
                    emoji = "⚠️"
                
                with st.expander(f"{emoji} {status}: Regulation Article {result.get('metadata', {}).get('article_id', 'N/A')}"):
                    st.markdown(f"**Regulation:**")
                    st.info(result.get('regulation_text'))
                    st.markdown(f"**Reasoning:**")
                    st.warning(result.get('reasoning', 'No reasoning provided.'))

    elif page == "4. Chat with Documents":
        st.header("💬 Chat with Your Documents")
        
        if not st.session_state.analysis_complete:
            st.warning("Please complete the analysis first on the '2. Run Analysis' page to enable chat functionality.")
        else:
            st.markdown("""
            Ask questions about your uploaded documents and compliance analysis results.
            
            **Example questions you can ask:**
            - What is the overall compliance score?
            - How does the insulation thickness compare to requirements?
            - What is the seismic resistance capability?
            - How long can the emergency system operate without power?
            - How many containment pumps are there?
            """)
            
            # Chat interface
            user_question = st.text_input("Ask a question about your documents:", placeholder="e.g., What is the compliance score?")
            
            if st.button("Ask Question"):
                if user_question.strip():
                    with st.spinner("Analyzing your question..."):
                        # Get response from chat function
                        response = chat_with_documents(
                            user_question, 
                            st.session_state.design_text, 
                            st.session_state.regulations_text, 
                            st.session_state.results
                        )
                        
                        # Add to chat history
                        st.session_state.chat_history.append({
                            "question": user_question,
                            "response": response,
                            "timestamp": time.strftime("%H:%M:%S")
                        })
                        
                        st.success("Response generated!")
                else:
                    st.error("Please enter a question.")
            
            # Display chat history
            if st.session_state.chat_history:
                st.subheader("Chat History")
                for i, chat in enumerate(reversed(st.session_state.chat_history)):
                    with st.expander(f"Q: {chat['question']} ({chat['timestamp']})"):
                        st.markdown(f"**Question:** {chat['question']}")
                        st.markdown(f"**Answer:** {chat['response']}")
            
            # Clear chat history
            if st.button("Clear Chat History"):
                st.session_state.chat_history = []
                st.success("Chat history cleared!")

if __name__ == "__main__":
    main()
