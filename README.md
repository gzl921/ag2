# Code Documentation Generator

An AI-powered documentation generator built with the AG2 framework that automatically creates comprehensive documentation for code and tracks version changes.

## Features

- **Multi-Agent System**: Uses AG2 ConversableAgent and GroupChat for collaborative documentation generation
- **Code Analysis**: Supports Python (AST-based) and Java (regex-based) analysis
- **Version Tracking**: Automatic semantic versioning and changelog generation
- **Cost Management**: Built-in API cost tracking and limits
- **Clean Architecture**: Dependency injection, factory patterns, and focused interfaces

## Architecture

### Clean Code Design
The system follows software engineering best practices with clean architecture principles. The codebase uses dependency injection, factory patterns, and focused interfaces to ensure maintainability and testability. Each class has a single responsibility, making the system extensible without modification and allowing for easy testing and future enhancements.

### Multi-Agent Workflow
1. **Code Analyzer Agent** - Analyzes code structure and extracts information
2. **Documentation Generator Agent** - Creates comprehensive documentation
3. **Quality Reviewer Agent** - Reviews and improves documentation quality
4. **Coordinator Agent** - Orchestrates the entire workflow

### Core Components
- **`doc_generator.py`** - Main system implementation
- **`version_recorder.py`** - Per-file version tracking

## Setup

### Prerequisites
- Python 3.10+
- AG2 framework installed
- OpenAI API key (configured in `OAI_CONFIG_LIST`)

### Installation
```bash
# Activate virtual environment
source ag2_env/bin/activate

# Install AG2
pip install 'ag2[openai]'
```

## Usage

### Command Line
```bash
# Analyze single file (use any file from test_samples folder)
python3 doc_generator.py name_generation.py

# Analyze folder (up to 5 files by default)
python3 doc_generator.py test_samples/SolidPrinciples-main/

# Custom options (The system takes the FIRST files it finds adjust limit based on your budget)
python3 doc_generator.py --limit 3 --hint "SOLID principles implementation" test_samples/SolidPrinciples-main/
```

### Programmatic Usage
```python
from doc_generator import DocumentationGenerator

# Initialize system
doc_gen = DocumentationGenerator()

# Analyze file
analysis = doc_gen.analyze_code_structure("path/to/file.py")

# Generate documentation
content = doc_gen.generate_documentation_summary_concise(analysis)
doc_gen.save_documentation(content, "docs/file_documentation.md")
```

## Output

### Generated Documentation
- **Per-file**: Concise Markdown with "What it does" and "How it works" sections
- **Version tracking**: Automatic version bumps and changelog entries
- **Multi-language**: Supports Python and Java code analysis

### Example Output
```markdown
# Doc Summary: name_generation.py

Version: 1.0.0 (change: new)

## What it does
A simple implementation that learns name patterns and generates new names.

## How it works
Key functions: train_model, generate_name, train_model_with_stop_symbol; Lines: 61
```

## AG2 Framework Integration

### Key Concepts Demonstrated
- **ConversableAgent**: Specialized agents with system messages
- **GroupChat**: Multi-agent collaboration and coordination
- **GroupChatManager**: Workflow orchestration
- **Dependency Injection**: Clean, testable architecture
- **Factory Pattern**: Extensible analyzer system

### Agent Configuration
```python
agent = ConversableAgent(
    name="code_analyzer",
    system_message="You are a code analysis expert...",
    llm_config=llm_config,
    human_input_mode="NEVER"
)
```

## Use Cases

- **Development Teams**: Automated documentation for new features
- **Open Source Projects**: Maintain documentation as code evolves
- **Enterprise Development**: Ensure documentation standards compliance
- **Code Review**: Understand changes through generated documentation

## Project Structure

```
ag2/
├── doc_generator.py          # Main implementation
├── version_recorder.py       # Version tracking
├── docs/                     # Generated documentation
├── test_samples/             # Sample code to analyze
└── OAI_CONFIG_LIST          # API configuration
```

## Contributing

This project demonstrates AG2 framework capabilities for building sophisticated multi-agent systems. Key areas for contribution:

- **New Language Support**: Add analyzers for additional programming languages
- **Enhanced Agents**: Create more specialized agents for specific tasks
- **Integration**: Add support for more version control systems
- **Templates**: Create customizable documentation templates

---

*Built with the AG2 framework to showcase practical applications of AI agents in software development workflows.*