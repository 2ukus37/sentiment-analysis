"""
Test image upload with OCR feature.
Creates a test image and uploads it to the API.
"""
from PIL import Image, ImageDraw, ImageFont
import requests
import io

def create_test_image(text, filename="test_image.png"):
    """Create a simple image with text."""
    # Create a white image
    img = Image.new('RGB', (800, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Draw text
    draw.text((50, 80), text, fill='black', font=font)
    
    # Save image
    img.save(filename)
    print(f"✅ Created test image: {filename}")
    return filename

def test_image_upload(image_path, text_description):
    """Test image upload to API."""
    print(f"\n📤 Testing: {text_description}")
    print(f"   Image: {image_path}")
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'source_type': 'auto'}
        
        response = requests.post('http://localhost:5000/api/predict/image',
                               files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Success!")
        print(f"   📝 Extracted Text: \"{result.get('extracted_text', 'N/A')}\"")
        print(f"   🎯 Prediction: {result.get('ensemble_label', 'N/A')}")
        print(f"   📊 Confidence: {result.get('ensemble_confidence', 0)*100:.1f}%")
        if result.get('ml_confidence'):
            print(f"   🤖 ML: {result['ml_confidence']*100:.1f}%")
        if result.get('gpt_confidence'):
            print(f"   🧠 GPT: {result['gpt_confidence']*100:.1f}%")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   {response.json()}")

def main():
    print("="*70)
    print("  🖼️ IMAGE UPLOAD & OCR TEST")
    print("="*70)
    
    # Test 1: Hate speech
    img1 = create_test_image("You are stupid and worthless", "test_hate.png")
    test_image_upload(img1, "Hate Speech Text")
    
    # Test 2: Non-hate
    img2 = create_test_image("Have a great day everyone!", "test_nonhate.png")
    test_image_upload(img2, "Non-Hate Text")
    
    # Test 3: Personal attack
    img3 = create_test_image("Stop vandalizing you moron", "test_attack.png")
    test_image_upload(img3, "Personal Attack Text")
    
    # Test 4: Non-attack
    img4 = create_test_image("This is a helpful contribution", "test_nonattack.png")
    test_image_upload(img4, "Non-Attack Text")
    
    print("\n" + "="*70)
    print("  ✅ IMAGE UPLOAD TESTS COMPLETE!")
    print("="*70)
    print("\n🌐 You can now use the Image Upload tab in the web interface!")
    print("   Open: http://localhost:5000")
    print("   Go to: Image Upload tab")
    print("   Upload any image with text and see the results!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure the server is running: .\\start_enhanced_api.bat")
