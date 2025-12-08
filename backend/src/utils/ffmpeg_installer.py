"""
FFmpeg Installer for VideoHub
Automatically download and install ffmpeg if not present
"""

import os
import platform
import shutil
import zipfile
from pathlib import Path
from typing import Optional, Tuple

import requests
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FFmpegInstaller:
    """Handle FFmpeg installation and management"""

    # FFmpeg download URLs (essentials only - ffmpeg and ffprobe)
    FFMPEG_URLS = {
        "Windows": "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
        "Darwin": "https://evermeet.cx/ffmpeg/ffmpeg-6.1.zip",  # macOS
        "Linux": None,  # Use system package manager
    }

    def __init__(self):
        """Initialize FFmpeg installer"""
        self.app_dir = Path.cwd()
        self.ffmpeg_dir = self.app_dir / "ffmpeg" / "bin"
        self.platform = platform.system()

    def is_installed(self) -> bool:
        """
        Check if ffmpeg is already installed

        Returns:
            True if ffmpeg is found (local or system)
        """
        # Check local installation
        if self._check_local_ffmpeg():
            logger.info("FFmpeg found in local directory")
            return True

        # Check system installation
        if self._check_system_ffmpeg():
            logger.info("FFmpeg found in system PATH")
            return True

        return False

    def _check_local_ffmpeg(self) -> bool:
        """Check if ffmpeg exists in local directory"""
        if self.platform == "Windows":
            ffmpeg_exe = self.ffmpeg_dir / "ffmpeg.exe"
        else:
            ffmpeg_exe = self.ffmpeg_dir / "ffmpeg"

        return ffmpeg_exe.exists()

    def _check_system_ffmpeg(self) -> bool:
        """Check if ffmpeg exists in system PATH"""
        return shutil.which("ffmpeg") is not None

    def get_download_url(self) -> Optional[str]:
        """
        Get appropriate download URL for current platform

        Returns:
            Download URL or None if not available
        """
        return self.FFMPEG_URLS.get(self.platform)

    def download_and_install(self, progress_callback=None) -> Tuple[bool, str]:
        """
        Download and install ffmpeg

        Args:
            progress_callback: Optional callback function(current, total, status)

        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if already installed
            if self.is_installed():
                return True, "FFmpeg đã được cài đặt"

            # Get download URL
            url = self.get_download_url()

            if not url:
                if self.platform == "Linux":
                    return (
                        False,
                        "Vui lòng cài ffmpeg qua package manager:\nsudo apt install ffmpeg",
                    )
                return False, f"Không hỗ trợ tự động cài đặt cho {self.platform}"

            logger.info(f"Downloading ffmpeg from {url}")

            # Create temp directory
            temp_dir = self.app_dir / "temp"
            temp_dir.mkdir(exist_ok=True)

            # Download file
            zip_path = temp_dir / "ffmpeg.zip"
            success = self._download_file(url, zip_path, progress_callback)

            if not success:
                return False, "Lỗi tải xuống ffmpeg"

            if progress_callback:
                progress_callback(0, 100, "Đang giải nén...")

            # Extract files
            success = self._extract_ffmpeg(zip_path, progress_callback)

            if not success:
                return False, "Lỗi giải nén ffmpeg"

            # Cleanup
            if zip_path.exists():
                zip_path.unlink()
            if temp_dir.exists() and not list(temp_dir.iterdir()):
                temp_dir.rmdir()

            logger.info("FFmpeg installed successfully")
            return True, "FFmpeg đã được cài đặt thành công"

        except Exception as e:
            logger.error(f"Failed to install ffmpeg: {e}")
            return False, f"Lỗi cài đặt: {str(e)}"

    def _download_file(self, url: str, dest: Path, progress_callback=None) -> bool:
        """
        Download file with progress tracking

        Args:
            url: Download URL
            dest: Destination path
            progress_callback: Progress callback

        Returns:
            True if successful
        """
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(dest, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if progress_callback and total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            progress_callback(
                                downloaded, total_size, f"Đang tải... {percent}%"
                            )

            return True

        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False

    def _extract_ffmpeg(self, zip_path: Path, progress_callback=None) -> bool:
        """
        Extract ffmpeg from zip (only essential files)

        Args:
            zip_path: Path to zip file
            progress_callback: Progress callback

        Returns:
            True if successful
        """
        try:
            # Create ffmpeg directory
            self.ffmpeg_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # Find and extract only ffmpeg and ffprobe executables
                files_to_extract = []

                for file_info in zip_ref.filelist:
                    filename = file_info.filename.lower()

                    # Only extract essential executables (not ffplay)
                    if "ffmpeg.exe" in filename or "ffmpeg" == Path(filename).name:
                        files_to_extract.append(
                            (
                                file_info,
                                "ffmpeg.exe"
                                if self.platform == "Windows"
                                else "ffmpeg",
                            )
                        )
                    elif "ffprobe.exe" in filename or "ffprobe" == Path(filename).name:
                        files_to_extract.append(
                            (
                                file_info,
                                "ffprobe.exe"
                                if self.platform == "Windows"
                                else "ffprobe",
                            )
                        )

                total = len(files_to_extract)

                for idx, (file_info, target_name) in enumerate(files_to_extract, 1):
                    # Extract to temp
                    zip_ref.extract(file_info, self.app_dir / "temp")

                    # Move to ffmpeg/bin with correct name
                    src = self.app_dir / "temp" / file_info.filename
                    dest = self.ffmpeg_dir / target_name

                    if src.exists():
                        shutil.move(str(src), str(dest))

                        # Make executable on Unix-like systems
                        if self.platform != "Windows":
                            os.chmod(dest, 0o755)

                    if progress_callback:
                        percent = int((idx / total) * 100)
                        progress_callback(idx, total, f"Giải nén... {percent}%")

            # Cleanup temp extracted folders
            temp_dir = self.app_dir / "temp"
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

            return True

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return False

    def get_size_info(self) -> str:
        """
        Get size information about installed ffmpeg

        Returns:
            Size string
        """
        if not self._check_local_ffmpeg():
            return "Chưa cài đặt"

        total_size = 0
        for file in self.ffmpeg_dir.iterdir():
            if file.is_file():
                total_size += file.stat().st_size

        # Convert to MB
        size_mb = total_size / (1024 * 1024)
        return f"{size_mb:.1f} MB"

    def add_to_path(self) -> bool:
        """
        Add ffmpeg to PATH environment variable

        Returns:
            True if successful
        """
        try:
            if not self.ffmpeg_dir.exists():
                return False

            ffmpeg_path = str(self.ffmpeg_dir)
            current_path = os.environ.get("PATH", "")

            if ffmpeg_path not in current_path:
                os.environ["PATH"] = ffmpeg_path + os.pathsep + current_path
                logger.info(f"Added ffmpeg to PATH: {ffmpeg_path}")

            return True

        except Exception as e:
            logger.error(f"Failed to add ffmpeg to PATH: {e}")
            return False
