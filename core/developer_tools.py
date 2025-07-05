import subprocess
import os
import json
import requests
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import git
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class GitManager:
    """Manages Git operations for development automation"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.repo = None
        try:
            self.repo = git.Repo(self.repo_path)
        except git.exc.InvalidGitRepositoryError:
            pass
    
    def init_repo(self) -> str:
        """Initialize a new Git repository"""
        try:
            self.repo = git.Repo.init(self.repo_path)
            return f"Initialized Git repository in {self.repo_path}"
        except Exception as e:
            return f"Failed to initialize repository: {str(e)}"
    
    def clone_repo(self, url: str, destination: str = None) -> str:
        """Clone a remote repository"""
        try:
            dest_path = destination or self.repo_path
            self.repo = git.Repo.clone_from(url, dest_path)
            return f"Cloned repository from {url} to {dest_path}"
        except Exception as e:
            return f"Failed to clone repository: {str(e)}"
    
    def get_status(self) -> Dict[str, Any]:
        """Get repository status"""
        if not self.repo:
            return {"error": "No Git repository found"}
        
        try:
            return {
                "branch": self.repo.active_branch.name,
                "is_dirty": self.repo.is_dirty(),
                "untracked_files": self.repo.untracked_files,
                "modified_files": [item.a_path for item in self.repo.index.diff(None)],
                "staged_files": [item.a_path for item in self.repo.index.diff("HEAD")],
                "commits_ahead": len(list(self.repo.iter_commits('HEAD..origin/HEAD'))),
                "commits_behind": len(list(self.repo.iter_commits('origin/HEAD..HEAD')))
            }
        except Exception as e:
            return {"error": f"Failed to get status: {str(e)}"}
    
    def add_files(self, files: List[str] = None) -> str:
        """Add files to staging area"""
        if not self.repo:
            return "No Git repository found"
        
        try:
            if files:
                self.repo.index.add(files)
                return f"Added files: {', '.join(files)}"
            else:
                self.repo.git.add(A=True)  # Add all files
                return "Added all files to staging"
        except Exception as e:
            return f"Failed to add files: {str(e)}"
    
    def commit(self, message: str) -> str:
        """Commit staged changes"""
        if not self.repo:
            return "No Git repository found"
        
        try:
            commit = self.repo.index.commit(message)
            return f"Committed changes: {commit.hexsha[:8]} - {message}"
        except Exception as e:
            return f"Failed to commit: {str(e)}"
    
    def push(self, remote: str = "origin", branch: str = None) -> str:
        """Push commits to remote repository"""
        if not self.repo:
            return "No Git repository found"
        
        try:
            branch_name = branch or self.repo.active_branch.name
            self.repo.git.push(remote, branch_name)
            return f"Pushed to {remote}/{branch_name}"
        except Exception as e:
            return f"Failed to push: {str(e)}"
    
    def pull(self, remote: str = "origin", branch: str = None) -> str:
        """Pull changes from remote repository"""
        if not self.repo:
            return "No Git repository found"
        
        try:
            branch_name = branch or self.repo.active_branch.name
            self.repo.git.pull(remote, branch_name)
            return f"Pulled from {remote}/{branch_name}"
        except Exception as e:
            return f"Failed to pull: {str(e)}"
    
    def create_branch(self, branch_name: str, checkout: bool = True) -> str:
        """Create a new branch"""
        if not self.repo:
            return "No Git repository found"
        
        try:
            new_branch = self.repo.create_head(branch_name)
            if checkout:
                new_branch.checkout()
                return f"Created and checked out branch: {branch_name}"
            else:
                return f"Created branch: {branch_name}"
        except Exception as e:
            return f"Failed to create branch: {str(e)}"
    
    def checkout_branch(self, branch_name: str) -> str:
        """Switch to a different branch"""
        if not self.repo:
            return "No Git repository found"
        
        try:
            self.repo.git.checkout(branch_name)
            return f"Switched to branch: {branch_name}"
        except Exception as e:
            return f"Failed to checkout branch: {str(e)}"
    
    def get_commit_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get commit history"""
        if not self.repo:
            return [{"error": "No Git repository found"}]
        
        try:
            commits = []
            for commit in self.repo.iter_commits(max_count=limit):
                commits.append({
                    "hash": commit.hexsha[:8],
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": commit.committed_datetime.isoformat(),
                    "files_changed": len(commit.stats.files)
                })
            return commits
        except Exception as e:
            return [{"error": f"Failed to get commit history: {str(e)}"}]

class DebugHelper:
    """Helps with debugging tasks"""
    
    def __init__(self):
        self.debugger_commands = {
            "python": "python -m pdb",
            "node": "node --inspect",
            "gdb": "gdb"
        }
    
    def analyze_log_file(self, log_path: str, error_patterns: List[str] = None) -> Dict[str, Any]:
        """Analyze log files for errors and patterns"""
        try:
            if not os.path.exists(log_path):
                return {"error": f"Log file {log_path} not found"}
            
            default_patterns = ["error", "exception", "failed", "warning", "critical"]
            patterns = error_patterns or default_patterns
            
            errors = []
            warnings = []
            line_count = 0
            
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line_count = line_num
                    line_lower = line.lower()
                    
                    for pattern in patterns:
                        if pattern in line_lower:
                            entry = {
                                "line_number": line_num,
                                "content": line.strip(),
                                "pattern": pattern
                            }
                            
                            if pattern in ["error", "exception", "failed", "critical"]:
                                errors.append(entry)
                            else:
                                warnings.append(entry)
                            break
            
            return {
                "file": log_path,
                "total_lines": line_count,
                "errors": errors[-20:],  # Last 20 errors
                "warnings": warnings[-20:],  # Last 20 warnings
                "error_count": len(errors),
                "warning_count": len(warnings)
            }
        
        except Exception as e:
            return {"error": f"Failed to analyze log: {str(e)}"}
    
    def check_process_status(self, process_name: str) -> Dict[str, Any]:
        """Check if a process is running and get its info"""
        try:
            import psutil
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if process_name.lower() in proc.info['name'].lower():
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_percent': proc.info['memory_percent'],
                            'status': proc.status()
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                "process_name": process_name,
                "running": len(processes) > 0,
                "instances": processes
            }
        
        except Exception as e:
            return {"error": f"Failed to check process: {str(e)}"}
    
    def profile_code_performance(self, script_path: str, language: str = "python") -> str:
        """Profile code performance"""
        try:
            if language == "python":
                cmd = f"python -m cProfile -s cumulative {script_path}"
            elif language == "node":
                cmd = f"node --prof {script_path}"
            else:
                return f"Profiling not supported for {language}"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            return result.stdout if result.returncode == 0 else result.stderr
        
        except subprocess.TimeoutExpired:
            return "Profiling timed out after 30 seconds"
        except Exception as e:
            return f"Failed to profile code: {str(e)}"

class WebAutomation:
    """Web automation for testing and scraping"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.wait = None
    
    def start_browser(self, browser: str = "chrome") -> str:
        """Start web browser"""
        try:
            if browser == "chrome":
                options = Options()
                if self.headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                
                self.driver = webdriver.Chrome(options=options)
            else:
                return f"Browser {browser} not supported"
            
            self.wait = WebDriverWait(self.driver, 10)
            return "Browser started successfully"
        
        except Exception as e:
            return f"Failed to start browser: {str(e)}"
    
    def navigate_to(self, url: str) -> str:
        """Navigate to a URL"""
        if not self.driver:
            return "Browser not started"
        
        try:
            self.driver.get(url)
            return f"Navigated to {url}"
        except Exception as e:
            return f"Failed to navigate: {str(e)}"
    
    def find_element(self, selector: str, by_type: str = "css") -> Dict[str, Any]:
        """Find element on page"""
        if not self.driver:
            return {"error": "Browser not started"}
        
        try:
            if by_type == "css":
                element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            elif by_type == "id":
                element = self.wait.until(EC.presence_of_element_located((By.ID, selector)))
            elif by_type == "xpath":
                element = self.wait.until(EC.presence_of_element_located((By.XPATH, selector)))
            else:
                return {"error": f"Selector type {by_type} not supported"}
            
            return {
                "found": True,
                "text": element.text,
                "tag": element.tag_name,
                "attributes": {
                    "class": element.get_attribute("class"),
                    "id": element.get_attribute("id")
                }
            }
        
        except Exception as e:
            return {"error": f"Element not found: {str(e)}"}
    
    def click_element(self, selector: str, by_type: str = "css") -> str:
        """Click an element"""
        if not self.driver:
            return "Browser not started"
        
        try:
            if by_type == "css":
                element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            elif by_type == "id":
                element = self.wait.until(EC.element_to_be_clickable((By.ID, selector)))
            elif by_type == "xpath":
                element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            else:
                return f"Selector type {by_type} not supported"
            
            element.click()
            return f"Clicked element: {selector}"
        
        except Exception as e:
            return f"Failed to click element: {str(e)}"
    
    def input_text(self, selector: str, text: str, by_type: str = "css") -> str:
        """Input text into an element"""
        if not self.driver:
            return "Browser not started"
        
        try:
            if by_type == "css":
                element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            elif by_type == "id":
                element = self.wait.until(EC.presence_of_element_located((By.ID, selector)))
            elif by_type == "xpath":
                element = self.wait.until(EC.presence_of_element_located((By.XPATH, selector)))
            else:
                return f"Selector type {by_type} not supported"
            
            element.clear()
            element.send_keys(text)
            return f"Entered text into {selector}"
        
        except Exception as e:
            return f"Failed to input text: {str(e)}"
    
    def get_page_info(self) -> Dict[str, Any]:
        """Get current page information"""
        if not self.driver:
            return {"error": "Browser not started"}
        
        try:
            return {
                "title": self.driver.title,
                "url": self.driver.current_url,
                "page_source_length": len(self.driver.page_source)
            }
        except Exception as e:
            return {"error": f"Failed to get page info: {str(e)}"}
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take a screenshot"""
        if not self.driver:
            return "Browser not started"
        
        try:
            if not filename:
                filename = f"screenshot_{int(time.time())}.png"
            
            self.driver.save_screenshot(filename)
            return f"Screenshot saved as {filename}"
        except Exception as e:
            return f"Failed to take screenshot: {str(e)}"
    
    def close_browser(self) -> str:
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                self.wait = None
                return "Browser closed"
            except Exception as e:
                return f"Failed to close browser: {str(e)}"
        return "Browser was not running"

class DeveloperTools:
    """Central hub for developer automation tools"""
    
    def __init__(self, repo_path: str = "."):
        self.git_manager = GitManager(repo_path)
        self.debug_helper = DebugHelper()
        self.web_automation = WebAutomation()
    
    def run_tests(self, test_framework: str = "pytest", test_path: str = "tests/") -> str:
        """Run tests using specified framework"""
        try:
            frameworks = {
                "pytest": f"python -m pytest {test_path} -v",
                "unittest": f"python -m unittest discover {test_path}",
                "jest": f"npm test",
                "mocha": f"npx mocha {test_path}"
            }
            
            if test_framework not in frameworks:
                return f"Test framework {test_framework} not supported"
            
            result = subprocess.run(
                frameworks[test_framework], 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=120
            )
            
            output = result.stdout + result.stderr
            status = "PASSED" if result.returncode == 0 else "FAILED"
            
            return f"Tests {status}\n\n{output}"
        
        except subprocess.TimeoutExpired:
            return "Tests timed out after 2 minutes"
        except Exception as e:
            return f"Failed to run tests: {str(e)}"
    
    def lint_code(self, language: str = "python", path: str = ".") -> str:
        """Lint code using appropriate linter"""
        try:
            linters = {
                "python": f"python -m flake8 {path}",
                "javascript": f"npx eslint {path}",
                "typescript": f"npx tslint {path}",
                "go": f"golint {path}",
                "rust": f"cargo clippy"
            }
            
            if language not in linters:
                return f"Linter for {language} not configured"
            
            result = subprocess.run(
                linters[language], 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            
            if result.returncode == 0:
                return "No linting issues found"
            else:
                return f"Linting issues found:\n{result.stdout}{result.stderr}"
        
        except subprocess.TimeoutExpired:
            return "Linting timed out after 1 minute"
        except Exception as e:
            return f"Failed to lint code: {str(e)}"
    
    def build_project(self, build_tool: str = "auto", path: str = ".") -> str:
        """Build project using appropriate build tool"""
        try:
            # Auto-detect build tool
            if build_tool == "auto":
                if os.path.exists(os.path.join(path, "package.json")):
                    build_tool = "npm"
                elif os.path.exists(os.path.join(path, "Cargo.toml")):
                    build_tool = "cargo"
                elif os.path.exists(os.path.join(path, "go.mod")):
                    build_tool = "go"
                elif os.path.exists(os.path.join(path, "setup.py")):
                    build_tool = "python"
                else:
                    return "Could not auto-detect build tool"
            
            build_commands = {
                "npm": "npm run build",
                "yarn": "yarn build",
                "cargo": "cargo build",
                "go": "go build",
                "python": "python setup.py build",
                "make": "make"
            }
            
            if build_tool not in build_commands:
                return f"Build tool {build_tool} not supported"
            
            result = subprocess.run(
                build_commands[build_tool],
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
                cwd=path
            )
            
            if result.returncode == 0:
                return f"Build successful using {build_tool}"
            else:
                return f"Build failed:\n{result.stdout}{result.stderr}"
        
        except subprocess.TimeoutExpired:
            return "Build timed out after 5 minutes"
        except Exception as e:
            return f"Failed to build project: {str(e)}"