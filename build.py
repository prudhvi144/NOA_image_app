#!/usr/bin/env python3
"""
Cross-platform build script for Sperm Verification App
Supports macOS and Windows builds with proper code signing
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def run_command(cmd, shell=False):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=shell, check=True, capture_output=True, text=True)
        print(f"✅ Success: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False, e.stderr

def clean_build():
    """Clean previous build artifacts"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🧹 Cleaned {dir_name}")

def build_app():
    """Build the application using PyInstaller"""
    print("🚀 Starting build process...")
    
    # Clean previous builds
    clean_build()
    
    # Run PyInstaller
    cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'build_config.spec']
    success, output = run_command(cmd)
    
    if not success:
        print("❌ Build failed!")
        return False
    
    print("✅ Build completed successfully!")
    return True

def sign_macos_app():
    """Sign macOS app for Gatekeeper (requires developer certificate)"""
    if platform.system() != 'Darwin':
        print("⏭️  Skipping macOS signing (not on macOS)")
        return True
        
    app_path = Path('dist/SpermVerificationApp.app')
    if not app_path.exists():
        print("❌ App bundle not found for signing")
        return False
    
    print("🔐 Attempting to sign macOS app...")
    
    # Check for available signing identities
    cmd = ['security', 'find-identity', '-v', '-p', 'codesigning']
    success, output = run_command(cmd)
    
    if not success or 'Developer ID Application' not in output:
        print("⚠️  No Developer ID certificate found.")
        print("📝 To pass Gatekeeper, you need:")
        print("   1. Apple Developer Account")
        print("   2. Developer ID Application certificate")
        print("   3. Run: codesign --deep --force --verify --verbose --sign 'Developer ID Application: Your Name' dist/SpermVerificationApp.app")
        return False
    
    # Extract certificate name
    lines = output.split('\n')
    cert_name = None
    for line in lines:
        if 'Developer ID Application' in line:
            start = line.find('"') + 1
            end = line.rfind('"')
            cert_name = line[start:end]
            break
    
    if not cert_name:
        print("❌ Could not find Developer ID certificate")
        return False
    
    # Sign the app
    sign_cmd = [
        'codesign',
        '--deep',
        '--force', 
        '--verify',
        '--verbose',
        '--sign', cert_name,
        '--options', 'runtime',
        str(app_path)
    ]
    
    success, _ = run_command(sign_cmd)
    if success:
        print("✅ App signed successfully!")
        
        # Verify signature
        verify_cmd = ['codesign', '--verify', '--deep', '--strict', str(app_path)]
        verify_success, _ = run_command(verify_cmd)
        if verify_success:
            print("✅ Signature verification passed!")
        else:
            print("⚠️  Signature verification failed")
    
    return success

def create_distribution():
    """Create distribution packages"""
    print("📦 Creating distribution packages...")
    
    if platform.system() == 'Darwin':
        # macOS: Create DMG (optional)
        app_path = Path('dist/SpermVerificationApp.app')
        if app_path.exists():
            print(f"📱 macOS app created: {app_path}")
            print("💡 To create DMG: hdiutil create -volname 'Sperm Verification App' -srcfolder dist/SpermVerificationApp.app -ov -format UDZO SpermVerificationApp.dmg")
    
    elif platform.system() == 'Windows':
        # Windows: Create installer (optional)
        exe_path = Path('dist/SpermVerificationApp/SpermVerificationApp.exe')
        if exe_path.exists():
            print(f"🪟 Windows executable created: {exe_path}")
            print("💡 Consider using NSIS or Inno Setup to create an installer")
    
    return True

def main():
    """Main build process"""
    print("🔨 Sperm Verification App - Build Script")
    print(f"🖥️  Platform: {platform.system()} {platform.machine()}")
    print("=" * 50)
    
    # Build the app
    if not build_app():
        sys.exit(1)
    
    # Sign macOS app if on macOS
    if platform.system() == 'Darwin':
        sign_macos_app()
    
    # Create distribution
    create_distribution()
    
    print("\n🎉 Build process completed!")
    print("\n📁 Output locations:")
    if platform.system() == 'Darwin':
        print("   macOS: dist/SpermVerificationApp.app")
    else:
        print("   Windows: dist/SpermVerificationApp/")

if __name__ == '__main__':
    main()
