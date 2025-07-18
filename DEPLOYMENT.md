# 🚀 Deployment Guide: Truffle Pig Creative Performance Dashboard

This guide will help you deploy both the **Jupyter Notebooks** and **Streamlit Dashboard** to make them accessible online for client presentations.

## 📋 Prerequisites

- GitHub account
- Python 3.8+ installed
- Git installed on your machine

---

## 🎯 Option 1: GitHub + Streamlit Cloud (Recommended)

### Step 1: Prepare Your Repository

1. **Initialize Git Repository** (if not already done):
```bash
git init
git add .
git commit -m "Initial commit: Truffle Pig Creative Performance Dashboard"
```

2. **Create GitHub Repository**:
   - Go to [GitHub.com](https://github.com)
   - Click "New repository"
   - Name it: `truffle-pig-dashboard`
   - Make it **Public** (required for free Streamlit Cloud)
   - Don't initialize with README (we already have one)

3. **Push to GitHub**:
```bash
git remote add origin https://github.com/YOUR_USERNAME/truffle-pig-dashboard.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy Streamlit Dashboard

1. **Go to Streamlit Cloud**:
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Deploy Your App**:
   - Click "New app"
   - Select your repository: `truffle-pig-dashboard`
   - Set the path to your Streamlit app: `dashboard.py`
   - Click "Deploy app"

3. **Your Dashboard URL**:
   - Streamlit will provide a URL like: `https://your-app-name.streamlit.app`
   - Share this URL with your client

### Step 3: Deploy Jupyter Notebooks

1. **Create a Binder Configuration**:
   Create a file named `binder/environment.yml`:
```yaml
name: truffle-pig
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.9
  - jupyter
  - pandas
  - numpy
  - scikit-learn
  - xgboost
  - plotly
  - streamlit
  - optuna
  - matplotlib
  - seaborn
  - pip
  - pip:
    - lifelines
```

2. **Push to GitHub**:
```bash
git add .
git commit -m "Add Binder configuration for Jupyter notebooks"
git push
```

3. **Launch with Binder**:
   - Go to [mybinder.org](https://mybinder.org)
   - Enter your repository URL: `https://github.com/YOUR_USERNAME/truffle-pig-dashboard`
   - Click "Launch"

---

## 🎯 Option 2: GitHub + Google Colab

### Step 1: Upload Notebook to Google Colab

1. **Open Google Colab**:
   - Go to [colab.research.google.com](https://colab.research.google.com)
   - Sign in with your Google account

2. **Upload Your Notebook**:
   - Click "File" → "Upload notebook"
   - Select your `JupyterFile.ipynb`
   - The notebook will open in Colab

3. **Share the Colab Link**:
   - Click "Share" in the top right
   - Set permissions to "Anyone with the link can view"
   - Copy the shareable link

### Step 2: Deploy Streamlit (Same as Option 1)

Follow the Streamlit Cloud deployment steps from Option 1.

---

## 🎯 Option 3: GitHub + Heroku (Advanced)

### Step 1: Prepare for Heroku

1. **Create `Procfile`**:
```
web: streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0
```

2. **Create `setup.sh`**:
```bash
mkdir -p ~/.streamlit/
echo "\
[general]\n\
email = \"your-email@example.com\"\n\
" > ~/.streamlit/credentials.toml
echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
```

3. **Update `requirements.txt`** (if needed):
```txt
streamlit==1.46.1
pandas==2.3.0
numpy==2.3.1
plotly==6.2.0
xgboost==3.0.2
scikit-learn==1.7.0
joblib==1.5.1
```

### Step 2: Deploy to Heroku

1. **Install Heroku CLI** and login
2. **Create Heroku app**:
```bash
heroku create your-app-name
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main
```

---

## 📊 Client Presentation Setup

### Create a Presentation Landing Page

Create a file named `presentation.md`:

```markdown
# 🎯 Truffle Pig Creative Performance Dashboard

## 📊 Interactive Dashboard
**Live Dashboard**: [Your Streamlit URL]

## 📓 Jupyter Notebook Analysis
**Interactive Notebook**: [Your Binder/Colab URL]

## 🎬 Demo Walkthrough
1. **Data Generation**: Run `mockupdata.py` to generate synthetic data
2. **Model Training**: Execute the Jupyter notebook to train the ML model
3. **Dashboard Exploration**: Use the Streamlit app to explore results

## 📈 Key Insights
- ROAS (Return on Ad Spend) analysis by creative format
- CAC (Customer Acquisition Cost) optimization
- Payback period visualization
- Predictive lift forecasting

## 🔧 Technical Stack
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: XGBoost, Scikit-learn
- **Visualization**: Plotly, Streamlit
- **Deployment**: Streamlit Cloud, Binder
```

---

## 🚀 Quick Start Commands

```bash
# 1. Initialize and push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/truffle-pig-dashboard.git
git push -u origin main

# 2. Deploy to Streamlit Cloud
# Go to share.streamlit.io and follow the deployment steps

# 3. Test locally
streamlit run dashboard.py
```

---

## 📞 Support & Troubleshooting

### Common Issues:

1. **Streamlit deployment fails**:
   - Check that `dashboard.py` is in the root directory
   - Ensure all dependencies are in `requirements.txt`
   - Verify the repository is public

2. **Binder takes too long to start**:
   - Optimize the `environment.yml` file
   - Consider using Google Colab instead

3. **Data files not found**:
   - Ensure `campaigns.csv`, `sessions.csv`, `orders.csv` are committed
   - Check file paths in the code

### Getting Help:
- Streamlit Cloud: [docs.streamlit.io](https://docs.streamlit.io)
- Binder: [mybinder.readthedocs.io](https://mybinder.readthedocs.io)
- GitHub: [github.com](https://github.com)

---

## 🎉 Success Checklist

- [ ] Repository pushed to GitHub
- [ ] Streamlit dashboard deployed and accessible
- [ ] Jupyter notebook accessible via Binder/Colab
- [ ] All data files committed to repository
- [ ] Client can access both dashboard and notebook
- [ ] Presentation materials prepared

**Your client can now access both the interactive dashboard and the detailed analysis notebook online! 🚀** 