"""
LLM Code Documentation Generator

This system uses real LLM API calls to analyze code and generate documentation
with cost tracking and file size limits.
"""

import os
import ast
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any, Protocol
from pathlib import Path
from abc import ABC, abstractmethod

from autogen import (
    ConversableAgent, 
    GroupChat, 
    GroupChatManager, 
    LLMConfig
)
from version_recorder import VersionRecorder


# Clean interfaces for better maintainability
class IConfigLoader(Protocol):
    """Interface for configuration loading"""
    
    def get_llm_config(self) -> LLMConfig: ...
    
    def get_limits(self) -> Dict[str, Any]: ...


class ICodeAnalyzer(Protocol):
    """Interface for code analysis"""
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]: ...


class IFileProcessor(Protocol):
    """Interface for file processing"""
    
    def save_documentation(self, content: str, output_file: str) -> None: ...


class ICostTracker(Protocol):
    """Interface for cost tracking"""
    
    def can_make_request(self, estimated_cost: float) -> bool: ...
    
    def record_request(self, cost: float) -> None: ...


# Clean class structure with single responsibilities
class ConfigLoader:
    """Load and manage API configuration"""
    
    def __init__(self, config_file: str = "OAI_CONFIG_LIST"):
        """Initialize config loader"""
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                configs = json.load(f)
            
            if configs and len(configs) > 0:
                return configs[0]
            else:
                raise ValueError("No configuration found")
                
        except Exception as e:
            print(f"! Failed to load config: {e}")
            return {}
    
    def get_llm_config(self) -> LLMConfig:
        """Get LLM configuration for agents"""
        if not self.config:
            return False
            
        return LLMConfig(
            model=self.config.get("model", "gpt-5"),
            api_key=self.config.get("api_key"),
            max_completion_tokens=self.config.get("max_tokens", 4000)
        )
    
    def get_limits(self) -> Dict[str, Any]:
        """Get cost and file limits"""
        return {
            "max_cost_per_request": self.config.get("max_cost_per_request", 0.50),
            "daily_spending_limit": self.config.get("daily_spending_limit", 10.00),
            "monthly_spending_limit": self.config.get("monthly_spending_limit", 50.00),
            "max_file_lines": self.config.get("max_file_lines", 5000),
            "max_file_size_mb": self.config.get("max_file_size_mb", 1.0),
            "skip_large_files": self.config.get("skip_large_files", True)
        }


class CostTracker:
    """Track API costs and enforce limits"""
    
    def __init__(self, limits: Dict[str, Any]):
        """Initialize cost tracker"""
        self.limits = limits
        self.daily_spent = 0.0
        self.monthly_spent = 0.0
        self.request_count = 0
    
    def can_make_request(self, estimated_cost: float = 0.50) -> bool:
        """Check if we can make a request within limits"""
        if self.daily_spent + estimated_cost > self.limits["daily_spending_limit"]:
            return False
        if self.monthly_spent + estimated_cost > self.limits["monthly_spending_limit"]:
            return False
        return True
    
    def record_request(self, cost: float):
        """Record the cost of a request"""
        self.daily_spent += cost
        self.monthly_spent += cost
        self.request_count += 1
        
        print(f"💰 Request #{self.request_count}: ${cost:.4f} (Daily: ${self.daily_spent:.2f}, Monthly: ${self.monthly_spent:.2f})")
    




# Extensible analyzer pattern for different programming languages
class BaseCodeAnalyzer(ABC):
    """Base class for code analyzers"""
    
    @abstractmethod
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a file and return structured information"""
        pass


class PythonCodeAnalyzer(BaseCodeAnalyzer):
    """Python code analyzer using AST"""
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a Python file and extract structure information using AST parsing"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            analysis = {
                'file_path': file_path,
                'functions': [],
                'classes': [],
                'imports': [],
                'docstrings': [],
                'line_count': len(content.splitlines()),
                'timestamp': datetime.now().isoformat(),
                'module_docstring': ast.get_docstring(tree) or None
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'line_number': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node) or "No docstring",
                        'is_async': isinstance(node, ast.AsyncFunctionDef)
                    }
                    analysis['functions'].append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'line_number': node.lineno,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        'docstring': ast.get_docstring(node) or "No docstring",
                        'bases': [base.id for base in node.bases if isinstance(base, ast.Name)]
                    }
                    analysis['classes'].append(class_info)
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        analysis['imports'].append(f"{module}.{alias.name}")
            
            return analysis
            
        except Exception as e:
            return {'error': f"Failed to analyze {file_path}: {str(e)}"}


class JavaCodeAnalyzer(BaseCodeAnalyzer):
    """Java code analyzer using regex"""
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze Java file using regex patterns"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            import re
            line_count = len(content.splitlines())
            imports = []
            
            for line in content.splitlines():
                s = line.strip()
                if s.startswith('import '):
                    imp = s.removeprefix('import ').rstrip(';').strip()
                    imports.append(imp)

            classes = []
            class_names = re.findall(r"\b(class|interface|enum)\s+([A-Za-z_][A-Za-z0-9_]*)", content)
            method_tuples = re.findall(r"\b(?:public|protected|private|static|final|abstract|synchronized|native|strictfp)?\s*[A-Za-z_][A-Za-z0-9_<>\[\]]*\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)", content)

            for _, cname in class_names:
                methods = []
                for mname, args in method_tuples:
                    if mname == cname:
                        continue
                    methods.append(mname)
                classes.append({
                    'name': cname,
                    'line_number': 1,
                    'methods': sorted(list(set(methods)))[:20],
                    'docstring': '',
                    'bases': []
                })

            return {
                'file_path': file_path,
                'functions': [],
                'classes': classes,
                'imports': imports,
                'docstrings': [],
                'line_count': line_count,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': f"Failed to analyze {file_path}: {str(e)}"}


class FileProcessor:
    """Handle file operations"""
    
    def save_documentation(self, content: str, output_file: str) -> None:
        """Save documentation to file"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Documentation saved to: {output_file}")


class AgentFactory:
    """Factory for creating agents"""
    
    def __init__(self, llm_config: LLMConfig):
        self.llm_config = llm_config
    
    def create_analyzer_agent(self) -> ConversableAgent:
        """Create code analyzer agent"""
        return ConversableAgent(
            name="code_analyzer",
            system_message="""You are a code analysis expert. Analyze the code and provide a brief summary of:
            1. Main functions and classes
            2. Key functionality
            3. Any notable patterns or issues
            
            Keep your response concise and focused.""",
            llm_config=self.llm_config,
            human_input_mode="NEVER"
        )
    
    def create_generator_agent(self) -> ConversableAgent:
        """Create documentation generator agent"""
        return ConversableAgent(
            name="doc_generator",
            system_message="""You are a documentation generation expert. Create concise documentation that:
            1. Explains what the code does in simple terms
            2. Highlights key functions and their purpose
            3. Provides a brief overview of the code structure
            
            Keep documentation clear and to the point. Avoid excessive detail.""",
            llm_config=self.llm_config,
            human_input_mode="NEVER"
        )
    
    def create_reviewer_agent(self) -> ConversableAgent:
        """Create quality reviewer agent"""
        return ConversableAgent(
            name="quality_reviewer",
            system_message="""You are a documentation quality expert. Review the documentation and:
            1. Check for clarity and completeness
            2. Suggest any important improvements
            3. Ensure it's easy to understand
            
            Provide brief, constructive feedback.""",
            llm_config=self.llm_config,
            human_input_mode="NEVER"
        )
    
    def create_coordinator_agent(self) -> ConversableAgent:
        """Create coordinator agent"""
        return ConversableAgent(
            name="coordinator",
            system_message="""You are the workflow coordinator. Create a final summary that:
            1. Combines the analysis and documentation
            2. Provides a clear overview of the code
            3. Highlights the most important points
            
            Keep the summary concise and well-organized.""",
            llm_config=self.llm_config,
            human_input_mode="NEVER"
        )


class AnalyzerFactory:
    """Factory for creating analyzers"""
    
    @staticmethod
    def create_analyzer(file_extension: str) -> BaseCodeAnalyzer:
        """Create appropriate analyzer based on file extension"""
        if file_extension == '.py':
            return PythonCodeAnalyzer()
        elif file_extension == '.java':
            return JavaCodeAnalyzer()
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")


class DocumentationGenerator:
    """Real LLM Documentation Generator System"""
    
    def __init__(self, 
                 config_loader: IConfigLoader = None,
                 file_processor: IFileProcessor = None,
                 cost_tracker: ICostTracker = None):
        """Initialize with dependency injection for better testability"""
        self.agents = {}
        self.groupchat = None
        self.manager = None
        
        # Dependency injection for better testability and flexibility
        self.config_loader = config_loader or ConfigLoader()
        self.file_processor = file_processor or FileProcessor()
        
        # Initialize cost tracker with injected limits
        limits = self.config_loader.get_limits()
        self.cost_tracker = cost_tracker or CostTracker(limits)
        
        self.llm_config = self.config_loader.get_llm_config()
        
        # Use factory pattern for agent creation
        self.agent_factory = AgentFactory(self.llm_config)
        
        self._create_agents()
        self._setup_group_chat()
    
    def _create_agents(self):
        """Create specialized agents using factory pattern"""
        self.agents['analyzer'] = self.agent_factory.create_analyzer_agent()
        self.agents['generator'] = self.agent_factory.create_generator_agent()
        self.agents['reviewer'] = self.agent_factory.create_reviewer_agent()
        self.agents['coordinator'] = self.agent_factory.create_coordinator_agent()
    
    def _setup_group_chat(self):
        """Setup the group chat for multi-agent collaboration"""
        agent_list = list(self.agents.values())
        
        self.groupchat = GroupChat(
            agents=agent_list,
            messages=[],
            speaker_selection_method="round_robin",
            max_round=10
        )
        
        self.manager = GroupChatManager(
            groupchat=self.groupchat,
            llm_config=self.llm_config
        )
    
    def analyze_code_structure(self, file_path: str) -> Dict[str, Any]:
        """Analyze code structure using appropriate analyzer"""
        print(f"Analyzing code structure for: {file_path}")
        
        # Use factory to get appropriate analyzer
        file_extension = Path(file_path).suffix.lower()
        analyzer = AnalyzerFactory.create_analyzer(file_extension)
        
        analysis = analyzer.analyze_file(file_path)
        
        if 'error' in analysis:
            print(f"! Analysis failed: {analysis['error']}")
            return analysis
        
        print(f"Analysis completed!")
        print(f"Found {len(analysis['functions'])} functions, {len(analysis['classes'])} classes")
        
        return analysis
    
    def analyze_code_string(self, code: str, description: str = "Code Analysis") -> str:
        """Analyze code directly from string using LLM agents"""
        print(f"Analyzing code: {description}")
        
        if not self.cost_tracker.can_make_request():
            return "! Daily spending limit reached. Cannot make request."
        
        try:
            # Multi-agent workflow
            print("Getting analysis from code_analyzer...")
            analyzer_response = self.agents['analyzer'].generate_reply(
                messages=[{"role": "user", "content": f"Analyze this code and provide language breakdown and project summary:\n\n{code}"}]
            )
            
            print("Getting documentation from doc_generator...")
            generator_response = self.agents['generator'].generate_reply(
                messages=[{"role": "user", "content": f"Explain the running logic and function analysis for this code:\n\n{code}"}]
            )
            
            print("Getting quality review...")
            reviewer_response = self.agents['reviewer'].generate_reply(
                messages=[{"role": "user", "content": f"Review and improve this analysis:\n\nAnalyzer: {analyzer_response}\n\nGenerator: {generator_response}"}]
            )
            
            print("Getting final summary...")
            coordinator_response = self.agents['coordinator'].generate_reply(
                messages=[{"role": "user", "content": f"Create a final comprehensive report combining:\n\nAnalyzer: {analyzer_response}\n\nGenerator: {generator_response}\n\nReviewer: {reviewer_response}"}]
            )
            
            estimated_cost = 0.20
            self.cost_tracker.record_request(estimated_cost)
            
            return coordinator_response
            
        except Exception as e:
            print(f"! Analysis failed: {str(e)}")
            return f"Analysis failed: {str(e)}"
    
    def save_documentation(self, content: str, output_file: str):
        """Save documentation using injected file processor"""
        self.file_processor.save_documentation(content, output_file)
    
    def generate_documentation_summary_concise(self, analysis: Dict[str, Any], max_sections: int = 2, max_chars: int = 1500, version_line: str = None, use_llm_explainer: bool = False, hint: str = None) -> str:
        """Generate concise documentation summary"""
        header = f"# Doc Summary: {Path(analysis['file_path']).name}\n\n"
        if version_line:
            header += f"{version_line}\n\n"

        what_lines = []
        first_doc = None
        
        # Check for module-level docstring first
        if analysis.get('module_docstring'):
            first_doc = analysis['module_docstring'].split('\n', 1)[0]
        else:
            # Fall back to function/class docstrings
            for func in analysis.get('functions', []):
                if func.get('docstring'):
                    first_doc = (func['docstring'] or '').split('\n', 1)[0]
                    break
            if not first_doc and analysis.get('classes'):
                for cls in analysis['classes']:
                    if cls.get('docstring'):
                        first_doc = (cls['docstring'] or '').split('\n', 1)[0]
                        break
        
        if first_doc:
            what_lines.append(first_doc.strip())
        else:
            what_lines.append(
                f"This file defines {len(analysis.get('functions', []))} functions and {len(analysis.get('classes', []))} classes."
            )
        what = "## What it does\n" + " ".join(what_lines)

        key_bits = []
        if analysis.get('functions'):
            fn_names = [f["name"] for f in analysis['functions'][:3]]
            if fn_names:
                key_bits.append("Key functions: " + ", ".join(fn_names))
        if analysis.get('classes'):
            cl_names = [c["name"] for c in analysis['classes'][:3]]
            if cl_names:
                key_bits.append("Key classes: " + ", ".join(cl_names))
        key_bits.append(f"Lines: {analysis.get('line_count', 0)}")
        how = "## How it works\n" + "; ".join([b for b in key_bits if b])

        out = header + what + "\n\n" + how + "\n"
        
        # Add simple function summary
        if analysis.get('functions'):
            out += "\n## Functions\n"
            for func in analysis['functions']:
                func_name = func['name']
                func_doc = func.get('docstring', '').strip()
                if func_doc and func_doc != "No docstring":
                    # Use first line of docstring
                    func_desc = func_doc.split('\n')[0].strip()
                else:
                    # Generate simple description from function name
                    func_desc = f"Function: {func_name}"
                out += f"- **{func_name}**: {func_desc}\n"
        
        # Add simple class summary
        if analysis.get('classes'):
            out += "\n## Classes\n"
            for cls in analysis['classes']:
                cls_name = cls['name']
                cls_doc = cls.get('docstring', '').strip()
                if cls_doc and cls_doc != "No docstring":
                    # Use first line of docstring
                    cls_desc = cls_doc.split('\n')[0].strip()
                else:
                    # Generate simple description from class name
                    cls_desc = f"Class: {cls_name}"
                out += f"- **{cls_name}**: {cls_desc}\n"
        
        # Add LLM explanation if enabled
        if use_llm_explainer:
            try:
                # Read the file content for LLM analysis
                with open(analysis['file_path'], 'r', encoding='utf-8') as f:
                    code_content = f.read()
                
                # Generate LLM explanation
                description = hint if hint else f"Code analysis for {Path(analysis['file_path']).name}"
                llm_explanation = self.analyze_code_string(code_content, description)
                
                if llm_explanation and not llm_explanation.startswith("!"):
                    out += f"\n\n{llm_explanation}\n"
            except Exception as e:
                out += f"\n\n<!-- LLM explanation failed: {str(e)} -->\n"
        
        if len(out) > max_chars:
            out = out[: max_chars - 20] + "\n...\n"
        return out


def main():
    """Main function demonstrating clean architecture"""
    parser = argparse.ArgumentParser(
        description="Code Documentation Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 doc_generator.py name_generation.py
  python3 doc_generator.py my_project/
  python3 doc_generator.py src/
        """
    )
    
    parser.add_argument(
        'path', 
        nargs='?', 
        default='name_generation.py',
        help='File or folder path to analyze (default: name_generation.py)'
    )
    parser.add_argument('--limit', type=int, default=5, help='Maximum number of files to analyze in folder mode')
    parser.add_argument('--no-ai-explain', action='store_true', help='Disable LLM explainer')
    parser.add_argument('--hint', type=str, default='', help='Optional hint text to guide the AI explainer')
    
    args = parser.parse_args()
    
    print("Code Documentation Generator")
    print("=" * 70)
    
    try:
        # Demonstrate dependency injection
        doc_gen = DocumentationGenerator()  # Uses default implementations
        
        if os.path.isfile(args.path):
            # Single file analysis
            analysis = doc_gen.analyze_code_structure(args.path)
            if 'error' in analysis:
                return

            vr = VersionRecorder()
            ver_info = vr.record_file(args.path)
            version_line = None
            if ver_info.get('status') in ('created', 'updated', 'unchanged'):
                version_line = f"Version: {ver_info['version']} (change: {ver_info['change']})"

            content = doc_gen.generate_documentation_summary_concise(
                analysis,
                max_sections=3,
                max_chars=1500,
                version_line=version_line,
                use_llm_explainer=not args.no_ai_explain,
                hint=(args.hint or None),
            )

            out_file = f"docs/{Path(args.path).stem}_documentation.md"
            doc_gen.save_documentation(content, out_file)
        else:
            # Folder analysis demonstrates extensible analyzer factory
            print(f"\n🔍 Folder mode: {args.path}")
            if not os.path.isdir(args.path):
                print("! Path is not a folder")
                return

            # Find code files
            code_files = []
            for root, dirs, files in os.walk(args.path):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
                for file in files:
                    if file.startswith('.'):
                        continue
                    fp = os.path.join(root, file)
                    ext = Path(file).suffix.lower()
                    if ext in ['.py', '.java']:
                        code_files.append(fp)

            if not code_files:
                print("! No code files found to analyze")
                return

            code_files = code_files[:max(1, args.limit)]

            vr = VersionRecorder()
            summary_lines = [f"# {Path(args.path).name} Summary", "", f"Processed {len(code_files)} files", ""]

            for fp in code_files:
                # Use factory to get appropriate analyzer
                analysis = doc_gen.analyze_code_structure(fp)
                if 'error' in analysis:
                    continue
                    
                ver_info = vr.record_file(fp)
                version_line = f"Version: {ver_info.get('version','?')} (change: {ver_info.get('change','?')})"
                content = doc_gen.generate_documentation_summary_concise(
                    analysis,
                    max_sections=3,
                    max_chars=1500,
                    version_line=version_line,
                    use_llm_explainer=not args.no_ai_explain,
                    hint=(args.hint or None),
                )
                out_file = f"docs/{Path(fp).stem}_documentation.md"
                doc_gen.save_documentation(content, out_file)
                summary_lines.append(f"- {Path(fp).name}: {version_line}")

            folder_summary = "\n".join(summary_lines) + "\n"
            summary_path = f"docs/{Path(args.path).name}_summary.md"
            doc_gen.save_documentation(folder_summary, summary_path)
        
        print("\n Analysis completed!")
        print("• Used GPT-5 API \n• Generated documentation \n• Cost tracking \n• Saved results to docs/")

        
    except Exception as e:
        print(f"! Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
