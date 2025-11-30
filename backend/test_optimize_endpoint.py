"""Test the optimization API endpoint."""
import sys
sys.path.insert(0, ".")

import requests
import json

# Test data
test_code = "result := 5 + 3.14;"

def test_optimize_endpoint():
    """Test the /api/optimize endpoint."""
    url = "http://localhost:8000/api/optimize"
    
    payload = {
        "source_code": test_code
    }
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✓ API Response successful")
            print(f"\nOriginal instructions ({len(data['original_instructions'])}):")
            for i, instr in enumerate(data['original_instructions']):
                print(f"  {i+1}. {instr['instruction']}")
            
            print(f"\nOptimized instructions ({len(data['optimized_instructions'])}):")
            for i, instr in enumerate(data['optimized_instructions']):
                print(f"  {i+1}. {instr['instruction']}")
            
            print(f"\nOptimization Statistics:")
            stats = data['stats']
            print(f"  - Instructions saved: {stats['instructions_saved']}")
            print(f"  - Reduction: {stats['reduction_percentage']:.1f}%")
            print(f"  - int2float inlined: {stats['int2float_inlined']}")
            print(f"  - Temps eliminated: {stats['temps_eliminated']}")
            print(f"  - Algebraic simplifications: {stats['algebraic_simplifications']}")
            
            return True
        else:
            print(f"✗ API Error: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to API server")
        print("  Start the server with: uv run uvicorn api:app --reload")
        return False


if __name__ == "__main__":
    print("Testing /api/optimize endpoint...")
    print(f"Test code: {test_code}\n")
    
    success = test_optimize_endpoint()
    
    if success:
        print("\n✅ Optimization API endpoint test passed!")
    else:
        print("\n❌ Optimization API endpoint test failed!")
        sys.exit(1)
