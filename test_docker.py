#!/usr/bin/env python3
"""
Quick test script to verify Docker setup works
"""
import subprocess
import sys
import time

def test_docker_build():
    """Test if Docker builds successfully"""
    print("🐳 Testing Docker Build...")
    
    try:
        result = subprocess.run([
            "docker", "build", "-t", "llm-quiz-test", "."
        ], capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ Docker build successful!")
            return True
        else:
            print("❌ Docker build failed:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Docker build timed out (>10 minutes)")
        return False
    except Exception as e:
        print(f"❌ Docker build error: {e}")
        return False

def test_docker_run():
    """Test if Docker container starts properly"""
    print("\n🚀 Testing Docker Run...")
    
    try:
        # Start container in background
        process = subprocess.Popen([
            "docker", "run", "-d", "-p", "5001:5000",
            "-e", "STUDENT_EMAIL=test@example.com",
            "-e", "STUDENT_SECRET=test-secret",
            "-e", "AIPIPE_TOKEN=test-token",
            "--name", "llm-quiz-test-run",
            "llm-quiz-test"
        ], capture_output=True, text=True)
        
        container_id = process.communicate()[0].strip()
        
        if not container_id:
            print("❌ Failed to start container")
            return False
            
        print(f"✅ Container started: {container_id[:12]}...")
        
        # Wait a bit for startup
        print("⏳ Waiting for app to start...")
        time.sleep(10)
        
        # Test health endpoint
        try:
            import requests
            response = requests.get("http://localhost:5001/api/v1/quiz/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health check successful!")
                print(f"📊 Response: {response.json()}")
                success = True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                success = False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            success = False
        
        # Cleanup
        subprocess.run(["docker", "stop", "llm-quiz-test-run"], capture_output=True)
        subprocess.run(["docker", "rm", "llm-quiz-test-run"], capture_output=True)
        
        return success
        
    except Exception as e:
        print(f"❌ Docker run error: {e}")
        # Cleanup attempt
        subprocess.run(["docker", "stop", "llm-quiz-test-run"], capture_output=True)
        subprocess.run(["docker", "rm", "llm-quiz-test-run"], capture_output=True)
        return False

def cleanup():
    """Remove test images"""
    print("\n🧹 Cleaning up test image...")
    subprocess.run(["docker", "rmi", "llm-quiz-test"], capture_output=True)

def main():
    """Main test function"""
    print("🧪 DOCKER SETUP VERIFICATION")
    print("=" * 50)
    
    # Check if Docker is available
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True)
        if result.returncode != 0:
            print("❌ Docker not available. Install Docker to test.")
            return False
    except:
        print("❌ Docker not available. Install Docker to test.")
        return False
    
    build_success = test_docker_build()
    
    if build_success:
        run_success = test_docker_run()
        cleanup()
        
        if run_success:
            print("\n🎉 Docker setup works perfectly!")
            print("✅ Build successful")
            print("✅ Container runs")
            print("✅ Health check passes")
            print("\n📝 Your Docker deployment is ready!")
            return True
        else:
            print("\n⚠️  Docker builds but has runtime issues")
            print("💡 Consider using Render instead - it's much easier!")
            return False
    else:
        print("\n❌ Docker build failed")
        print("💡 Recommendation: Use Render deployment instead")
        print("   It's much simpler and works reliably")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        cleanup()
        sys.exit(1)
