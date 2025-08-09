# Python App Template

This is a template for creating Python applications that can be deployed to Google Cloud Run.

## Supported Frameworks

- **Streamlit**: Interactive data applications
- **Gradio**: Machine learning model interfaces  
- **Dash**: Analytical web applications
- **Flask**: General web applications (default)

## Getting Started

### 1. Copy this template

```bash
cp -r templates/python-app your-app-name
cd your-app-name
```

### 2. Update configuration

1. Edit `src/core/config.py`:
   - Change `APP_NAME` to your app name
   
2. Edit `pyproject.toml`:
   - Update project name and description
   - Uncomment and modify dependencies for your framework

3. Edit `app.py`:
   - Replace with your actual app implementation
   - Uncomment the framework example you want to use

4. Edit `Dockerfile`:
   - Update the CMD instruction for your framework

### 3. Install dependencies

```bash
uv sync
```

### 4. Run locally

```bash
uv run python app.py
```

### 5. Deploy

1. Copy the GitHub Actions workflow template:
   ```bash
   cp .github/workflows/deploy-template.yml .github/workflows/your-app-name.yml
   ```

2. Update the workflow file:
   - Replace `{APP_NAME}` with your app name
   - Replace `{APP_DIRECTORY}` with your directory name

3. Push changes and run the workflow manually from GitHub Actions

## Framework-specific Instructions

### Streamlit
- Uncomment Streamlit dependencies in `pyproject.toml`
- Use the Streamlit example in `app.py`
- Update Dockerfile CMD: `CMD ["uv", "run", "--no-sync", "streamlit", "run", "app.py"]`

### Gradio
- Uncomment Gradio dependencies in `pyproject.toml`  
- Use the Gradio example in `app.py`
- Keep default Dockerfile CMD

### Dash
- Uncomment Dash dependencies in `pyproject.toml`
- Use the Dash example in `app.py` 
- Keep default Dockerfile CMD