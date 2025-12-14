# GitHub & Deployment Setup Guide

## Step 1: Push to GitHub

### Option A: If you have an existing GitHub repository
```bash
cd d:\Learning2\LLMs\mvp_project

# Add the remote origin (replace with your GitHub repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

### Option B: Create a new repository on GitHub
1. Go to https://github.com/new
2. Create a new repository named `mvp-agentic-assistant` (or your preferred name)
3. Copy the HTTPS URL provided (e.g., `https://github.com/YOUR_USERNAME/mvp-agentic-assistant.git`)
4. Run these commands:
```bash
cd d:\Learning2\LLMs\mvp_project
git remote add origin https://github.com/YOUR_USERNAME/mvp-agentic-assistant.git
git branch -M main
git push -u origin main
```

**Note**: If you see authentication errors, use a Personal Access Token instead of your password:
- Go to GitHub Settings → Developer Settings → Personal Access Tokens
- Create a new token with `repo` scope
- Use the token as your password when prompted

---

## Step 2: Deploy Streamlit App on Streamlit Cloud

### Prerequisites
- GitHub account with your repository
- Streamlit Cloud account (free at https://streamlit.io/cloud)

### Deployment Steps

1. **Sign up for Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Click "Sign up" and authenticate with GitHub
   - Grant Streamlit permission to access your repositories

2. **Deploy Your App**
   - Click "Create app"
   - Connect to your GitHub repository
   - Select the branch: `main`
   - Set the main file path: `streamlit_app.py`
   - Click "Deploy"

3. **Configure Environment Variables (if needed)**
   - In the app's settings, go to "Secrets"
   - Add any sensitive environment variables like API keys:
     ```toml
     OPENAI_API_KEY = "sk-..."
     ```

4. **Access Your App**
   - Your app will be available at: `https://YOUR_USERNAME-mvp-agentic-assistant.streamlit.app`
   - Share this URL with others to access your app

---

## Step 3: Alternative: Deploy on Other Platforms

### Option 1: Render
1. Go to https://render.com
2. Create a free account
3. New → Web Service
4. Connect GitHub repository
5. Configure:
   - Build command: `pip install -r requirements.txt`
   - Start command: `streamlit run streamlit_app.py`
6. Deploy

### Option 2: Heroku (Free tier deprecated, use paid)
1. Go to https://www.heroku.com
2. Create app and connect to GitHub
3. Add Procfile with: `web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
4. Deploy

### Option 3: Railway
1. Go to https://railway.app
2. Create new project
3. Connect GitHub repository
4. Railway automatically detects and deploys Python apps
5. Set start command: `streamlit run streamlit_app.py`

---

## Troubleshooting

### If you see "ModuleNotFoundError"
- Ensure `requirements.txt` includes all dependencies
- Check that file imports use correct relative paths
- Streamlit Cloud may need a restart after updating `requirements.txt`

### If LangGraph is not available
- Make sure `langgraph` is in your `requirements.txt`
- Check that `LANGGRAPH_AVAILABLE` flag is set correctly
- The app should fall back gracefully if LangGraph is not installed

### GitHub Authentication Issues
- Use Personal Access Token instead of password
- Ensure token has `repo` scope
- Check that you're in the correct directory before running `git` commands

### Streamlit App Not Loading
- Check the Logs section in Streamlit Cloud dashboard
- Verify `streamlit_app.py` is in the root directory
- Check that all imports are available in `requirements.txt`

---

## Summary of Changes Made

✅ **Removed non-LangGraph components:**
   - `agentic_supervisor.py`
   - `goal_planner.py`
   - `react_agent.py`
   - `reflection.py`
   - `memory.py`

✅ **Updated files:**
   - `src/agentic/__init__.py` - Now only exports LangGraph components
   - `app/streamlit_app.py` - Removed custom agentic supervisor, uses only LangGraph
   - Created `streamlit_app.py` in root for Cloud deployment
   - Created `.streamlit/config.toml` for Streamlit configuration

✅ **Added deployment files:**
   - `.gitignore` - Prevents committing sensitive files
   - `.streamlit/config.toml` - Streamlit Cloud configuration

✅ **Git initialized:**
   - Repository initialized locally
   - Initial commit created with all cleaned-up code

---

## Next Steps

1. **Push to GitHub:**
   ```bash
   cd d:\Learning2\LLMs\mvp_project
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git branch -M main
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud:**
   - Visit https://share.streamlit.io
   - Click "Create app"
   - Select your GitHub repository
   - Deployment will be automatic

3. **Share Your App:**
   - Use the public URL provided by Streamlit Cloud
   - App updates automatically when you push to GitHub

---

## Support

- Streamlit Docs: https://docs.streamlit.io
- GitHub Guides: https://guides.github.com
- LangGraph Docs: https://langchain-ai.github.io/langgraph/
