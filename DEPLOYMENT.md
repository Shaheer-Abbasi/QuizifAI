# 🚀 AI Quiz App Deployment Guide

## 📋 Prerequisites

1. **GitHub Account** - To host your code
2. **Render Account** - Free at [render.com](https://render.com)
3. **Google AI API Key** - From [Google AI Studio](https://makersuite.google.com/app/apikey)

---

## 🎯 **Option 1: Deploy to Render (Recommended)**

### Step 1: Push to GitHub

1. **Create a new repository** on GitHub
2. **Push your code**:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

### Step 2: Deploy on Render

1. **Go to [render.com](https://render.com)** and sign up/login
2. **Click "New +"** → **"Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service**:
   - **Name**: `ai-quiz-app` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`

### Step 3: Set Environment Variables

In your Render dashboard, add these environment variables:

1. **SECRET_KEY**: Generate a secure random string
   ```python
   # Generate one using Python:
   import secrets
   print(secrets.token_hex(32))
   ```

2. **GEMINI_API_KEY**: Your Google AI API key

3. **FLASK_ENV**: `production`

### Step 4: Deploy!

- **Click "Create Web Service"**
- **Wait for deployment** (5-10 minutes)
- **Your app will be live** at `https://your-app-name.onrender.com`

---

## 🎯 **Option 2: Deploy to Railway**

### Step 1: Push to GitHub (same as above)

### Step 2: Deploy on Railway

1. **Go to [railway.app](https://railway.app)** and sign up
2. **Click "New Project"** → **"Deploy from GitHub repo"**
3. **Select your repository**
4. **Add environment variables**:
   - `SECRET_KEY`: Generate a secure key
   - `GEMINI_API_KEY`: Your Google AI API key
   - `FLASK_ENV`: `production`

### Step 3: Deploy!

- **Railway auto-detects** your Python app
- **Deployment happens automatically**
- **Your app will be live** at the provided Railway URL

---

## 🎯 **Option 3: Deploy to PythonAnywhere**

### Step 1: Upload Files

1. **Sign up at [pythonanywhere.com](https://pythonanywhere.com)**
2. **Upload your project files** via the Files tab
3. **Install requirements** in a Bash console:
   ```bash
   pip3.10 install --user -r requirements.txt
   ```

### Step 2: Configure Web App

1. **Go to Web tab** → **"Add a new web app"**
2. **Choose Flask**
3. **Set source code path** to your project directory
4. **Set environment variables** in the .env file

---

## 🔧 **Environment Variables You Need**

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `your-secret-key-here` |
| `GEMINI_API_KEY` | Google AI API key | `AIza...` |
| `FLASK_ENV` | Environment | `production` |
| `DATABASE_URL` | Database URL (auto-provided by Render) | `postgresql://...` |

---

## ✅ **Post-Deployment Checklist**

- [ ] **Test user registration/login**
- [ ] **Test quiz creation**
- [ ] **Test question generation**
- [ ] **Test taking quizzes**
- [ ] **Test analytics page**
- [ ] **Verify all pages load correctly**

---

## 🐛 **Troubleshooting**

### Common Issues:

1. **"Internal Server Error"**
   - Check your environment variables are set
   - Verify your GEMINI_API_KEY is correct

2. **Database errors**
   - Render automatically provisions PostgreSQL
   - Your app handles the database creation

3. **Static files not loading**
   - Render serves static files automatically
   - Check your file paths are correct

### Getting Logs:

- **Render**: Check the "Logs" tab in your service dashboard
- **Railway**: View logs in the deployment section
- **PythonAnywhere**: Check error logs in the Web tab

---

## 🎉 **You're Live!**

Once deployed, your AI Quiz App will be accessible worldwide! Share the URL with others to try your quiz application.

**Features that work in production:**
- ✅ User registration & authentication
- ✅ Quiz creation and management
- ✅ AI-powered question generation
- ✅ Interactive quiz taking
- ✅ Progress analytics with charts
- ✅ Responsive design for all devices

---

## 📞 **Need Help?**

If you encounter issues:
1. Check the platform-specific documentation
2. Review the deployment logs
3. Verify all environment variables are set correctly
4. Ensure your GitHub repository is public (for free tiers)
