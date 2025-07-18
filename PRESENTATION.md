# 🎯 Truffle Pig Creative Performance Dashboard

## 📊 Interactive Dashboard
**Live Dashboard**: [Your Streamlit URL will be here after deployment]

## 📓 Jupyter Notebook Analysis
**Interactive Notebook**: [Your Binder/Colab URL will be here after deployment]

## 🎬 Demo Walkthrough

### 1. Data Generation
Run `mockupdata.py` to generate synthetic campaign, session, and order data:
```bash
python3 mockupdata.py
```

### 2. Model Training
Execute the Jupyter notebook to train the machine learning model:
- Open `JupyterFile.ipynb` in Jupyter/Binder/Colab
- Run all cells to train the XGBoost conversion prediction model
- This creates `conversion_model.joblib` and `model_features.joblib`

### 3. Dashboard Exploration
Use the Streamlit app to explore results:
```bash
streamlit run dashboard.py
```

## 📈 Key Insights & Features

### 🎯 ROAS & CAC Analysis
- **Return on Ad Spend (ROAS)** by creative format and theme
- **Customer Acquisition Cost (CAC)** optimization
- Interactive treemap visualization of performance

### 📊 Payback Curve
- Campaign-specific payback period analysis
- Revenue accumulation over time
- Break-even point identification

### 🚀 Lift Forecast
- Predictive modeling for conversion rates
- Machine learning-powered insights
- Performance optimization recommendations

### 🧠 Model Insights
- Feature importance analysis
- Model performance metrics
- Predictive analytics dashboard

## 🔧 Technical Stack

| Component | Technology |
|-----------|------------|
| **Data Processing** | Pandas, NumPy |
| **Machine Learning** | XGBoost, Scikit-learn |
| **Visualization** | Plotly, Streamlit |
| **Deployment** | Streamlit Cloud, Binder |
| **Hyperparameter Tuning** | Optuna |

## 📊 Data Structure

### Generated Mock Data
- **campaigns.csv**: Campaign metadata, spend, creative formats
- **sessions.csv**: User session data, conversion events
- **orders.csv**: Purchase data, revenue attribution

### Model Files
- **conversion_model.joblib**: Trained XGBoost model
- **model_features.joblib**: Feature list for consistency

## 🎯 Business Value

### For Marketing Teams
- **Creative Performance**: Identify which ad formats and themes drive the best ROAS
- **Budget Optimization**: Allocate spend to high-performing creatives
- **Predictive Insights**: Forecast conversion rates for new campaigns

### For Data Scientists
- **End-to-End Pipeline**: Complete ML workflow from data generation to deployment
- **Interactive Visualization**: Real-time dashboard for data exploration
- **Reproducible Analysis**: Jupyter notebook with full documentation

## 🚀 Quick Access Links

Once deployed, your client will have access to:

1. **📊 Live Dashboard**: Interactive Streamlit app with real-time data exploration
2. **📓 Analysis Notebook**: Detailed Jupyter notebook with full ML workflow
3. **📈 Presentation**: This document with key insights and business value

## 📞 Support & Next Steps

### For Technical Questions
- Review the `DEPLOYMENT.md` file for setup instructions
- Check `README.md` for local development setup
- All code is documented and ready for production use

### For Client Presentations
- Use the live dashboard for interactive demos
- Share the notebook for detailed technical review
- Customize the presentation based on client needs

---

**🎉 Ready for Client Presentation!**

Your Truffle Pig Creative Performance Dashboard is now ready to showcase the power of data-driven creative optimization to your clients. 