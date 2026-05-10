# 🏟️ Venue Analytics Dashboard

A premium, production-ready business intelligence dashboard for live entertainment venues. Built with **Streamlit**, **Plotly**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-2.74.0-black?style=for-the-badge&logo=streamlit&logoColor=white)](https://customer-dash.streamlit.app/)



## 🚀 Overview

This dashboard provides venue managers and stakeholders with actionable insights into revenue, customer demographics, and temporal visit patterns. It features a bold, high-contrast aesthetic with sharp edges and professional iconography.

### Key Analytical Modules:
- **🏠 Overview**: High-level KPIs and critical trend summaries.
- **💰 Revenue Analysis**: Deep dive into ticket sales, merchandise, and drink revenue by country and seating region.
- **👥 Customer Analysis**: Demographic breakdowns (Age, Gender) and geographic distribution.
- **🕒 Time-Based Analysis**: Monthly trends, day-of-week patterns, and revenue composition over time.

## Live Demo
Link:- https://customer-dash.streamlit.app/

## 🛠️ Technical Stack

- **Framework**: [Streamlit](https://streamlit.io/)
- **Visualizations**: [Plotly Express](https://plotly.com/python/)
- **Data Processing**: [Pandas](https://pandas.pydata.org/)



## 📂 Project Structure

```text
├── app.py                # Main application entry & global styling
├── data/
│   └── raw.csv           # Venue dataset
├── views/                # Modular analytical components
│   ├── overview.py
│   ├── revenue_analysis.py
│   ├── customer_analysis.py
│   └── time_analysis.py
├── requirements.txt      # Dependency management
```



## 🔧 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/TonyRoyze/customer-dash
   cd customer-dash
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```
