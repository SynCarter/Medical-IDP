#!/usr/bin/env python3
"""
Quick Setup and Test Script
Validates installation and runs basic tests
"""

import subprocess
import sys
import os


def print_section(title):
    """Print a section header"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70 + "\n")


def check_python_version():
    """Check Python version"""
    print_section("Checking Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    
    print("✅ Python version OK")
    return True


def install_dependencies():
    """Install required packages"""
    print_section("Installing Dependencies")
    
    print("Installing packages... (this may take a few minutes)")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements.txt",
            "--break-system-packages",
            "-q"
        ], check=True)
        
        print("✅ All dependencies installed")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False


def test_imports():
    """Test that all required modules can be imported"""
    print_section("Testing Module Imports")
    
    modules = [
        ('pandas', 'Data processing'),
        ('folium', 'Map visualization'),
        ('streamlit', 'Web interface'),
        ('mlflow', 'Experiment tracking'),
        ('langgraph', 'Agent orchestration'),
        ('pydantic', 'Data validation')
    ]
    
    all_ok = True
    for module, description in modules:
        try:
            __import__(module)
            print(f"✅ {module:20} - {description}")
        except ImportError:
            print(f"❌ {module:20} - {description} (FAILED)")
            all_ok = False
    
    return all_ok


def test_data_loading():
    """Test data loading"""
    print_section("Testing Data Loading")
    
    try:
        from document_parser import parse_facility_dataset
        
        profiles = parse_facility_dataset('ghana_facilities.csv')
        
        if not profiles:
            print("❌ No facilities parsed")
            return False
        
        print(f"✅ Loaded {len(profiles)} facilities")
        print(f"   Sample: {profiles[0].facility_name}")
        print(f"   Capabilities extracted: {len(profiles[0].capabilities)}")
        
        return True
    
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False


def test_agent():
    """Test the AI agent"""
    print_section("Testing AI Agent")
    
    try:
        from document_parser import parse_facility_dataset
        from agentic_planner import HealthcareAgent
        
        profiles = parse_facility_dataset('ghana_facilities.csv')
        agent = HealthcareAgent(profiles)
        
        result = agent.run("Which regions have the highest risk?")
        
        if not result or not result.get('answer'):
            print("❌ Agent failed to generate answer")
            return False
        
        print("✅ Agent successfully processed query")
        print(f"   Generated {len(result.get('recommendations', []))} recommendations")
        print(f"   Reasoning steps: {len(result.get('reasoning_steps', []))}")
        
        return True
    
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualization():
    """Test visualization creation"""
    print_section("Testing Visualization")
    
    try:
        from document_parser import parse_facility_dataset
        from visualization import create_medical_desert_map
        
        profiles = parse_facility_dataset('ghana_facilities.csv')
        map_path = create_medical_desert_map(profiles, '/tmp/test_map.html')
        
        if not os.path.exists(map_path):
            print("❌ Map file not created")
            return False
        
        file_size = os.path.getsize(map_path)
        print(f"✅ Map created successfully")
        print(f"   File: {map_path}")
        print(f"   Size: {file_size:,} bytes")
        
        return True
    
    except Exception as e:
        print(f"❌ Visualization test failed: {e}")
        return False


def run_all_tests():
    """Run all setup and test procedures"""
    print("\n" + "="*70)
    print(" 🏥 MEDICAL DESERT INTELLIGENCE SYSTEM")
    print(" Setup and Validation Script")
    print("="*70)
    
    tests = [
        ("Python Version", check_python_version),
        ("Dependencies", install_dependencies),
        ("Module Imports", test_imports),
        ("Data Loading", test_data_loading),
        ("AI Agent", test_agent),
        ("Visualization", test_visualization)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print_section("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} - {test_name}")
    
    print(f"\n{'='*70}")
    print(f" Results: {passed}/{total} tests passed")
    print(f"{'='*70}\n")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("  1. Run full analysis:    python main.py analyze")
        print("  2. Launch web interface: python main.py web")
        print("  3. Read documentation:   README.md")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("   Try running: pip install -r requirements.txt --break-system-packages")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
