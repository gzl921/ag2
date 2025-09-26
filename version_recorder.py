#!/usr/bin/env python3
"""
Per-file semantic version recorder using AST-based change detection.

Persists versions in docs/.versions.json and appends brief entries to docs/CHANGELOG.md.
"""

import ast
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple
import re


def _get_function_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args = []
    for arg in node.args.args:
        args.append(arg.arg)
    if node.args.vararg:
        args.append("*" + node.args.vararg.arg)
    for kw in node.args.kwonlyargs:
        args.append(kw.arg + "=")
    if node.args.kwarg:
        args.append("**" + node.args.kwarg.arg)
    returns = ast.unparse(node.returns) if getattr(node, "returns", None) is not None else ""
    return f"def {node.name}({','.join(args)})->{returns}"


def _get_class_signature(node: ast.ClassDef) -> str:
    bases = ",".join([ast.unparse(b) for b in node.bases]) if node.bases else ""
    method_sigs: list[str] = []
    for n in node.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            method_sigs.append(_get_function_signature(n))
    method_sigs.sort()
    return f"class {node.name}({bases}){{{';'.join(method_sigs)}}}"


def compute_ast_signatures(content: str) -> Tuple[str, str]:
    """Return (semantic_hash_str, docs_hash_str) canonical strings.

    semantic_hash_str excludes docstrings; docs_hash_str includes only docstrings for
    functions/classes/module to allow patch-only detection.
    """
    tree = ast.parse(content)

    semantic_parts: list[str] = []
    docs_parts: list[str] = []

    # Module docstring
    module_doc = ast.get_docstring(tree) or ""
    docs_parts.append(f"module:{module_doc}")

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if not node.name.startswith("_"):
                semantic_parts.append(_get_function_signature(node))
                docs_parts.append(f"func:{node.name}:{ast.get_docstring(node) or ''}")
        elif isinstance(node, ast.ClassDef):
            if not node.name.startswith("_"):
                semantic_parts.append(_get_class_signature(node))
                docs_parts.append(f"class:{node.name}:{ast.get_docstring(node) or ''}")

    semantic_parts.sort()
    docs_parts.sort()
    return ("\n".join(semantic_parts), "\n".join(docs_parts))


def compute_java_signatures(content: str) -> Tuple[str, str]:
    """Very lightweight Java signature extraction (best-effort, not a full parser)."""
    semantic_parts: list[str] = []
    docs_parts: list[str] = []

    # imports
    # classes/interfaces/enums
    class_names = re.findall(r"\b(class|interface|enum)\s+([A-Za-z_][A-Za-z0-9_]*)", content)
    for _, cname in class_names:
        # collect methods within file (coarse; not scoped per class)
        method_names = re.findall(r"\b(?:public|protected|private|static|final|abstract|synchronized|native|strictfp)?\s*[A-Za-z_][A-Za-z0-9_<>\[\]]*\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)", content)
        # Filter out constructors (method name equals class name)
        method_sigs: list[str] = []
        for mname, args in method_names:
            if mname == cname:
                continue
            # Normalize args to names count only
            arg_count = 0 if args.strip() == "" else len([a for a in args.split(',') if a.strip()])
            method_sigs.append(f"def {mname}({arg_count} args)")
        method_sigs = sorted(set(method_sigs))
        semantic_parts.append(f"class {cname}{{{';'.join(method_sigs)}}}")

    semantic_parts.sort()
    return ("\n".join(semantic_parts), "")


def compute_signatures_for_file(file_path: str, content: str) -> Tuple[str, str]:
    if file_path.endswith('.py'):
        return compute_ast_signatures(content)
    if file_path.endswith('.java'):
        return compute_java_signatures(content)
    # Fallback: use a simple line-hash approximation (names only)
    names = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", content)
    return (" ".join(sorted(set(names))[:2000]), "")


class VersionRecorder:
    def __init__(self, versions_path: str = "docs/.versions.json", changelog_path: str = "docs/CHANGELOG.md"):
        self.versions_path = versions_path
        self.changelog_path = changelog_path
        self.store: Dict[str, Any] = self._load_store()

    def _load_store(self) -> Dict[str, Any]:
        if os.path.exists(self.versions_path):
            try:
                with open(self.versions_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {"files": {}}
        return {"files": {}}

    def _save_store(self) -> None:
        os.makedirs(os.path.dirname(self.versions_path), exist_ok=True)
        with open(self.versions_path, "w", encoding="utf-8") as f:
            json.dump(self.store, f, indent=2)

    @staticmethod
    def _parse_version(v: str) -> Tuple[int, int, int]:
        try:
            major, minor, patch = [int(x) for x in v.split(".")]
            return major, minor, patch
        except Exception:
            return 1, 0, 0

    @staticmethod
    def _format_version(t: Tuple[int, int, int]) -> str:
        return f"{t[0]}.{t[1]}.{t[2]}"

    def _bump(self, current: str, level: str) -> str:
        major, minor, patch = self._parse_version(current)
        if level == "major":
            major += 1; minor = 0; patch = 0
        elif level == "minor":
            minor += 1; patch = 0
        elif level == "patch":
            patch += 1
        return self._format_version((major, minor, patch))

    def record_file(self, file_path: str) -> Dict[str, Any]:
        """Compute signatures, compare with store, decide bump level, persist, and return summary.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return {"file": file_path, "status": "error", "message": str(e)}
        #Extract code signatures (functions, classes, docstrings)
        semantic_str, docs_str = compute_signatures_for_file(file_path, content)

        files = self.store.setdefault("files", {})
        prev = files.get(file_path)

        ts = datetime.now().isoformat()
        if not prev:
            # First time seen
            files[file_path] = {
                "version": "1.0.0",
                "semantic": semantic_str,
                "docs": docs_str,
                "last_changed": ts,
            }
            self._save_store()
            return {"file": file_path, "status": "created", "version": "1.0.0", "change": "new"}

        prev_sem = prev.get("semantic", "")
        prev_docs = prev.get("docs", "")
        current_version = prev.get("version", "1.0.0")

        #Compare with previous version
        if semantic_str != prev_sem:
            #Determine change level: major/minor/patch
            # Determine breaking vs additive (approximation via arity change)
            level = "minor"
            # crude check: if function list counts changed treat as minor; if same names but different signatures, treat as major
            prev_funcs = [l for l in prev_sem.split("\n") if l.startswith("def ")]
            cur_funcs = [l for l in semantic_str.split("\n") if l.startswith("def ")]
            if len(prev_funcs) == len(cur_funcs):
                # compare name->sig mapping
                def map_funcs(lst: list[str]) -> Dict[str, str]:
                    m: Dict[str, str] = {}
                    for s in lst:
                        name = s[4:s.find("(")]
                        m[name] = s
                    return m
                mp = map_funcs(prev_funcs)
                mc = map_funcs(cur_funcs)
                shared = set(mp.keys()).intersection(mc.keys())
                for n in shared:
                    if mp[n] != mc[n]:
                        level = "major"
                        break
            new_version = self._bump(current_version, level)
            #Update version and changelog
            files[file_path] = {"version": new_version, "semantic": semantic_str, "docs": docs_str, "last_changed": ts}
            self._save_store()
            self._append_changelog(file_path, current_version, new_version, level)
            return {"file": file_path, "status": "updated", "version": new_version, "change": level}

        if docs_str != prev_docs:
            new_version = self._bump(current_version, "patch")
            files[file_path] = {"version": new_version, "semantic": semantic_str, "docs": docs_str, "last_changed": ts}
            self._save_store()
            self._append_changelog(file_path, current_version, new_version, "patch")
            return {"file": file_path, "status": "updated", "version": new_version, "change": "patch"}

        # No semantic nor docs change
        return {"file": file_path, "status": "unchanged", "version": current_version, "change": "none"}

    def _append_changelog(self, file_path: str, old: str, new: str, level: str) -> None:
        os.makedirs(os.path.dirname(self.changelog_path), exist_ok=True)
        line = f"- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {file_path}: {old} → {new} ({level})\n"
        if not os.path.exists(self.changelog_path):
            with open(self.changelog_path, "w", encoding="utf-8") as f:
                f.write("# Changelog\n\n")
                f.write(line)
        else:
            with open(self.changelog_path, "a", encoding="utf-8") as f:
                f.write(line)


