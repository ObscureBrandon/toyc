from api import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_icg_endpoint():
    code = "x := 5 + 3 * 2;"
    response = client.post("/api/icg", json={"code": code})
    
    assert response.status_code == 200
    data = response.json()
    
    print("Status:", response.status_code)
    print("Instructions:")
    for inst in data["instructions"]:
        print(f"  {inst}")
    print(f"Temp count: {data['temp_count']}")
    print(f"Label count: {data['label_count']}")
    
    assert len(data["instructions"]) == 3
    assert data["temp_count"] == 2
    assert data["label_count"] == 0

if __name__ == "__main__":
    test_icg_endpoint()
    print("\n✓ ICG endpoint test passed!")
