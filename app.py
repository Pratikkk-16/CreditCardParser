import os
import tempfile
import streamlit as st
import pandas as pd

from parser import ChaseParser, StatementData

# Page configuration
st.set_page_config(
    page_title="Credit Card Statement Parser",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        margin-bottom: 3rem;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 3rem;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Upload area styling */
    .upload-section {
        background: #f8fafc;
        border: 2px dashed #cbd5e1;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-section:hover {
        border-color: #667eea;
        background: #f1f5f9;
    }
    
    /* Metrics styling */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .metric-label {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        color: #64748b;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: #1e293b;
        font-size: 2rem;
        margin: 0;
    }
    
    /* Section headers */
    .section-header {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #1e293b;
        font-size: 1.5rem;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Success message styling */
    .success-message {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Error message styling */
    .error-message {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Info message styling */
    .info-message {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with information
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: #1e293b; margin: 0;">💳 Statement Parser</h2>
        <p style="color: #64748b; margin: 0.5rem 0;">Extract data from PDF statements</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📋 Supported Features")
    st.markdown("""
    - credit card statements Parser
    - Transaction extraction
    - Balance and due date parsing
    - Billing cycle detection
    - Transaction summaries
    """)
    
    st.markdown("### How it works")
    st.markdown("""
    1. Upload your PDF statement
    2. Parser parses the document
    3. Extract structured data
    4. View results instantly
    """)
    
    st.markdown("### Privacy")
    st.markdown("""
    - Files are processed locally
    - No data is stored permanently
    - Temporary files are deleted
    - Your data stays private
    """)

# Main header
st.markdown("""
<div class="main-header">
    <h1>Credit Card Statement Parser</h1>
    <p>Upload your PDF statement to extract transaction data automatically</p>
</div>
""", unsafe_allow_html=True)


# Upload section with modern styling
st.markdown("""
<div class="upload-section">
    <h3 style="color: #64748b; margin-bottom: 1rem;">Upload Your Statement</h3>
    <p style="color: #94a3b8; margin: 0;">Supported formats: PDF</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a PDF file", 
    type=["pdf"], 
    accept_multiple_files=False,
    help="Upload a Chase credit card statement PDF to extract transaction data"
)

if uploaded_file is not None:
    parser = ChaseParser()
    tmp_path = None
    try:
        with st.spinner("Parsing PDF statement..."):
            # Write uploaded bytes to a temporary file for pdfplumber
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name

            # Parse the temporary file
            data: StatementData = parser.parse(tmp_path)

        # Success message
        st.markdown("""
        <div class="success-message">
            Statement parsed successfully! Here are the extracted details:
        </div>
        """, unsafe_allow_html=True)

        # Display results with modern styling
        st.markdown('<h2 class="section-header">📊 Summary</h2>', unsafe_allow_html=True)
        
        # Create custom metric cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Card Last 4</div>
                <div class="metric-value">{data.card_last_4 or "-"}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Billing Cycle</div>
                <div class="metric-value" style="font-size: 1.2rem;">{data.billing_cycle or "-"}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Due Date</div>
                <div class="metric-value" style="font-size: 1.2rem;">{data.due_date or "-"}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            balance_color = "#ef4444" if data.total_balance > 0 else "#10b981"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Balance</div>
                <div class="metric-value" style="color: {balance_color};">${data.total_balance:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        # Transactions section
        st.markdown('<h2 class="section-header">Extracted Transactions</h2>', unsafe_allow_html=True)
        df = pd.DataFrame(data.transactions)
        
        if not df.empty:
            # Format the dataframe for better display
            df_display = df.copy()
            df_display['Amount'] = df_display['Amount'].apply(lambda x: f"${x:,.2f}")
            
            # Display with custom styling
            st.dataframe(
                df_display, 
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Date": st.column_config.TextColumn("📅 Date", width="medium"),
                    "Description": st.column_config.TextColumn("🏪 Description", width="large"),
                    "Amount": st.column_config.TextColumn("💰 Amount", width="small")
                }
            )
            
            # Transaction summary
            total_transactions = len(df)
            total_amount = df['Amount'].sum()
            avg_amount = df['Amount'].mean()
            
            st.markdown(f"""
            <div style="background: #f8fafc; padding: 1.5rem; border-radius: 10px; margin-top: 1rem;">
                <h4 style="color: #1e293b; margin: 0 0 1rem 0;">📈 Transaction Summary</h4>
                <div style="display: flex; gap: 2rem; flex-wrap: wrap; color: #000000;">
                    <div style="color: #000000;"><strong>Total Transactions:</strong> {total_transactions}</div>
                    <div style="color: #000000;"><strong>Total Amount:</strong> ${total_amount:,.2f}</div>
                    <div style="color: #000000;"><strong>Average Amount:</strong> ${avg_amount:,.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-message">
                ℹ️ No transactions detected in this statement.
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.markdown(f"""
        <div class="error-message">
            ❌ Failed to parse PDF: {e}
        </div>
        """, unsafe_allow_html=True)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


