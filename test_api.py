import requests
import os

BASE_URL = "http://localhost:8000"

def test_root():
    print("Testing Root Endpoint...")
    response = requests.get(BASE_URL + "/")
    assert response.status_code == 200
    print("✅ Root Endpoint OK")

def test_upload():
    print("\nTesting File Upload...")
    # Create a dummy file
    with open("test_file.txt", "w") as f:
        f.write("This is a test file.")
    
    files = {'file': open('test_file.txt', 'rb')}
    response = requests.post(BASE_URL + "/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "file_path" in data
    assert "media_type" in data
    print(f"✅ Upload OK: {data}")
    
    # Cleanup
    files['file'].close()
    os.remove("test_file.txt")
    return data['file_path'], data['media_type']

def test_chat(file_path=None, media_type=None):
    print("\nTesting Chat Endpoint...")
    payload = {
        "user_id": 1,
        "message": "Hello from test script!",
        "file_path": file_path,
        "media_type": media_type
    }
    response = requests.post(BASE_URL + "/chat", json=payload)
    if response.status_code != 200:
        print(f"❌ Chat Error: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    print(f"✅ Chat Reply: {data['reply']}")

def test_image_chat():
    print("\nTesting Image Chat...")
    # Create a dummy image (1x1 pixel PNG)
    import base64
    img_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
    with open("test_image.png", "wb") as f:
        f.write(img_data)
        
    files = {'file': open('test_image.png', 'rb')}
    response = requests.post(BASE_URL + "/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    f_path = data['file_path']
    m_type = data['media_type']
    
    payload = {
        "user_id": 1,
        "message": "What is in this image?",
        "file_path": f_path,
        "media_type": m_type
    }
    response = requests.post(BASE_URL + "/chat", json=payload)
    if response.status_code != 200:
        print(f"❌ Image Chat Error: {response.text}")
    else:
        print(f"✅ Image Chat Reply: {response.json()['reply']}")
    
    # Cleanup
    files['file'].close()
    os.remove("test_image.png")

if __name__ == "__main__":
    try:
        test_root()
        f_path, m_type = test_upload()
        test_chat(f_path, m_type)
        test_image_chat()
        print("\n🎉 All Tests Passed!")
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        print("Make sure the server is running: uvicorn main:app --reload")
