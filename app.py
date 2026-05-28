import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import zscore
from PyPDF2 import PdfReader
import smtplib
from email.mime.text import MIMEText

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="AI Supply Chain Dashboard",
    layout="wide"
)

# ==========================================
# CUSTOM THEME
# ==========================================
st.markdown("""
<style>

.main {
    background-color: #f4f6f9;
}

h1 {
    color: #0f172a;
    text-align: center;
}

.stMetric {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 0px 5px rgba(0,0,0,0.1);
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# TITLE
# ==========================================
st.title("📦 AI Supply Chain Analytics Dashboard")

st.write("Upload CSV, Excel or PDF files for supply chain analytics")

# ==========================================
# FILE TYPE SELECTION
# ==========================================
file_type = st.sidebar.selectbox(
    "Choose File Type",
    ["CSV File", "Excel File", "PDF File"]
)

uploaded_file = None

# ==========================================
# FILE UPLOAD
# ==========================================
if file_type == "CSV File":

    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV File",
        type=["csv"]
    )

elif file_type == "Excel File":

    uploaded_file = st.sidebar.file_uploader(
        "Upload Excel File",
        type=["xlsx"]
    )

elif file_type == "PDF File":

    uploaded_file = st.sidebar.file_uploader(
        "Upload PDF File",
        type=["pdf"]
    )

# ==========================================
# PDF PROCESSING
# ==========================================
if uploaded_file is not None and file_type == "PDF File":

    pdf_reader = PdfReader(uploaded_file)

    text = ""

    for page in pdf_reader.pages:
        text += page.extract_text()

    st.success("✅ PDF Uploaded Successfully")

    st.subheader("📄 PDF Content")

    st.text(text[:5000])

# ==========================================
# CSV / EXCEL PROCESSING
# ==========================================
elif uploaded_file is not None:

    # ==========================================
    # LOAD DATA
    # ==========================================
    if file_type == "CSV File":

        df = pd.read_csv(uploaded_file)

    else:

        df = pd.read_excel(uploaded_file)

    # ==========================================
    # DATA PREVIEW
    # ==========================================
    st.subheader("📊 Dataset Preview")

    st.dataframe(df.head())

    # ==========================================
    # DATA CLEANING
    # ==========================================
    st.subheader("🧹 Data Cleaning")

    missing_before = df.isnull().sum().sum()

    duplicate_before = df.duplicated().sum()

    # Remove Missing Values
    df = df.dropna()

    # Remove Duplicate Values
    df = df.drop_duplicates()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Missing Values Removed",
        missing_before
    )

    col2.metric(
        "Duplicate Rows Removed",
        duplicate_before
    )

    col3.metric(
        "Final Rows",
        len(df)
    )

    st.success("✅ Data Cleaning Completed")

    # ==========================================
    # DOWNLOAD CLEAN DATA
    # ==========================================
    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="⬇ Download Cleaned CSV",
        data=csv,
        file_name='cleaned_supply_chain.csv',
        mime='text/csv'
    )

    # ==========================================
    # KPI METRICS
    # ==========================================
    st.subheader("📌 KPI Metrics")

    numeric_cols = df.select_dtypes(include=np.number).columns

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Rows",
        len(df)
    )

    if len(numeric_cols) > 0:

        col2.metric(
            "Average Value",
            round(df[numeric_cols[0]].mean(), 2)
        )

        col3.metric(
            "Maximum Value",
            round(df[numeric_cols[0]].max(), 2)
        )

    # ==========================================
    # CATEGORICAL COLUMNS
    # ==========================================
    categorical_cols = df.select_dtypes(include='object').columns

    # ==========================================
    # PIE CHART
    # ==========================================
    st.subheader("🥧 Pie Chart")

    if len(categorical_cols) > 0:

        pie_col = st.selectbox(
            "Select Column for Pie Chart",
            categorical_cols
        )

        pie_data = df[pie_col].value_counts()

        fig1, ax1 = plt.subplots(figsize=(6,6))

        ax1.pie(
            pie_data.values,
            labels=pie_data.index,
            autopct='%1.1f%%'
        )

        ax1.set_title(f"{pie_col} Distribution")

        st.pyplot(fig1)

    # ==========================================
    # LINE CHART
    # ==========================================
    st.subheader("📈 Line Chart")

    if len(numeric_cols) > 0:

        line_col = st.selectbox(
            "Select Numeric Column",
            numeric_cols,
            key="line"
        )

        fig2, ax2 = plt.subplots(figsize=(10,5))

        ax2.plot(
            df[line_col].head(100)
        )

        ax2.set_xlabel("Index")

        ax2.set_ylabel(line_col)

        ax2.set_title(f"{line_col} Trend")

        st.pyplot(fig2)

    # ==========================================
    # COLUMN BAR CHART
    # ==========================================
    st.subheader("📊 Column Bar Chart")

    if len(categorical_cols) > 0:

        bar_col = st.selectbox(
            "Select Column for Column Bar Chart",
            categorical_cols,
            key="bar"
        )

        bar_data = df[bar_col].value_counts()

        fig3, ax3 = plt.subplots(figsize=(8,5))

        ax3.bar(
            bar_data.index,
            bar_data.values
        )

        ax3.set_xlabel(bar_col)

        ax3.set_ylabel("Count")

        ax3.set_title(f"{bar_col} Analysis")

        plt.xticks(rotation=45)

        st.pyplot(fig3)

    # ==========================================
    # STACKED BAR CHART
    # ==========================================
    st.subheader("📚 Stacked Bar Chart")

    if len(categorical_cols) >= 2:

        stack_x = st.selectbox(
            "Select X Column",
            categorical_cols,
            key="stack_x"
        )

        stack_y = st.selectbox(
            "Select Stack Column",
            categorical_cols,
            key="stack_y"
        )

        stack_data = pd.crosstab(
            df[stack_x],
            df[stack_y]
        )

        fig4, ax4 = plt.subplots(figsize=(10,6))

        stack_data.plot(
            kind='bar',
            stacked=True,
            ax=ax4
        )

        ax4.set_xlabel(stack_x)

        ax4.set_ylabel("Count")

        ax4.set_title(f"{stack_x} by {stack_y}")

        plt.xticks(rotation=45)

        st.pyplot(fig4)

    # ==========================================
    # REAL-TIME DELAY ALERT
    # ==========================================
    st.subheader("🚨 Delay Alert System")

    if "Delay_Days" in df.columns:

        high_delay = df[
            df["Delay_Days"] > 5
        ]

        if len(high_delay) > 0:

            st.error(
                f"⚠ {len(high_delay)} delayed shipments found"
            )

            st.dataframe(high_delay.head(10))

        else:

            st.success("✅ No major delays found")

    # ==========================================
    # SALES ALERT
    # ==========================================
    st.subheader("💰 Sales Alert")

    if "Price" in df.columns:

        avg_sales = df["Price"].mean()

        low_sales = df[
            df["Price"] < avg_sales * 0.5
        ]

        if len(low_sales) > 0:

            st.warning(
                f"⚠ {len(low_sales)} low sales records found"
            )

            st.dataframe(low_sales.head(10))

    # ==========================================
    # EMAIL ALERT
    # ==========================================
    st.subheader("📧 Email Alert")

    sender_email = st.text_input(
        "Sender Email"
    )

    sender_password = st.text_input(
        "Sender Password",
        type="password"
    )

    receiver_email = st.text_input(
        "Receiver Email"
    )

    if st.button("Send Email Alert"):

        try:

            message = MIMEText(
                "Supply Chain Alert: Delay or Low Sales detected"
            )

            message['Subject'] = "Supply Chain Dashboard Alert"

            message['From'] = sender_email

            message['To'] = receiver_email

            server = smtplib.SMTP(
                'smtp.gmail.com',
                587
            )

            server.starttls()

            server.login(
                sender_email,
                sender_password
            )

            server.sendmail(
                sender_email,
                receiver_email,
                message.as_string()
            )

            server.quit()

            st.success("✅ Email Sent Successfully")

        except:

            st.error("❌ Email Sending Failed")

    # ==========================================
    # Z-SCORE ANOMALY DETECTION
    # ==========================================
    st.subheader("📈 Z-Score Anomaly Detection")

    if len(numeric_cols) > 0:

        z_col = st.selectbox(
            "Select Column for Z-Score",
            numeric_cols,
            key="zscore"
        )

        df["Z_Score"] = zscore(df[z_col])

        z_anomalies = df[
            (df["Z_Score"] > 3) |
            (df["Z_Score"] < -3)
        ]

        st.write(
            f"Total Z-Score Anomalies: {len(z_anomalies)}"
        )

        st.dataframe(
            z_anomalies.head(20)
        )

    # ==========================================
    # IQR ANOMALY DETECTION
    # ==========================================
    st.subheader("📊 IQR Anomaly Detection")

    if len(numeric_cols) > 0:

        iqr_col = st.selectbox(
            "Select Column for IQR",
            numeric_cols,
            key="iqr"
        )

        Q1 = df[iqr_col].quantile(0.25)

        Q3 = df[iqr_col].quantile(0.75)

        IQR = Q3 - Q1

        lower_limit = Q1 - 1.5 * IQR

        upper_limit = Q3 + 1.5 * IQR

        iqr_anomalies = df[
            (df[iqr_col] < lower_limit) |
            (df[iqr_col] > upper_limit)
        ]

        st.write(
            f"Total IQR Anomalies: {len(iqr_anomalies)}"
        )

        st.dataframe(
            iqr_anomalies.head(20)
        )

    # ==========================================
    # DATASET SUMMARY
    # ==========================================
    st.subheader("📋 Dataset Summary")

    st.write(df.describe())

    st.subheader("📑 Column Information")

    summary_df = pd.DataFrame({
        "Column Name": df.columns,
        "Data Type": df.dtypes.astype(str),
        "Missing Values": df.isnull().sum().values,
        "Unique Values": df.nunique().values
    })

    st.dataframe(summary_df)

else:

    st.info("📂 Upload CSV, Excel or PDF file")