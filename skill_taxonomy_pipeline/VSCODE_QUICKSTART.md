# VS Code Quick Start Guide

## 📋 Prerequisites

- Python 3.8 or higher
- VS Code installed
- Git (optional but recommended)
- 16GB+ RAM for processing 200K skills

## 🚀 Quick Setup (5 minutes)

### 1. Open in VS Code

```bash
# Clone or download the project
cd skill_taxonomy_pipeline
code .  # Opens in VS Code
```

### 2. Install VS Code Extensions

When VS Code opens, you'll see a popup asking to install recommended extensions. Click **"Install All"**.

Or manually install these essential extensions:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Jupyter (ms-toolsai.jupyter)

### 3. Set Up Python Environment

**Option A: Using the terminal in VS Code** (Ctrl+` or Cmd+`):

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**Option B: Using Make** (if you have Make installed):

```bash
make setup
```

### 4. Select Python Interpreter in VS Code

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Python: Select Interpreter"
3. Choose the interpreter from `./venv/bin/python`

### 5. Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your OpenAI API key (optional)
# The pipeline works without it but won't have LLM features
```

## 🎯 Running the Pipeline in VS Code

### Method 1: Using the Debug Panel (Recommended)

1. Click the **Run and Debug** icon in the sidebar (or press `Ctrl+Shift+D`)
2. Select **"Run Pipeline - Sample"** from the dropdown
3. Click the green play button or press `F5`

The pipeline will run with sample data and you can set breakpoints for debugging.

### Method 2: Using the Terminal

```bash
# Run with sample data
python example_usage.py

# Run with your data
python run_pipeline.py data/your_skills.csv -o output/results

# Run with specific options
python run_pipeline.py data/skills.csv --sample 1000 --skip-llm
```

### Method 3: Using Make Commands

```bash
# Run sample pipeline
make run

# Run tests
make test

# Format code
make format

# Clean outputs
make clean
```

## 🔍 VS Code Features for This Project

### 1. IntelliSense and Auto-completion

- Hover over any function for documentation
- Press `Ctrl+Space` for suggestions
- `F12` to go to definition
- `Shift+F12` to find all references

### 2. Debugging

Set breakpoints by clicking left of line numbers, then:
1. Press `F5` to start debugging
2. Use debug console to inspect variables
3. Step through code with `F10` (step over) or `F11` (step into)

### 3. Running Tests

- Open any test file in `tests/` folder
- Click "Run Test" above test functions
- Or use Test Explorer in the sidebar

### 4. Jupyter Notebooks

- Open any `.ipynb` file in `notebooks/` folder
- VS Code will open it as an interactive notebook
- Run cells with `Shift+Enter`

## 📁 Project Structure in VS Code

```
Key folders to know:
├── src/              # Main source code - your pipeline logic
├── config/           # Configuration files
├── data/sample/      # Sample data for testing
├── output/           # Where results are saved
├── notebooks/        # Jupyter notebooks for exploration
└── tests/           # Test files
```

## 🎨 VS Code Workspace Settings

The project includes optimized VS Code settings:

- **Auto-formatting** on save (using Black)
- **Linting** with Pylint
- **Type checking** with Pylance
- **Test discovery** with pytest
- **Git integration** for version control

## 🐛 Common Issues and Solutions

### Issue 1: "No module named 'src'"

**Solution**: Make sure you've selected the correct Python interpreter (from venv)

### Issue 2: "Import could not be resolved"

**Solution**: 
1. Restart VS Code
2. Ensure venv is activated
3. Check that PYTHONPATH includes the project root

### Issue 3: Memory errors with large datasets

**Solution**: Adjust batch size in config:
```python
# In config/settings.py
DATA_CONFIG = {
    "batch_size": 500,  # Reduce this
}
```

### Issue 4: Slow processing

**Solution**: Use GPU if available:
```bash
# Set in .env file
USE_GPU=1

# Or in command line
python run_pipeline.py data/skills.csv --use-gpu
```

## 📊 Monitoring Progress

1. **Watch logs in real-time**:
   - Terminal: `tail -f taxonomy_pipeline.log`
   - Or use Output panel in VS Code

2. **Check memory usage**:
   - Use Task Manager (Windows) or Activity Monitor (Mac)
   - Or install the "Resource Monitor" VS Code extension

3. **Progress bars**:
   - The pipeline shows progress bars for long operations
   - Check the terminal for current status

## 🎓 Learning Resources

### In VS Code:
- **Hover** over any function for documentation
- **Ctrl+Click** on imports to see source code
- Check `example_usage.py` for usage patterns

### Project Documentation:
- `README.md` - Overall project guide
- `docs/` folder - Detailed documentation
- Inline comments in code

## 💡 Tips for Large Datasets (200K skills)

1. **Start small**: Test with 1000 skills first
   ```bash
   python run_pipeline.py data/skills.csv --sample 1000
   ```

2. **Use caching**: The pipeline caches embeddings automatically

3. **Monitor resources**: Keep Task Manager open

4. **Run overnight**: Full 200K processing takes 1-3 hours

5. **Save intermediate results**: Results are saved at each step

## 🚀 Next Steps

1. **Explore the sample notebook**:
   - Open `notebooks/01_data_exploration.ipynb`
   - Run cells to understand the data flow

2. **Customize configuration**:
   - Edit `config/settings.py` for your needs
   - Adjust clustering parameters based on your data

3. **Run with your data**:
   - Place your CSV in `data/` folder
   - Ensure it has all required columns
   - Run: `python run_pipeline.py data/your_file.csv`

## 🆘 Getting Help

- **IntelliSense issues**: Reload VS Code window (`Ctrl+Shift+P` → "Reload Window")
- **Python issues**: Check Python version (`python --version`)
- **Memory issues**: Reduce batch sizes or sample size
- **Speed issues**: Enable GPU or reduce UMAP components

---

**Ready to process 200K skills?** Start with a sample, validate results, then run the full dataset! 🎯
