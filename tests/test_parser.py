import sys
from pathlib import Path

# Reconfigure stdout/stderr to support UTF-8 (crucial for printing Hindi/Gujarati text on Windows)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Add project root to path so we can import app
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.parser import parse_business_card

def test_english_card_parsing():
    raw_text = """
    Nexus Solutions India
    Amit Patel
    Chief Executive Officer
    
    Mob: +91 98765 43210
    Tel: +91 80 1234 5678
    amit.patel@nexussolutions.in
    www.nexussolutions.in
    
    1200 Innovation Way, Sector 4,
    Whitefield, Bangalore, Karnataka - 560066
    """
    
    parsed = parse_business_card(raw_text)
    
    print("\n--- English Card Parsing Test ---")
    print(f"Raw Text:\n{raw_text.strip()}\n")
    print(f"Parsed Result: {parsed}")
    
    assert parsed["person_name"] == "Amit Patel", f"Expected Amit Patel, got {parsed['person_name']}"
    assert parsed["designation"] == "Chief Executive Officer", f"Expected Chief Executive Officer, got {parsed['designation']}"
    assert parsed["business_name"] == "Nexus Solutions India", f"Expected Nexus Solutions India, got {parsed['business_name']}"
    assert "amit.patel@nexussolutions.in" in parsed["emails"]
    assert "www.nexussolutions.in" in parsed["websites"]
    assert parsed["city"] == "Bangalore", f"Expected Bangalore, got {parsed['city']}"
    assert parsed["state"] == "Karnataka", f"Expected Karnataka, got {parsed['state']}"
    assert "1200 Innovation Way" in parsed["address"]
    assert len(parsed["phones"]) >= 2
    print("[OK] English card parsing test PASSED!")

def test_gujarati_card_parsing():
    raw_text = """
    શ્રીજી એન્ટરપ્રાઇઝ
    મહેશભાઈ શાહ
    માલિક
    
    ફોન: +91 99887 76655
    ઇમેઇલ: contact@shreejienterprise.in
    વેબસાઇટ: www.shreejienterprise.in
    
    ૨૦૨, શ્રીજી કોમ્પ્લેક્સ, એસ. જી. હાઇવે, અમદાવાદ - ૩૮૦૦૫૪
    """
    
    parsed = parse_business_card(raw_text)
    
    print("\n--- Gujarati Card Parsing Test ---")
    print(f"Raw Text:\n{raw_text.strip()}\n")
    print(f"Parsed Result: {parsed}")
    
    assert parsed["person_name"] == "મહેશભાઈ શાહ", f"Expected મહેશભાઈ શાહ, got {parsed['person_name']}"
    assert parsed["designation"] == "માલિક", f"Expected માલિક, got {parsed['designation']}"
    assert parsed["business_name"] == "શ્રીજી એન્ટરપ્રાઇઝ", f"Expected શ્રીજી એન્ટરપ્રાઇઝ, got {parsed['business_name']}"
    assert "contact@shreejienterprise.in" in parsed["emails"]
    assert "www.shreejienterprise.in" in parsed["websites"]
    assert parsed["city"] == "અમદાવાદ", f"Expected અમદાવાદ, got {parsed['city']}"
    assert parsed["state"] == "ગુજરાત", f"Expected ગુજરાત, got {parsed['state']}"
    assert "એસ. જી. હાઇવે" in parsed["address"] or "એસ.જી. હાઇવે" in parsed["address"]
    assert "+91 99887 76655" in parsed["phones"]
    print("[OK] Gujarati card parsing test PASSED!")

def test_hindi_card_parsing():
    raw_text = """
    माँ शारदा प्रिंटर्स
    राजेश शर्मा
    प्रबंधक
    
    मोबाईल: +91 98765 43210
    ईमेल: rajesh@sharda.in
    वेबसाइट: www.sharda.in
    
    १०२, श्री राम काम्प्लेक्स, एमजी रोड, इंदौर, मध्य प्रदेश - ४५२००१
    """
    
    parsed = parse_business_card(raw_text)
    
    print("\n--- Hindi Card Parsing Test ---")
    print(f"Raw Text:\n{raw_text.strip()}\n")
    print(f"Parsed Result: {parsed}")
    
    assert parsed["person_name"] == "राजेश शर्मा", f"Expected राजेश शर्मा, got {parsed['person_name']}"
    assert parsed["designation"] == "प्रबंधक", f"Expected प्रबंधक, got {parsed['designation']}"
    assert parsed["business_name"] == "माँ शारदा प्रिंटर्स", f"Expected माँ शारदा प्रिंटर्स, got {parsed['business_name']}"
    assert "rajesh@sharda.in" in parsed["emails"]
    assert "www.sharda.in" in parsed["websites"]
    assert parsed["city"] == "इंदौर", f"Expected इंदौर, got {parsed['city']}"
    assert parsed["state"] == "मध्य प्रदेश", f"Expected मध्य प्रदेश, got {parsed['state']}"
    assert "एमजी रोड" in parsed["address"]
    assert "+91 98765 43210" in parsed["phones"]
    print("[OK] Hindi card parsing test PASSED!")

if __name__ == "__main__":
    print("Running parser heuristic tests...")
    test_english_card_parsing()
    test_gujarati_card_parsing()
    test_hindi_card_parsing()
    print("\nAll parser tests completed successfully!")
