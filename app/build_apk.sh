#!/bin/bash

###############################################################################
# FLUTTER APK BUILD SCRIPT - TRAFFIC SHARE
# 100% Working Build Script
###############################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Functions
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

###############################################################################
# 1. PREREQUISITES CHECK
###############################################################################

print_header "1. PREREQUISITES CHECK"

# Check Flutter
if ! command -v flutter &> /dev/null; then
    print_error "Flutter not found"
    print_info "Install Flutter: https://flutter.dev/docs/get-started/install"
    exit 1
fi

FLUTTER_VERSION=$(flutter --version | head -n 1)
print_success "Flutter: $FLUTTER_VERSION"

# Check Java
if ! command -v java &> /dev/null; then
    print_error "Java not found"
    print_info "Install Java JDK 11+"
    exit 1
fi

JAVA_VERSION=$(java -version 2>&1 | head -n 1)
print_success "Java: $JAVA_VERSION"

# Check Android SDK
if [[ -z "$ANDROID_HOME" ]]; then
    print_warning "ANDROID_HOME not set"
else
    print_success "Android SDK: $ANDROID_HOME"
fi

###############################################################################
# 2. PROJECT SETUP
###############################################################################

print_header "2. PROJECT SETUP"

# Check if pubspec.yaml exists
if [[ ! -f "pubspec.yaml" ]]; then
    print_error "pubspec.yaml not found"
    print_info "Run this script from the Flutter project root directory"
    exit 1
fi

print_success "Project directory: $(pwd)"

###############################################################################
# 3. CLEAN BUILD
###############################################################################

print_header "3. CLEAN BUILD"

print_info "Cleaning previous build..."
flutter clean
print_success "Clean complete"

###############################################################################
# 4. GET DEPENDENCIES
###############################################################################

print_header "4. GET DEPENDENCIES"

print_info "Fetching dependencies..."
flutter pub get
print_success "Dependencies fetched"

###############################################################################
# 5. CODE GENERATION (if needed)
###############################################################################

print_header "5. CODE GENERATION"

if grep -q "build_runner" pubspec.yaml; then
    print_info "Running build_runner..."
    flutter pub run build_runner build --delete-conflicting-outputs
    print_success "Code generation complete"
else
    print_info "No code generation needed"
fi

###############################################################################
# 6. ANALYZE CODE
###############################################################################

print_header "6. CODE ANALYSIS"

print_info "Analyzing code..."
if flutter analyze --no-pub; then
    print_success "No analysis issues found"
else
    print_warning "Analysis found some issues (continuing anyway)"
fi

###############################################################################
# 7. BUILD APK
###############################################################################

print_header "7. BUILD APK"

BUILD_TYPE=${1:-release}

if [[ "$BUILD_TYPE" == "debug" ]]; then
    print_info "Building DEBUG APK..."
    flutter build apk --debug
    APK_PATH="build/app/outputs/flutter-apk/app-debug.apk"
elif [[ "$BUILD_TYPE" == "split" ]]; then
    print_info "Building SPLIT APKs (per ABI)..."
    flutter build apk --split-per-abi --release
    APK_PATH="build/app/outputs/flutter-apk/"
else
    print_info "Building RELEASE APK..."
    flutter build apk --release
    APK_PATH="build/app/outputs/flutter-apk/app-release.apk"
fi

if [[ $? -eq 0 ]]; then
    print_success "Build successful!"
else
    print_error "Build failed"
    exit 1
fi

###############################################################################
# 8. APK INFO
###############################################################################

print_header "8. BUILD OUTPUT"

echo ""
if [[ "$BUILD_TYPE" == "split" ]]; then
    echo "APK files:"
    ls -lh build/app/outputs/flutter-apk/*.apk | awk '{print "  "$9" ("$5")"}'
else
    if [[ -f "$APK_PATH" ]]; then
        APK_SIZE=$(ls -lh "$APK_PATH" | awk '{print $5}')
        echo "APK file: $APK_PATH"
        echo "Size: $APK_SIZE"
    fi
fi
echo ""

###############################################################################
# 9. VERIFICATION
###############################################################################

print_header "9. VERIFICATION"

if [[ "$BUILD_TYPE" == "split" ]]; then
    APK_COUNT=$(ls build/app/outputs/flutter-apk/*.apk 2>/dev/null | wc -l)
    if [[ $APK_COUNT -gt 0 ]]; then
        print_success "Generated $APK_COUNT APK files"
    else
        print_error "No APK files found"
        exit 1
    fi
else
    if [[ -f "$APK_PATH" ]]; then
        print_success "APK file exists"
        
        # Check APK signature (release only)
        if [[ "$BUILD_TYPE" == "release" ]]; then
            if command -v apksigner &> /dev/null; then
                if apksigner verify "$APK_PATH" 2>&1 | grep -q "Verified"; then
                    print_success "APK signature verified"
                else
                    print_warning "APK signature verification failed"
                fi
            fi
        fi
    else
        print_error "APK file not found"
        exit 1
    fi
fi

###############################################################################
# 10. INSTALL (optional)
###############################################################################

print_header "10. INSTALL TO DEVICE"

# Check if device connected
if adb devices | grep -q "device$"; then
    print_info "Android device detected"
    
    read -p "Install APK to device? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ "$BUILD_TYPE" == "split" ]]; then
            print_info "Installing split APKs..."
            flutter install
        else
            print_info "Installing APK..."
            adb install -r "$APK_PATH"
        fi
        
        if [[ $? -eq 0 ]]; then
            print_success "App installed successfully"
        else
            print_error "Installation failed"
        fi
    fi
else
    print_info "No Android device connected"
fi

###############################################################################
# SUMMARY
###############################################################################

print_header "BUILD COMPLETE"

echo ""
print_success "APK build successful! 🎉"
echo ""

if [[ "$BUILD_TYPE" == "split" ]]; then
    echo "Output directory:"
    echo "  build/app/outputs/flutter-apk/"
    echo ""
    echo "APK files:"
    ls -1 build/app/outputs/flutter-apk/*.apk | sed 's/^/  /'
else
    echo "APK location:"
    echo "  $APK_PATH"
    echo ""
    echo "File size:"
    echo "  $(ls -lh "$APK_PATH" | awk '{print $5}')"
fi

echo ""
echo "Next steps:"
echo "  1. Test the APK on a device"
echo "  2. Upload to your server or distribution platform"
echo "  3. Share with users"
echo ""

print_success "Done! 🚀"
