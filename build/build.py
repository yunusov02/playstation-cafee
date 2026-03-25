"""
Build script for PlayStation Cafe Manager
"""
import os
import sys
import shutil
import subprocess
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
        for pycache in self.project_root.rglob("__pycache__"):
            shutil.rmtree(pycache)
        
        self.print_success("Cleanup complete")
        
    def check_dependencies(self):
        """Check if all dependencies are installed"""
        self.print_step("Checking dependencies...")
        
        required = {
            'PyQt6': 'PyQt6.QtWidgets',
            'SQLAlchemy': 'sqlalchemy', 
            'PyInstaller': 'PyInstaller'
        }
        
        missing = []
        
        for package_name, import_name in required.items():
            try:
                __import__(import_name)
                print(f"   ✓ {package_name}")
            except ImportError:
                print(f"   ✗ {package_name}")
                missing.append(package_name)
        
        if missing:
            self.print_error(f"Missing packages: {', '.join(missing)}")
            print("\nInstall with: pip install " + " ".join(missing))
            return False
        
        self.print_success("All dependencies installed")
        return True
        
    def create_icon(self):
        """Create or verify icon exists"""
        self.print_step("Checking icon...")
        
        if ICON_FILE.exists():
            self.print_success(f"Icon found: {ICON_FILE.name}")
            return True
        else:
            print(f"   ⚠️  Icon not found: {ICON_FILE}")
            print("   Creating placeholder icon...")
            
            # Create a simple icon using PIL if available
            try:
                from PIL import Image, ImageDraw
                
                # Create a simple icon
                img = Image.new('RGB', (256, 256), color='#2196F3')
                draw = ImageDraw.Draw(img)
                draw.text((80, 120), "PS", fill='white')
                
                # Save as .ico
                ICON_FILE.parent.mkdir(exist_ok=True)
                img.save(ICON_FILE, format='ICO', sizes=[(256, 256)])
                
                self.print_success("Created placeholder icon")
                return True
            except ImportError:
                print("   ⚠️  PIL not installed, building without icon")
                print("   Install with: pip install Pillow")
                return False
                
    def create_version_file(self):
        """Create version info file for Windows"""
        self.print_step("Creating version info...")
        
        version_file = self.build_dir / "version_info.txt"
        
        version_info = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({APP_VERSION.replace('.', ', ')}, 0),
    prodvers=({APP_VERSION.replace('.', ', ')}, 0),
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
        StringStruct(u'OriginalFilename', u'PlayStationCafeManager.exe'),
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
        
    def build_executable(self):
        """Build the executable using PyInstaller"""
        self.print_step("Building executable...")
        
        # Prepare PyInstaller command
        cmd = [
            'pyinstaller',
            '--name=PlayStationCafeManager',
            '--onefile' if ONE_FILE else '--onedir',
            '--noconfirm',
            '--clean',
        ]
        
        # Add windowed mode (no console)
        if not CONSOLE:
            cmd.append('--windowed')
        
        # Add icon if it exists
        if ICON_FILE.exists():
            cmd.append(f'--icon={ICON_FILE}')
        
        # Add data files
        for src, dest in INCLUDE_FILES:
            cmd.append(f'--add-data={src}{os.pathsep}{dest}')
        
        # Add hidden imports
        for imp in HIDDEN_IMPORTS:
            cmd.append(f'--hidden-import={imp}')
        
        # Add excludes
        for exc in EXCLUDES:
            cmd.append(f'--exclude-module={exc}')
        
        # UPX compression
        if UPX:
            cmd.append('--upx-dir=upx')
        
        # Dist and build paths
        cmd.append(f'--distpath={self.dist_dir}')
        cmd.append(f'--workpath={self.build_dir}/build')
        cmd.append(f'--specpath={self.build_dir}')
        
        # Main script
        cmd.append(str(MAIN_SCRIPT))
        
        # Print command
        print("\n   Command:")
        print(f"   {' '.join(cmd)}\n")
        
        # Run PyInstaller
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.print_success("Build successful!")
                return True
            else:
                self.print_error("Build failed!")
                print("\nError output:")
                print(result.stderr)
                return False
                
        except Exception as e:
            self.print_error(f"Build error: {e}")
            return False
            
    def create_distribution_package(self):
        """Create a distribution package with all necessary files"""
        self.print_step("Creating distribution package...")
        
        # Create distribution folder
        pkg_name = f"PlayStation_Cafe_v{APP_VERSION}"
        pkg_dir = self.dist_dir / pkg_name
        pkg_dir.mkdir(exist_ok=True)
        
        # Copy executable
        exe_name = "PlayStationCafeManager.exe" if sys.platform == "win32" else "PlayStationCafeManager"
        
        if ONE_FILE:
            src_exe = self.dist_dir / exe_name
            if src_exe.exists():
                shutil.copy(src_exe, pkg_dir / exe_name)
                print(f"   ✓ Copied {exe_name}")
        else:
            src_dir = self.dist_dir / "PlayStationCafeManager"
            if src_dir.exists():
                shutil.copytree(src_dir, pkg_dir / "PlayStationCafeManager")
                print(f"   ✓ Copied application folder")
        
        # Copy README
        readme_src = self.project_root / "README.md"
        if readme_src.exists():
            shutil.copy(readme_src, pkg_dir / "README.txt")
            print("   ✓ Copied README")
        
        # Create installation instructions
        install_instructions = f"""
╔══════════════════════════════════════════════════════════════╗
║                 PlayStation Cafe Manager                      ║
║                      Version {APP_VERSION}                           ║
╚══════════════════════════════════════════════════════════════╝

📦 INSTALLATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Extract this folder to your desired location
2. Run PlayStationCafeManager.exe
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
Email: support@yourcompany.com
Website: https://yourwebsite.com

Built with ❤️ for PlayStation Cafe Management
"""
        
        (pkg_dir / "INSTALL.txt").write_text(install_instructions, encoding='utf-8')
        print("   ✓ Created INSTALL.txt")
        
        # Create a simple launcher script (for folder distribution)
        if not ONE_FILE:
            launcher = f"""@echo off
title {APP_NAME}
cd /d "%~dp0"
start PlayStationCafeManager\\PlayStationCafeManager.exe
"""
            (pkg_dir / "Launch.bat").write_text(launcher)
            print("   ✓ Created Launch.bat")
        
        self.print_success(f"Distribution package created: {pkg_name}")
        return pkg_dir
        
    def create_portable_zip(self, pkg_dir):
        """Create a portable ZIP file"""
        self.print_step("Creating portable ZIP...")
        
        zip_name = f"{pkg_dir.name}_Portable"
        zip_path = self.dist_dir / zip_name
        
        try:
            shutil.make_archive(
                str(zip_path),
                'zip',
                pkg_dir.parent,
                pkg_dir.name
            )
            
            zip_file = Path(str(zip_path) + '.zip')
            size_mb = zip_file.stat().st_size / (1024 * 1024)
            
            self.print_success(f"ZIP created: {zip_file.name} ({size_mb:.2f} MB)")
            return True
            
        except Exception as e:
            self.print_error(f"Failed to create ZIP: {e}")
            return False
            
    def print_summary(self):
        """Print build summary"""
        self.print_header("BUILD SUMMARY")
        
        print(f"\n📦 Application: {APP_NAME}")
        print(f"📌 Version: {APP_VERSION}")
        print(f"🕒 Build Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Find built files
        exe_name = "PlayStationCafeManager.exe" if sys.platform == "win32" else "PlayStationCafeManager"
        exe_path = self.dist_dir / exe_name
        
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n📂 Executable: {exe_path.relative_to(self.project_root)}")
            print(f"💾 Size: {size_mb:.2f} MB")
        
        # Find ZIP
        for zip_file in self.dist_dir.glob("*.zip"):
            size_mb = zip_file.stat().st_size / (1024 * 1024)
            print(f"\n📦 Package: {zip_file.relative_to(self.project_root)}")
            print(f"💾 Size: {size_mb:.2f} MB")
        
        print("\n" + "=" * 60)
        
    def build(self):
        """Main build process"""
        self.print_header(f"Building {APP_NAME} v{APP_VERSION}")
        
        # Step 1: Clean
        self.clean_build()
        
        # Step 2: Check dependencies
        if not self.check_dependencies():
            return False
        
        # Step 3: Create/check icon
        self.create_icon()
        
        # Step 4: Create version info
        self.create_version_file()
        
        # Step 5: Build executable
        if not self.build_executable():
            return False
        
        # Step 6: Create distribution package
        pkg_dir = self.create_distribution_package()
        
        # Step 7: Create portable ZIP
        self.create_portable_zip(pkg_dir)
        
        # Step 8: Print summary
        self.print_summary()
        
        print("\n✨ Build completed successfully!\n")
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