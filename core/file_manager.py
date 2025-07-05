import os
import shutil
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

class FileManager:
    """Handles file and document management operations"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.home()
        self.allowed_extensions = {
            'documents': ['.txt', '.doc', '.docx', '.pdf', '.odt', '.rtf'],
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg'],
            'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'code': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.c', '.php']
        }
    
    def list_files(self, directory: str = None, pattern: str = None) -> List[Dict[str, Any]]:
        """List files in a directory with metadata"""
        try:
            target_dir = Path(directory) if directory else self.base_path
            if not target_dir.exists():
                return [{"error": f"Directory {target_dir} does not exist"}]
            
            files = []
            for item in target_dir.iterdir():
                try:
                    if pattern and pattern.lower() not in item.name.lower():
                        continue
                    
                    stat = item.stat()
                    file_info = {
                        "name": item.name,
                        "path": str(item),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "is_directory": item.is_dir(),
                        "extension": item.suffix,
                        "type": self._get_file_type(item)
                    }
                    files.append(file_info)
                except (PermissionError, OSError):
                    continue
            
            return sorted(files, key=lambda x: x['modified'], reverse=True)
        except Exception as e:
            return [{"error": f"Failed to list files: {str(e)}"}]
    
    def create_file(self, file_path: str, content: str = "") -> str:
        """Create a new file with optional content"""
        try:
            target_path = Path(file_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"File created: {target_path}"
        except Exception as e:
            return f"Failed to create file: {str(e)}"
    
    def read_file(self, file_path: str) -> str:
        """Read content of a text file"""
        try:
            target_path = Path(file_path)
            if not target_path.exists():
                return f"File {file_path} does not exist"
            
            if target_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
                return self._extract_text_from_image(str(target_path))
            elif target_path.suffix.lower() == '.pdf':
                return self._extract_text_from_pdf(str(target_path))
            else:
                with open(target_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            return f"Failed to read file: {str(e)}"
    
    def write_file(self, file_path: str, content: str, append: bool = False) -> str:
        """Write content to a file"""
        try:
            target_path = Path(file_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'a' if append else 'w'
            with open(target_path, mode, encoding='utf-8') as f:
                f.write(content)
            
            action = "appended to" if append else "written to"
            return f"Content {action} {target_path}"
        except Exception as e:
            return f"Failed to write file: {str(e)}"
    
    def delete_file(self, file_path: str) -> str:
        """Delete a file or directory"""
        try:
            target_path = Path(file_path)
            if not target_path.exists():
                return f"File {file_path} does not exist"
            
            if target_path.is_dir():
                shutil.rmtree(target_path)
                return f"Directory deleted: {target_path}"
            else:
                target_path.unlink()
                return f"File deleted: {target_path}"
        except Exception as e:
            return f"Failed to delete: {str(e)}"
    
    def copy_file(self, source: str, destination: str) -> str:
        """Copy a file or directory"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                return f"Source {source} does not exist"
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if source_path.is_dir():
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                return f"Directory copied: {source_path} -> {dest_path}"
            else:
                shutil.copy2(source_path, dest_path)
                return f"File copied: {source_path} -> {dest_path}"
        except Exception as e:
            return f"Failed to copy: {str(e)}"
    
    def move_file(self, source: str, destination: str) -> str:
        """Move/rename a file or directory"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                return f"Source {source} does not exist"
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_path), str(dest_path))
            
            return f"Moved: {source_path} -> {dest_path}"
        except Exception as e:
            return f"Failed to move: {str(e)}"
    
    def create_directory(self, directory_path: str) -> str:
        """Create a new directory"""
        try:
            target_path = Path(directory_path)
            target_path.mkdir(parents=True, exist_ok=True)
            return f"Directory created: {target_path}"
        except Exception as e:
            return f"Failed to create directory: {str(e)}"
    
    def search_files(self, query: str, directory: str = None, extension: str = None) -> List[Dict[str, Any]]:
        """Search for files by name or content"""
        try:
            target_dir = Path(directory) if directory else self.base_path
            results = []
            
            for file_path in target_dir.rglob("*"):
                try:
                    if file_path.is_file():
                        # Check file name
                        if query.lower() in file_path.name.lower():
                            results.append({
                                "path": str(file_path),
                                "name": file_path.name,
                                "match_type": "filename",
                                "size": file_path.stat().st_size
                            })
                        
                        # Check extension filter
                        if extension and not file_path.suffix.lower() == extension.lower():
                            continue
                        
                        # Search content for text files
                        if file_path.suffix.lower() in ['.txt', '.py', '.js', '.html', '.css', '.md', '.json', '.xml']:
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    if query.lower() in content.lower():
                                        results.append({
                                            "path": str(file_path),
                                            "name": file_path.name,
                                            "match_type": "content",
                                            "size": file_path.stat().st_size
                                        })
                            except (UnicodeDecodeError, PermissionError):
                                continue
                
                except (PermissionError, OSError):
                    continue
            
            return results[:50]  # Limit results
        except Exception as e:
            return [{"error": f"Search failed: {str(e)}"}]
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get detailed information about a file"""
        try:
            target_path = Path(file_path)
            if not target_path.exists():
                return {"error": f"File {file_path} does not exist"}
            
            stat = target_path.stat()
            mime_type, _ = mimetypes.guess_type(str(target_path))
            
            return {
                "name": target_path.name,
                "path": str(target_path),
                "size": stat.st_size,
                "size_human": self._format_size(stat.st_size),
                "extension": target_path.suffix,
                "mime_type": mime_type,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "is_directory": target_path.is_dir(),
                "permissions": oct(stat.st_mode)[-3:],
                "type": self._get_file_type(target_path)
            }
        except Exception as e:
            return {"error": f"Failed to get file info: {str(e)}"}
    
    def _extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using OCR (placeholder for now)"""
        try:
            # This would require pytesseract and PIL
            # For now, return a placeholder
            return f"OCR text extraction not implemented yet for {image_path}"
        except Exception as e:
            return f"Failed to extract text from image: {str(e)}"
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF (placeholder for now)"""
        try:
            # This would require PyPDF2 or pdfplumber
            # For now, return a placeholder
            return f"PDF text extraction not implemented yet for {pdf_path}"
        except Exception as e:
            return f"Failed to extract text from PDF: {str(e)}"
    
    def _get_file_type(self, file_path: Path) -> str:
        """Determine file type category"""
        extension = file_path.suffix.lower()
        
        for category, extensions in self.allowed_extensions.items():
            if extension in extensions:
                return category
        
        return "other"
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"