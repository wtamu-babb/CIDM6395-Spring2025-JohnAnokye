# 🚗 CIDM-6305: Business Intelligence and Decision Systems

Welcome to the **Business Intelligence and Machine Learning Project for Predicting Vehicle Selling Prices**. This repository contains a project aimed at leveraging advanced analytics and machine learning techniques to predict vehicle selling prices for **All American Motors Corp. (AAMC)**.

---

## 📋 Overview

This project utilizes historical vehicle sales data to develop predictive models and actionable insights. By analyzing sales trends and leveraging machine learning algorithms, the project aims to provide accurate predictions and empower data-driven decision-making.

---

## 📂 Project Phases

### 🛠️ Phase 1: Data Collection and Cleaning
- **Data Source**: Historical vehicle sales data from Kaggle's "Vehicle Sales and Market Trends Dataset".
- **Dataset Overview**:
  - **16 attributes** and **~100,000 records** detailing sales transactions, vehicle conditions, and market factors.
- **Key Steps**:
  1. Data preprocessing (handling missing values, detecting outliers, normalization).
  2. Feature identification using techniques like correlation analysis, PCA, and lasso regression.

---

### 🤖 Phase 2: Model Development
- **Objective**: Predict vehicle selling prices using features such as year, make, model, transmission, and condition.
- **Modeling**:
  - Models trained using **AutoML in Azure**.
  - Algorithms considered: Linear Regression, LightGBM, Decision Tree, ElasticNet, and Voting Ensemble.
- **Best Model**: The **Voting Ensemble** model, achieving an impressive **normalized RMSE of 0.01698**.
- **Deployment**: Integrated into a **Power BI dashboard** for actionable insights.

---

### 📊 Phase 3: Data Visualization
- **Tool**: **Power BI**
- **Dashboard Features**:
  - 📈 Revenue trends by year and quarter.
  - 🌎 Vehicles sold by state and make.
  - 🔍 Predicted vs. actual selling prices and percentage differences.
  - 📌 Key performance indicators for data-driven decision-making.

---

## 🎯 Key Deliverables
1. **Phase 1 & 2 Report**: Comprehensive documentation of the data collection, preprocessing, and model development process.
2. **Phase 2 Summary**: Concise highlights of data preparation, modeling, and evaluation outcomes.
3. **Phase 3 Dashboard**: An interactive **Power BI dashboard** showcasing sales trends, predictions, and insights.

---

## 🚀 Future Enhancements
- 📊 Expand the dataset to include additional variables like customer demographics and market trends.
- 🔄 Increase data update frequency for real-time predictions.
