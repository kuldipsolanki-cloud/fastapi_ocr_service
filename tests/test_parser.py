import sys
from pathlib import Path

# Reconfigure stdout/stderr to support UTF-8 (crucial for printing Gujarati text on Windows)
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
    Nexus Solutions Inc.
    John Doe
    Chief Executive Officer
    
    Mob: +1 (555) 019-2834
    Tel: +1-555-019-2835
    john.doe@nexussolutions.com
    www.nexussolutions.com
    
    1200 Innovation Way, Suite 400
    Tech District, San Francisco, CA 94105
    """
    
    parsed = parse_business_card(raw_text)
    
    print("\n--- English Card Parsing Test ---")
    print(f"Raw Text:\n{raw_text.strip()}\n")
    print(f"Parsed Result: {parsed}")
    
    assert parsed["owner_name"] == "John Doe", f"Expected John Doe, got {parsed['owner_name']}"
    assert parsed["designation"] == "Chief Executive Officer", f"Expected Chief Executive Officer, got {parsed['designation']}"
    assert parsed["company_name"] == "Nexus Solutions Inc", f"Expected Nexus Solutions Inc, got {parsed['company_name']}"
    assert parsed["email"] == "john.doe@nexussolutions.com"
    assert parsed["website"] == "www.nexussolutions.com"
    assert "1200 Innovation Way" in parsed["location"]
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
    
    assert parsed["owner_name"] == "મહેશભાઈ શાહ", f"Expected મહેશભાઈ શાહ, got {parsed['owner_name']}"
    assert parsed["designation"] == "માલિક", f"Expected માલિક, got {parsed['designation']}"
    assert parsed["company_name"] == "શ્રીજી એન્ટરપ્રાઇઝ", f"Expected શ્રીજી એન્ટરપ્રાઇઝ, got {parsed['company_name']}"
    assert parsed["email"] == "contact@shreejienterprise.in"
    assert parsed["website"] == "www.shreejienterprise.in"
    assert "એસ. જી. હાઇવે" in parsed["location"] or "એસ.જી. હાઇવે" in parsed["location"]
    assert "+91 99887 76655" in parsed["phones"]
    print("[OK] Gujarati card parsing test PASSED!")

if __name__ == "__main__":
    print("Running parser heuristic tests...")
    test_english_card_parsing()
    test_gujarati_card_parsing()
    print("\nAll parser tests completed successfully!")
