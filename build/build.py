"""
Build script for PlayStation Cafe Manager
Cross-platform support: Windows, Linux, macOS
"""
import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from build.build_config import *


class PSCafeBuilder:
    """Build manager for PlayStation Cafe application"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.build_dir = BUILD_DIR
        self.dist_dir = DIST_DIR
        self.platform = platform.system()  # 'Windows', 'Linux', 'Darwin'
        self.arch = platform.machine()  # 'x86_64', 'AMD64', 'arm64', etc.
        
        # Platform-specific settings
        self.exe_extension = '.exe' if self.platform == 'Windows' else ''
        self.exe_name = f"PlayStationCafeManager{self.exe_extension}"
        self.path_separator = ';' if self.platform == 'Windows' else ':'
        
        # Icon files per platform
        self.icon_extensions = {
            'Windows': '.ico',
            'Linux': '.png',
            'Darwin': '.icns'  # macOS
        }
        
    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60)
        
    def print_step(self, text):
        """Print step information"""
        print(f"\n🔹 {text}")
        
    def print_success(self, text):
        """Print success message"""
        print(f"✅ {text}")
        
    def print_error(self, text):
        """Print error message"""
        print(f"❌ {text}")
        
    def print_warning(self, text):
        """Print warning message"""
        print(f"⚠️  {text}")
        
    def print_info(self, text):
        """Print info message"""
        print(f"ℹ️  {text}")
        
    def get_platform_info(self):
        """Get and display platform information"""
        self.print_step("Detecting platform...")
        
        print(f"   OS: {self.platform}")
        print(f"   Architecture: {self.arch}")
        print(f"   Python: {platform.python_version()}")
        print(f"   Executable format: {self.exe_name}")
        
        # Platform-specific notes
        if self.platform == 'Linux':
            self.print_info("Building for Linux - output will be an executable binary")
        elif self.platform == 'Windows':
            self.print_info("Building for Windows - output will be .exe file")
        elif self.platform == 'Darwin':
            self.print_info("Building for macOS - output will be .app bundle")
        
        return True
        
    def clean_build(self):
        """Clean previous build artifacts"""
        self.print_step("Cleaning previous builds...")
        
        # Directories to clean
        clean_dirs = [
            self.build_dir / "dist",
            self.build_dir / "build",
            self.dist_dir,
        ]
        
        for dir_path in clean_dirs:
            if dir_path.exists() and dir_path != self.build_dir:
                shutil.rmtree(dir_path)
                print(f"   Removed: {dir_path.relative_to(self.project_root)}")
        
        # Remove .spec files
        for spec_file in self.build_dir.glob("*.spec"):
            spec_file.unlink()
            print(f"   Removed: {spec_file.name}")
        
        # Clean __pycache__
        pycache_count = 0
        for pycache in self.project_root.rglob("__pycache__"):
            shutil.rmtree(pycache)
            pycache_count += 1
        
        if pycache_count > 0:
            print(f"   Removed: {pycache_count} __pycache__ directories")
        
        self.print_success("Cleanup complete")
        
    def check_dependencies(self):
        """Check if all dependencies are installed"""
        self.print_step("Checking dependencies...")
        
        # Map display name to actual import name
        required = {
            'PyQt6': 'PyQt6.QtWidgets',
            'SQLAlchemy': 'sqlalchemy',
            'PyInstaller': 'PyInstaller'
        }
        
        missing = []
        installed_versions = {}
        
        for display_name, import_name in required.items():
            try:
                module = __import__(import_name)
                # Try to get version
                try:
                    if hasattr(module, '__version__'):
                        version = module.__version__
                    elif hasattr(module, 'version'):
                        version = module.version
                    else:
                        version = "installed"
                except:
                    version = "installed"
                
                installed_versions[display_name] = version
                print(f"   ✓ {display_name} ({version})")
            except ImportError:
                print(f"   ✗ {display_name}")
                missing.append(display_name.lower())
        
        if missing:
            self.print_error(f"Missing packages: {', '.join(missing)}")
            print("\nInstall with: pip install " + " ".join(missing))
            return False
        
        # Check for conflicting Qt bindings
        self.print_step("Checking for Qt conflicts...")
        try:
            __import__('PyQt5')
            self.print_warning("PyQt5 is also installed - will be excluded from build")
        except ImportError:
            print("   ✓ No conflicting Qt bindings found")
        
        self.print_success("All dependencies ready")
        return True
        
    def create_icon(self):
        """Create or verify icon exists for current platform"""
        self.print_step("Checking icon...")
        
        icon_ext = self.icon_extensions.get(self.platform, '.png')
        icon_file = RESOURCES_DIR / f"icon{icon_ext}"
        
        # Also check for .ico as fallback
        if not icon_file.exists() and icon_ext != '.ico':
            icon_file = RESOURCES_DIR / "icon.ico"
        
        if icon_file.exists():
            self.print_success(f"Icon found: {icon_file.name}")
            return icon_file
        else:
            print(f"   ⚠️  Icon not found: {icon_file}")
            print("   Creating placeholder icon...")
            
            # Create a simple icon using PIL if available
            try:
                from PIL import Image, ImageDraw, ImageFont
                
                # Create a simple icon
                size = 256
                img = Image.new('RGB', (size, size), color='#2196F3')
                draw = ImageDraw.Draw(img)
                
                # Try to add text
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
                except:
                    try:
                        font = ImageFont.truetype("arial.ttf", 80)
                    except:
                        font = ImageFont.load_default()
                
                # Draw "PS" text
                text = "PS"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                position = ((size - text_width) // 2, (size - text_height) // 2 - 20)
                draw.text(position, text, fill='white', font=font)
                
                # Save based on platform
                RESOURCES_DIR.mkdir(exist_ok=True)
                
                if self.platform == 'Windows':
                    icon_file = RESOURCES_DIR / "icon.ico"
                    img.save(icon_file, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
                elif self.platform == 'Darwin':
                    icon_file = RESOURCES_DIR / "icon.icns"
                    # For macOS, save as PNG first (would need iconutil to create .icns)
                    png_file = RESOURCES_DIR / "icon.png"
                    img.save(png_file, 'PNG')
                    icon_file = png_file  # Use PNG as fallback
                    self.print_warning("Created PNG icon (use iconutil to create .icns for macOS)")
                else:  # Linux
                    icon_file = RESOURCES_DIR / "icon.png"
                    img.save(icon_file, 'PNG')
                
                self.print_success(f"Created icon: {icon_file.name}")
                return icon_file
                
            except ImportError:
                self.print_warning("PIL not installed, building without icon")
                print("   Install with: pip install Pillow")
                return None
                
    def create_version_file(self):
        """Create version info file for Windows"""
        if self.platform != 'Windows':
            print("   Skipping version info (Windows only)")
            return None
            
        self.print_step("Creating version info...")
        
        version_file = self.build_dir / "version_info.txt"
        
        # Parse version
        version_parts = APP_VERSION.split('.')
        while len(version_parts) < 4:
            version_parts.append('0')
        version_tuple = ', '.join(version_parts[:4])
        
        version_info = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_tuple}),
    prodvers=({version_tuple}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{APP_AUTHOR}'),
        StringStruct(u'FileDescription', u'{APP_DESCRIPTION}'),
        StringStruct(u'FileVersion', u'{APP_VERSION}'),
        StringStruct(u'InternalName', u'{APP_NAME}'),
        StringStruct(u'LegalCopyright', u'Copyright © 2024 {APP_AUTHOR}'),
        StringStruct(u'OriginalFilename', u'{self.exe_name}'),
        StringStruct(u'ProductName', u'{APP_NAME}'),
        StringStruct(u'ProductVersion', u'{APP_VERSION}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
        
        version_file.write_text(version_info)
        self.print_success("Version info created")
        return version_file
        
    def build_executable(self, icon_file=None):
        """Build the executable using PyInstaller"""
        self.print_step(f"Building executable for {self.platform}...")
        
        # Prepare PyInstaller command
        cmd = [
            sys.executable, '-m', 'PyInstaller',  # Use python -m PyInstaller for reliability
            '--name=PlayStationCafeManager',
            '--noconfirm',
            '--clean',
        ]
        
        # One file or one directory
        if ONE_FILE:
            cmd.append('--onefile')
        else:
            cmd.append('--onedir')
        
        # Add windowed mode (no console)
        if not CONSOLE:
            cmd.append('--windowed')
        
        # Add icon if it exists
        if icon_file and icon_file.exists():
            cmd.append(f'--icon={icon_file}')
        
        # Add data files with platform-specific separator
        for src, dest in INCLUDE_FILES:
            cmd.append(f'--add-data={src}{self.path_separator}{dest}')
        
        # Add hidden imports
        for imp in HIDDEN_IMPORTS:
            cmd.append(f'--hidden-import={imp}')
        
        # Add excludes - IMPORTANT: Exclude PyQt5 to avoid conflicts
        excludes = list(EXCLUDES)
        # Always exclude PyQt5 when building with PyQt6
        pyqt5_excludes = [
            'PyQt5',
            'PyQt5.QtCore',
            'PyQt5.QtGui', 
            'PyQt5.QtWidgets',
            'PyQt5.QtNetwork',
            'PyQt5.QtMultimedia',
            'PyQt5.Qt',
            'PyQt5.Qt5',
        ]
        excludes.extend(pyqt5_excludes)
        
        for exc in excludes:
            cmd.append(f'--exclude-module={exc}')
        
        # Platform-specific options
        if self.platform == 'Darwin':
            # macOS specific
            cmd.append(f'--osx-bundle-identifier={APP_IDENTIFIER}')
        
        # UPX compression (if available)
        if UPX:
            upx_dir = self.build_dir / 'upx'
            if upx_dir.exists():
                cmd.append(f'--upx-dir={upx_dir}')
        
        # Dist and build paths
        cmd.append(f'--distpath={self.dist_dir}')
        cmd.append(f'--workpath={self.build_dir}/build')
        cmd.append(f'--specpath={self.build_dir}')
        
        # Log level
        cmd.append('--log-level=WARN')
        
        # Main script
        cmd.append(str(MAIN_SCRIPT))
        
        # Print command
        print("\n   Command:")
        cmd_str = ' '.join(cmd)
        # Print in multiple lines for readability
        print(f"   {cmd_str[:80]}...")
        print()
        
        # Run PyInstaller
        try:
            print("   Building... (this may take a few minutes)")
            print("   " + "-" * 50)
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                # Don't capture output - let it print in real-time
            )
            
            print("   " + "-" * 50)
            
            if result.returncode == 0:
                self.print_success("Build successful!")
                return True
            else:
                self.print_error("Build failed!")
                return False
                
        except FileNotFoundError:
            self.print_error("PyInstaller not found. Install with: pip install pyinstaller")
            return False
        except Exception as e:
            self.print_error(f"Build error: {e}")
            return False
            
    def verify_build(self):
        """Verify the build was successful"""
        self.print_step("Verifying build...")
        
        exe_path = self.dist_dir / self.exe_name
        
        if not exe_path.exists():
            # Check for folder build
            folder_path = self.dist_dir / "PlayStationCafeManager"
            if folder_path.exists():
                exe_in_folder = folder_path / self.exe_name
                if exe_in_folder.exists():
                    exe_path = exe_in_folder
                    self.print_success(f"Found executable in folder: {exe_in_folder.name}")
                    return exe_path
        
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            self.print_success(f"Executable verified: {exe_path.name} ({size_mb:.2f} MB)")
            return exe_path
        else:
            self.print_error(f"Executable not found: {exe_path}")
            return None
            
    def create_distribution_package(self, exe_path):
        """Create a distribution package with all necessary files"""
        self.print_step("Creating distribution package...")
        
        # Create distribution folder with platform suffix
        platform_suffix = {
            'Windows': 'Win64',
            'Linux': 'Linux64',
            'Darwin': 'macOS'
        }.get(self.platform, self.platform)
        
        pkg_name = f"PlayStation_Cafe_v{APP_VERSION}_{platform_suffix}"
        pkg_dir = self.dist_dir / pkg_name
        pkg_dir.mkdir(exist_ok=True)
        
        # Copy executable
        if ONE_FILE:
            if exe_path and exe_path.exists():
                shutil.copy(exe_path, pkg_dir / self.exe_name)
                print(f"   ✓ Copied {self.exe_name}")
        else:
            src_dir = self.dist_dir / "PlayStationCafeManager"
            if src_dir.exists():
                dest_dir = pkg_dir / "PlayStationCafeManager"
                shutil.copytree(src_dir, dest_dir)
                print(f"   ✓ Copied application folder")
        
        # Copy README
        readme_src = self.project_root / "README.md"
        if readme_src.exists():
            shutil.copy(readme_src, pkg_dir / "README.txt")
            print("   ✓ Copied README")
        
        # Create platform-specific installation instructions
        if self.platform == 'Linux':
            install_instructions = self._get_linux_instructions()
        elif self.platform == 'Darwin':
            install_instructions = self._get_macos_instructions()
        else:
            install_instructions = self._get_windows_instructions()
        
        (pkg_dir / "INSTALL.txt").write_text(install_instructions, encoding='utf-8')
        print("   ✓ Created INSTALL.txt")
        
        # Create launcher scripts
        if self.platform == 'Linux':
            self._create_linux_launcher(pkg_dir)
        elif self.platform == 'Windows' and not ONE_FILE:
            self._create_windows_launcher(pkg_dir)
        elif self.platform == 'Darwin':
            self._create_macos_launcher(pkg_dir)
        
        # Create .desktop file for Linux
        if self.platform == 'Linux':
            self._create_desktop_file(pkg_dir)
        
        self.print_success(f"Distribution package created: {pkg_name}")
        return pkg_dir
    
    def _get_linux_instructions(self):
        """Get Linux-specific installation instructions"""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                 PlayStation Cafe Manager                      ║
║                      Version {APP_VERSION}                           ║
║                         Linux                                 ║
╚══════════════════════════════════════════════════════════════╝

📦 INSTALLATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Extract this archive to your desired location:
   tar -xzf PlayStation_Cafe_v{APP_VERSION}_Linux64.tar.gz

2. Make the file executable:
   chmod +x PlayStationCafeManager

3. Run the application:
   ./PlayStationCafeManager

   OR use the launcher script:
   ./run.sh

📋 OPTIONAL: Create Desktop Shortcut
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Copy the .desktop file to your applications folder:
   cp playstation-cafe.desktop ~/.local/share/applications/

🔐 DEFAULT LOGIN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Username: admin
Password: admin123

⚠️  IMPORTANT: Change the default password after first login!

🐧 LINUX NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• The database (playstation_cafe.db) is created in the same
  directory as the executable
• Make sure you have write permissions in the directory
• For system-wide installation, copy to /opt/ or /usr/local/bin/

🆘 TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If the app doesn't start:
1. Check permissions: chmod +x PlayStationCafeManager
2. Run from terminal to see errors: ./PlayStationCafeManager
3. Install required libraries:
   sudo apt install libxcb-xinerama0 libxcb-cursor0  # Ubuntu/Debian
   sudo dnf install libxcb                           # Fedora

🆘 SUPPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For support or questions:
Email: englishisakovich@gmail.com

Built with ❤️ for Amir Arena Management
"""

    def _get_macos_instructions(self):
        """Get macOS-specific installation instructions"""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                 PlayStation Cafe Manager                      ║
║                      Version {APP_VERSION}                           ║
║                        macOS                                  ║
╚══════════════════════════════════════════════════════════════╝

📦 INSTALLATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Extract this archive
2. Drag PlayStationCafeManager to your Applications folder
3. Double-click to run

⚠️  FIRST RUN (Gatekeeper)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If macOS blocks the app:
1. Right-click the app and select "Open"
2. Click "Open" in the dialog
3. Or go to System Preferences → Security & Privacy → "Open Anyway"

🔐 DEFAULT LOGIN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Username: admin
Password: admin123

⚠️  IMPORTANT: Change the default password after first login!

🆘 SUPPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For support or questions:
Email: englishisakovich@gmail.com

Built with ❤️ for Amir Arena Management
"""

    def _get_windows_instructions(self):
        """Get Windows-specific installation instructions"""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                 PlayStation Cafe Manager                      ║
║                      Version {APP_VERSION}                           ║
║                       Windows                                 ║
╚══════════════════════════════════════════════════════════════╝

📦 INSTALLATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Extract this folder to your desired location
2. Double-click PlayStationCafeManager.exe to run
3. The application will automatically:
   • Create the database
   • Set up sample data
   • Create the default admin account

🔐 DEFAULT LOGIN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Username: admin
Password: admin123

⚠️  IMPORTANT: Change the default password after first login!

🚀 QUICK START
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Login with default credentials
2. Go to Management → Add your PlayStations
3. Go to Management → Add your Joysticks
4. Start managing sessions from the Dashboard

📋 FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Real-time session monitoring
✓ Dynamic joystick management
✓ Multiple payment methods (Cash/Terminal/Hybrid)
✓ Comprehensive reports (Daily/Weekly/Monthly/Custom)
✓ User management
✓ Dark mode support
✓ Sound notifications

💡 TIPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• The database file (playstation_cafe.db) will be created
  in the same folder as the executable
• Back up the database regularly
• Use Management tab to configure prices
• Check Reports tab for business insights

🆘 SUPPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For support or questions:
Email: englishisakovich@gmail.com

Built with ❤️ for Amir Arena Management
"""

    def _create_linux_launcher(self, pkg_dir):
        """Create Linux launcher script"""
        launcher_content = f"""#!/bin/bash
# PlayStation Cafe Manager Launcher

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
cd "$SCRIPT_DIR"

# Make executable if needed
chmod +x PlayStationCafeManager 2>/dev/null

# Run the application
./PlayStationCafeManager "$@"
"""
        launcher_path = pkg_dir / "run.sh"
        launcher_path.write_text(launcher_content)
        launcher_path.chmod(0o755)
        print("   ✓ Created run.sh launcher")
        
    def _create_windows_launcher(self, pkg_dir):
        """Create Windows launcher script"""
        launcher_content = f"""@echo off
title {APP_NAME}
cd /d "%~dp0"
start "" "PlayStationCafeManager\\PlayStationCafeManager.exe"
"""
        launcher_path = pkg_dir / "Launch.bat"
        launcher_path.write_text(launcher_content)
        print("   ✓ Created Launch.bat")
        
    def _create_macos_launcher(self, pkg_dir):
        """Create macOS launcher script"""
        launcher_content = f"""#!/bin/bash
# PlayStation Cafe Manager Launcher

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Run the application
./PlayStationCafeManager "$@"
"""
        launcher_path = pkg_dir / "run.command"
        launcher_path.write_text(launcher_content)
        launcher_path.chmod(0o755)
        print("   ✓ Created run.command launcher")
        
    def _create_desktop_file(self, pkg_dir):
        """Create Linux .desktop file"""
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={APP_NAME}
Comment={APP_DESCRIPTION}
Exec={pkg_dir}/PlayStationCafeManager
Icon={pkg_dir}/resources/icon.png
Terminal=false
Categories=Office;Utility;
StartupWMClass=PlayStationCafeManager
"""
        desktop_path = pkg_dir / "playstation-cafe.desktop"
        desktop_path.write_text(desktop_content)
        print("   ✓ Created playstation-cafe.desktop")
        
    def create_portable_archive(self, pkg_dir):
        """Create a portable archive file"""
        self.print_step("Creating portable archive...")
        
        archive_name = pkg_dir.name
        archive_path = self.dist_dir / archive_name
        
        try:
            if self.platform == 'Windows':
                # Create ZIP for Windows
                shutil.make_archive(
                    str(archive_path),
                    'zip',
                    pkg_dir.parent,
                    pkg_dir.name
                )
                archive_file = Path(str(archive_path) + '.zip')
                archive_type = "ZIP"
            else:
                # Create tar.gz for Linux/macOS
                shutil.make_archive(
                    str(archive_path),
                    'gztar',
                    pkg_dir.parent,
                    pkg_dir.name
                )
                archive_file = Path(str(archive_path) + '.tar.gz')
                archive_type = "TAR.GZ"
            
            if archive_file.exists():
                size_mb = archive_file.stat().st_size / (1024 * 1024)
                self.print_success(f"{archive_type} created: {archive_file.name} ({size_mb:.2f} MB)")
                return archive_file
            else:
                self.print_error("Archive file not created")
                return None
            
        except Exception as e:
            self.print_error(f"Failed to create archive: {e}")
            return None
            
    def print_summary(self, exe_path=None, archive_path=None):
        """Print build summary"""
        self.print_header("BUILD SUMMARY")
        
        print(f"\n📦 Application: {APP_NAME}")
        print(f"📌 Version: {APP_VERSION}")
        print(f"💻 Platform: {self.platform} ({self.arch})")
        print(f"🕒 Build Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Find built files
        if exe_path and exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n📂 Executable: {exe_path.relative_to(self.project_root)}")
            print(f"💾 Size: {size_mb:.2f} MB")
        
        # Archive
        if archive_path and archive_path.exists():
            size_mb = archive_path.stat().st_size / (1024 * 1024)
            print(f"\n📦 Archive: {archive_path.relative_to(self.project_root)}")
            print(f"💾 Size: {size_mb:.2f} MB")
        
        # Distribution folder
        for dist_folder in self.dist_dir.glob("PlayStation_Cafe_*"):
            if dist_folder.is_dir():
                print(f"\n📁 Distribution: {dist_folder.relative_to(self.project_root)}")
        
        print("\n" + "=" * 60)
        
        # Platform-specific run instructions
        print("\n🚀 TO RUN THE APPLICATION:")
        if self.platform == 'Windows':
            print(f"   dist\\{self.exe_name}")
        elif self.platform == 'Linux':
            print(f"   chmod +x dist/{self.exe_name}")
            print(f"   ./dist/{self.exe_name}")
        else:  # macOS
            print(f"   open dist/{self.exe_name}")
        
        print()
        
    def build(self):
        """Main build process"""
        self.print_header(f"Building {APP_NAME} v{APP_VERSION}")
        
        # Step 1: Platform info
        self.get_platform_info()
        
        # Step 2: Clean
        self.clean_build()
        
        # Step 3: Check dependencies
        if not self.check_dependencies():
            return False
        
        # Step 4: Create/check icon
        icon_file = self.create_icon()
        
        # Step 5: Create version info (Windows only)
        self.create_version_file()
        
        # Step 6: Build executable
        if not self.build_executable(icon_file):
            return False
        
        # Step 7: Verify build
        exe_path = self.verify_build()
        if not exe_path:
            return False
        
        # Step 8: Create distribution package
        pkg_dir = self.create_distribution_package(exe_path)
        
        # Step 9: Create portable archive
        archive_path = self.create_portable_archive(pkg_dir)
        
        # Step 10: Print summary
        self.print_summary(exe_path, archive_path)
        
        print("✨ Build completed successfully!\n")
        return True


def main():
    """Entry point"""
    builder = PSCafeBuilder()
    
    try:
        success = builder.build()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Build failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()