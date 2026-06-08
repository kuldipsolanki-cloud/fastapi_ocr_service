import re
from typing import Dict, List, Any

# English, Gujarati, and Hindi designation keywords (case-insensitive)
DESIGNATION_KEYWORDS = [
    # English designations
    "ceo", "founder", "co-founder", "director", "managing director", "md",
    "manager", "proprietor", "prop.", "owner", "partner", "president", "vp",
    "vice president", "chairman", "secretary", "developer", "engineer", "architect",
    "consultant", "designer", "executive", "representative", "agent", "officer",
    "specialist", "coordinator", "administrator", "accountant", "advocate",
    "doctor", "dr.", "professor", "prof.", "principal", "head", "lead",
    # Gujarati designations (transliterated & native script)
    "સંચાલક", "માલિક", "ભાગીદાર", "સેક્રેટરી", "પ્રમુખ", "અધ્યક્ષ",
    "વ્યવસ્થાપક", "પ્રોપરાઈટર", "તંત્રી", "કન્વેનર", "આયોજક",
    "એડવોકેટ", "વકીલ", "ડોક્ટર", "ડૉક્ટર", "ઇજનેર", "ઈજનેર",
    "શિક્ષક", "પ્રોફેસર", "મેનેજર",
    # Hindi designations
    "संचालक", "मालिक", "प्रबंधक", "साझेदार", "अध्यक्ष", "सचिव", 
    "अधिवक्ता", "वकील", "डॉक्टर", "अभियंता", "शिक्षक", "प्राध्यापक", 
    "प्रधान", "एडवोकेट", "मैनेजर"
]

# English, Gujarati, and Hindi company suffix/type keywords (case-insensitive)
COMPANY_KEYWORDS = [
    # English suffixes
    r"\bltd\b", r"\blimited\b", r"\bpvt\b", r"\bprivate\b", r"\bcorp\b", 
    r"\bcorporation\b", r"\binc\b", r"\bincorporated\b", r"\bllp\b", 
    r"\bco\b", r"\bcompany\b", r"\bgroup\b", r"\bindustries\b", r"\bindustry\b",
    r"\benterprises\b", r"\benterprise\b", r"\bsolutions\b", r"\bsolution\b",
    r"\bservices\b", r"\bservice\b", r"\btechnologies\b", r"\btechnology\b",
    r"\bsystems\b", r"\bsystem\b", r"\bstudio\b", r"\bassociates\b", 
    r"\bagency\b", r"\bagencies\b", r"\bbank\b", r"\bmart\b", r"\btrust\b",
    r"\borganization\b", r"\borg\b", r"\bassociation\b", r"\bclub\b",
    # Gujarati company indicators
    "લિમીટેડ", "લીમીટેડ", "પ્રાઇવેટ", "પ્રાઈવેટ", "એન્ટરપ્રાઇઝ", "એન્ટરપ્રાઈઝ",
    "ઇન્ડસ્ટ્રીઝ", "ઈન્ડસ્ટ્રીઝ", "સોલ્યુશન્સ", "સોલ્યુશન", "સર્વિસીસ", "સર્વિસ",
    "એસોસિએટ્સ", "ગ્રુપ", "એજન્સી", "બેંક", "ટ્રસ્ટ", "મંડળ", "દુકાન", "સ્ટોર્સ", "સ્ટોર",
    # Hindi company indicators
    "लिमिटेड", "लीमिटेड", "प्राइवेट", "प्राईवेट", "एंटरप्राइजेज", "एंटरप्राइज",
    "इंडस्ट्रीज", "सॉल्यूशंस", "सॉल्यूशन", "सर्विसेज", "सर्विस",
    "एसोसिएट्स", "ग्रुप", "एजेंसी", "बैंक", "ट्रस्ट", "मंडल", "समिति", "दुकान", "स्टोर्स", "स्टोर"
]

# English, Gujarati, and Hindi address / location keywords (case-insensitive)
ADDRESS_KEYWORDS = [
    # English address tokens
    "road", "rd", "street", "st", "avenue", "ave", "society", "soc", "sector", "sec",
    "building", "bldg", "complex", "comp.", "plaza", "tower", "towers", "floor", "flr",
    "area", "city", "state", "district", "dist", "pincode", "pin", "near", "opp", "opposite",
    "behind", "beside", "at & po", "at.", "post", "taluka", "tal.", "tehsil", "highway", "hwy",
    "gujarat", "ahmedabad", "surat", "vadodara", "baroda", "rajkot", "gandhinagar",
    "bhavnagar", "jamnagar", "junagadh", "anand", "nadiad", "mehsana", "morbi", "bhuj", "valsad",
    "way", "suite", "ste", "apt", "apartment", "flat", "shop", "office", "off.", "block", "blck",
    "zone", "center", "centre", "square", "sq", "lane", "ln", "cross", "bypass",
    # Gujarati address tokens
    "રોડ", "સોસાયટી", "સોસા.", "નગર", "નગરની", "ગામ", "પોસ્ટ", "તાલુકો", "જીલ્લો",
    "બિલ્ડિંગ", "બિલ્ડીંગ", "કોમ્પ્લેક્સ", "પાસે", "સામે", "પાછળ", "નજીક", "હાઈવે", "હાઇવે",
    "ગુજરાત", "અમદાવાદ", "સુરત", "વડોદરા", "રાજકોટ", "ગાંધીનગર", "ભાવનગર", "જામનગર",
    "બ્લોક", "ફ્લેટ", "ઓફિસ", "માળ", "શોપ", "દુકાન", "ઝોન", "સેક્ટર",
    "પાર્ક", "બાગ", "વાડી", "ચોક", "શેરી", "ગલી", "અપાર્ટમેન્ટ", "બંગલો", "બંગલોઝ", "કોલોની", "વિસ્તાર", "જિલ્લો", "જિ.",
    # Hindi address tokens
    "मार्ग", "रोड", "गली", "चौक", "नगर", "ग्राम", "गाँव", "गांव", "जिला", "ज़िला", "जि.", "तहसील", "ता.",
    "भवन", "अपार्टमेंट", "बंगला", "सोसायटी", "सोसा.", "कोलोनी", "क्षेत्र", "इलाका", "पास", "के पास", 
    "सामने", "के सामने", "पीछे", "के पीछे", "राजमार्ग", "हाईवे", "हाई-वे", "कार्यालय", "ऑफिस", 
    "दुकान", "मंजिल", "मंज़िल", "फ्लैट", "सेक्टर"
]

STATES = [
    # English
    "Gujarat", "Maharashtra", "Rajasthan", "Delhi", "Karnataka", "Tamil Nadu", "Uttar Pradesh", 
    "Madhya Pradesh", "West Bengal", "Haryana", "Punjab", "Telangana", "Andhra Pradesh", "Kerala", "Goa", "Bihar",
    # Gujarati
    "ગુજરાત", "મહારાષ્ટ્ર", "રાજસ્થાન", "દિલ્હી", "કર્ણાટક", "તમિલનાડુ", "ઉત્તર પ્રદેશ", "મધ્ય પ્રદેશ",
    # Hindi
    "गुजरात", "महाराष्ट्र", "राजस्थान", "दिल्ली", "कर्नाटक", "तमिलनाडु", "उत्तर प्रदेश", "मध्य प्रदेश", "बिहार", "हरियाणा", "पंजाब"
]

CITIES = [
    # English
    "Ahmedabad", "Surat", "Vadodara", "Baroda", "Rajkot", "Bhavnagar", "Jamnagar", "Gandhinagar", 
    "Bhuj", "Morbi", "Anand", "Nadiad", "Mehsana", "Valsad", "Vapi", "Navsari", "Bharuch", "Ankleshwar", 
    "Junagadh", "Surendranagar", "Porbandar", "Godhra", "Dahod", "Palanpur", "Patan", "Veraval", "Amreli", 
    "Deesa", "Mumbai", "Pune", "Bangalore", "Bengaluru", "Chennai", "Hyderabad", "Delhi", "New Delhi", 
    "Kolkata", "Jaipur", "Udaipur", "Jodhpur", "Noida", "Gurugram", "Gurgaon", "Indore", "Bhopal", 
    "Lucknow", "Patna", "Dwarka",
    # Gujarati
    "અમદાવાદ", "સુરત", "વડોદરા", "બરોડા", "રાજકોટ", "ભાવનગર", "જામનગર", "ગાંધીનગર", 
    "ભુજ", "મોરબી", "આણંદ", "નડિયાદ", "મહેસાણા", "વલસાડ", "વાપી", "નવસારી", "ભરૂચ", "અંકલેશ્વર", 
    "જૂનાગઢ", "સુરેન્દ્રનગર", "પોરબંદર", "ગોધરા", "દાહોદ", "પાલનપુર", "પાટણ", "વેરાવળ", "અમરેલી", 
    "ડીસા", "મુંબઈ", "પુણે", "બેંગલોર", "બેલગાવી", "ચેન્નાઈ", "હૈદરાબાદ", "દિલ્હી", "નવી દિલ્હી", 
    "કોલકાતા", "જયપુર", "ઉદયપુર", "જોધપુર", "નોઈડા", "ગુરૂગ્રામ", "ઇન્દોર", "ભોપาล", 
    "લખનૌ", "પટના", "દ્વારકા",
    # Hindi
    "अहमदाबाद", "सूरत", "वडोदरा", "बड़ौदा", "राजकोट", "भावनगर", "जामनगर", "गांधीनगर", 
    "भुज", "मोरबी", "आनंद", "नडियाद", "मेहसाना", "वलसाड", "वापी", "नवसारी", "भरूच", "अंकलेश्वर", 
    "जूनागढ़", "सुरेंद्रनगर", "पोरबंदर", "गोधरा", "दाहौद", "दाहोद", "पालनपुर", "पाटन", "वेरावल", "अमरेली", 
    "डीसा", "मुंबई", "पुणे", "बंगलौर", "बेंगलुरु", "चेन्नई", "हैबाद", "हैदराबाद", "दिल्ली", "नई दिल्ली", 
    "कोलकाता", "जयपुर", "उदयपुर", "जोधपुर", "नोएडा", "गुरुग्राम", "गुड़गांव", "इंदौर", "भोपाल", 
    "लखनऊ", "पटना", "द्वारका"
]

CITY_TO_STATE_EN = {
    # Gujarat
    "Ahmedabad": "Gujarat", "Surat": "Gujarat", "Vadodara": "Gujarat", "Baroda": "Gujarat", "Rajkot": "Gujarat",
    "Bhavnagar": "Gujarat", "Jamnagar": "Gujarat", "Gandhinagar": "Gujarat", "Bhuj": "Gujarat", "Morbi": "Gujarat",
    "Anand": "Gujarat", "Nadiad": "Gujarat", "Mehsana": "Gujarat", "Valsad": "Gujarat", "Vapi": "Gujarat",
    "Navsari": "Gujarat", "Bharuch": "Gujarat", "Ankleshwar": "Gujarat", "Junagadh": "Gujarat", 
    "Surendranagar": "Gujarat", "Porbandar": "Gujarat", "Godhra": "Gujarat", "Dahod": "Gujarat", 
    "Palanpur": "Gujarat", "Patan": "Gujarat", "Veraval": "Gujarat", "Amreli": "Gujarat", "Deesa": "Gujarat",
    "Dwarka": "Gujarat",
    # Maharashtra
    "Mumbai": "Maharashtra", "Pune": "Maharashtra",
    # Karnataka
    "Bangalore": "Karnataka", "Bengaluru": "Karnataka",
    # Tamil Nadu
    "Chennai": "Tamil Nadu",
    # Telangana
    "Hyderabad": "Telangana",
    # Delhi
    "Delhi": "Delhi", "New Delhi": "Delhi",
    # West Bengal
    "Kolkata": "West Bengal",
    # Rajasthan
    "Jaipur": "Rajasthan", "Udaipur": "Rajasthan", "Jodhpur": "Rajasthan",
    # Uttar Pradesh
    "Noida": "Uttar Pradesh", "Lucknow": "Uttar Pradesh",
    # Haryana
    "Gurugram": "Haryana", "Gurgaon": "Haryana",
    # Madhya Pradesh
    "Indore": "Madhya Pradesh", "Bhopal": "Madhya Pradesh",
    # Bihar
    "Patna": "Bihar"
}

CITY_TO_STATE_GU = {
    "અમદાવાદ": "ગુજરાત", "સુરત": "ગુજરાત", "વડોદરા": "ગુજરાત", "બરોડા": "ગુજરાત", "રાજકોટ": "ગુજરાત",
    "ભાવનગર": "ગુજરાત", "જામનગર": "ગુજરાત", "ગાંધીનગર": "ગુજરાત", "ભુજ": "ગુજરાત", "મોરબી": "ગુજરાત",
    "આણંદ": "ગુજરાત", "નડિયાદ": "ગુજરાત", "મહેસાણા": "ગુજરાત", "વલસાડ": "ગુજરાત", "વાપી": "ગુજરાત",
    "નવસારી": "ગુજરાત", "ભરૂચ": "ગુજરાત", "અંકલેશ્વર": "ગુજરાત", "જૂનાગઢ": "ગુજરાત", "સુરેન્દ્રનગર": "ગુજરાત",
    "પોરબંદર": "ગુજરાત", "ગોધરા": "ગુજરાત", "દાહોદ": "ગુજરાત", "પાલનપુર": "ગુજરાત", "પાટણ": "ગુજરાત",
    "વેરાવળ": "ગુજરાત", "અમરેલી": "ગુજરાત", "ડીસા": "ગુજરાત", "દ્વારકા": "ગુજરાત",
    "મુંબઈ": "મહારાષ્ટ્ર", "પુણે": "મહારાષ્ટ્ર", "બેંગલોર": "કર્ણાટક", "ચેન્નાઈ": "તમિલનાડુ",
    "હૈદરાબાદ": "તેલંગાણા", "દિલ્હી": "દિલ્હી", "નવી દિલ્હી": "દિલ્હી"
}

CITY_TO_STATE_HI = {
    "अहमदाबाद": "गुजरात", "सूरत": "गुजरात", "वडोदरा": "गुजरात", "बड़ौदा": "गुजरात", "राजकोट": "गुजरात",
    "भावनगर": "गुजरात", "जामनगर": "गुजरात", "गांधीनगर": "गुजरात", "भुज": "गुजरात", "मोरबी": "गुजरात",
    "आनंद": "गुजरात", "नडियाद": "गुजरात", "मेहसाना": "गुजरात", "वलसाड": "गुजरात", "वापी": "गुजरात",
    "नवसारी": "गुजरात", "भरूच": "गुजरात", "अंकलेश्वर": "गुजरात", "जूनागढ़": "गुजरात", "सुरेंद्रनगर": "गुजरात",
    "पोरबंदर": "गुजरात", "गोधरा": "गुजरात", "दाहौद": "गुजरात", "दाहोद": "गुजरात", "पालनपुर": "गुजरात",
    "पाटन": "गुजरात", "वेरावल": "गुजरात", "अमरेली": "गुजरात", "डीसा": "गुजरात", "द्वारका": "गुजरात",
    "मुंबई": "महाराष्ट्र", "पुणे": "महाराष्ट्र", "बंगलौर": "कर्नाटक", "बेंगलुरु": "कर्नाटक",
    "चेन्नई": "तमिलनाडु", "हैराबाद": "तेलंगाना", "हैदराबाद": "तेलंगाना", "दिल्ली": "दिल्ली", "नई दिल्ली": "दिल्ली",
    "कोलकाता": "पश्चिम बंगाल", "जयपुर": "राजस्थान", "उदयपुर": "राजस्थान", "जोधपुर": "राजस्थान",
    "नोएडा": "उत्तर प्रदेश", "लखनऊ": "उत्तर प्रदेश", "गुरुग्राम": "हरियाणा", "गुड़गांव": "हरियाणा",
    "इन्डोर": "मध्य प्रदेश", "इंदौर": "मध्य प्रदेश", "भोपाल": "मध्य प्रदेश", "पटना": "बिहार"
}

def extract_city_and_state(text: str) -> (str, str):
    city = ""
    state = ""
    
    # Check for state presence
    for s in STATES:
        if re.search(r'[a-zA-Z]', s):
            if re.search(rf"\b{re.escape(s)}\b", text, re.IGNORECASE):
                state = s
                break
        else:
            if s in text:
                state = s
                break
                
    # Check for city presence
    for c in CITIES:
        if re.search(r'[a-zA-Z]', c):
            if re.search(rf"\b{re.escape(c)}\b", text, re.IGNORECASE):
                city = c
                break
        else:
            if c in text:
                city = c
                break
                
    # Fallback lookup if city is found but state is not present in text
    if city and not state:
        if city in CITY_TO_STATE_EN:
            state = CITY_TO_STATE_EN[city]
        elif city in CITY_TO_STATE_GU:
            state = CITY_TO_STATE_GU[city]
        elif city in CITY_TO_STATE_HI:
            state = CITY_TO_STATE_HI[city]
            
    return city, state

def clean_text_line(line: str) -> str:
    """Cleans a line of text by stripping whitespace and removing leading/trailing punctuation."""
    if not line:
        return ""
    # Strip whitespace
    line = line.strip()
    # Remove leading/trailing common punctuation but preserve Gujarati, Devanagari (Hindi) and English letters/numbers
    line = re.sub(r"^[^\w\s\u0A80-\u0AFF\u0900-\u097F]+|[^\w\s\u0A80-\u0AFF\u0900-\u097F]+$", "", line)
    return line.strip()

def extract_emails(text: str) -> List[str]:
    """Extracts email addresses from text."""
    # Standard email regex
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return re.findall(email_pattern, text)

def extract_websites(text: str, emails: List[str]) -> List[str]:
    """
    Extracts website URLs from text.
    Filters out emails to avoid matching domain names of email addresses.
    """
    # Remove email lines or text first to prevent email domains from being recognized as websites
    temp_text = text
    for email in emails:
        temp_text = temp_text.replace(email, "")

    # Website patterns including common prefixes or extensions
    website_pattern = r"\b(?:https?://)?(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?(?:/[^\s]*)?\b"
    matches = re.findall(website_pattern, temp_text)
    
    # Filter and validate matches (avoid pure numbers/IPs or invalid patterns)
    valid_websites = []
    for match in matches:
        match_clean = match.strip(".,/ ")
        # Skip if match looks like a file name, email portion, or simple numeric IP
        if not re.match(r"^\d+(\.\d+){3}$", match_clean) and "." in match_clean:
            # Avoid picking up strings that are just emails (in case any slipped through)
            if "@" not in match_clean:
                valid_websites.append(match_clean)
                
    return list(set(valid_websites))

def translate_indian_digits_to_english(text: str) -> str:
    """Translates Gujarati and Devanagari digits to standard English ASCII digits."""
    gujarati_digits = "૦૧૨૩૪૫૬૭૮૯"
    devanagari_digits = "०१२३४५६७८९"
    english_digits = "0123456789"
    
    trans_table = str.maketrans(
        gujarati_digits + devanagari_digits,
        english_digits + english_digits
    )
    return text.translate(trans_table)

def clean_stray_artifacts(text: str) -> str:
    """
    Cleans stray OCR artifacts from parsed string fields:
    - Removes standalone vertical bars '|' and extraneous slashes
    - Trims leading/trailing whitespace
    - Strips stray trailing letters or incomplete character residues (e.g. single letters like 'ટ્', 'ગા', 'જ' at the end)
    """
    if not text:
        return ""
        
    # Remove standalone vertical bars, backslashes, or common separator noise
    text = re.sub(r'\s*\|\s*', ' ', text)
    text = re.sub(r'\s*\\\s*', ' ', text)
    text = text.strip()
    
    while True:
        prev_text = text
        # Remove trailing single Gujarati/Hindi letters (optionally with a virama/zwnj/zwj) separated by space
        text = re.sub(r'\s+[\u0A80-\u0AFF\u0900-\u097F][\u0ACD\u200C\u200D]?$', '', text)
        # Remove trailing single English letters separated by space
        text = re.sub(r'\s+[a-zA-Z]$', '', text)
        # Remove trailing non-alphanumeric punctuation marks/garbage symbols
        text = re.sub(r'\s+[^\w\s\u0A80-\u0AFF\u0900-\u097F]+$', '', text)
        text = text.strip()
        if text == prev_text:
            break
            
    # Also remove any leftover leading/trailing commas, dots, dashes, or spaces
    text = re.sub(r'^[.,/\\\s-]+|[.,/\\\s-]+$', '', text)
    return text.strip()

def extract_phones(text: str) -> List[str]:
    """Extracts phone numbers, mobile numbers from text and translates Indian digits to English."""
    # Matches formats like +91 98765 43210, 0261-2345678, (079) 12345678, 98765-43210, etc.
    # Pattern allows for Gujarati numbers as well if transcribed as digits (Tesseract usually outputs English digits for numbers)
    phone_pattern = r"\+?\d{1,4}[-.\s]??\(?\d{1,4}?\)?[-.\s]??\d{3,4}[-.\s]??\d{3,4}[-.\s]??\d{0,4}"
    
    candidates = re.findall(phone_pattern, text)
    valid_phones = []
    for candidate in candidates:
        # Translate Gujarati/Devanagari digits to English digits
        candidate_eng = translate_indian_digits_to_english(candidate)
        # Clean candidates: count actual ASCII digits
        digits_only = re.sub(r"[^0-9]", "", candidate_eng)
        # Phone numbers usually have 8 to 15 digits (including country code)
        if 8 <= len(digits_only) <= 15:
            valid_phones.append(candidate_eng.strip())
            
    return list(set(valid_phones))

def parse_business_card(raw_text: str) -> Dict[str, Any]:
    """
    Parses business card text to extract Owner Name, Designation, Company, 
    Emails, Websites, Phones, and Location.
    Supports both English and Gujarati.
    """
    # Fix OCR spacing issues in websites/emails, e.g. "www.google. com" -> "www.google.com"
    # only in lines that look like emails or websites to avoid breaking abbreviations like "Opp. Yash"
    cleaned_raw_lines = []
    for line in raw_text.split("\n"):
        line_lower = line.lower()
        if "@" in line or "www" in line_lower or "http" in line_lower or any(k in line_lower for k in ["website", "web:", "email:", "mail:"]):
            line = re.sub(r'(\w+)\.[ \t]+(\w+)', r'\1.\2', line)
        cleaned_raw_lines.append(line)
    raw_text = "\n".join(cleaned_raw_lines)
    
    # 1. Extract contact details (independent of line structure)
    emails = extract_emails(raw_text)
    websites = extract_websites(raw_text, emails)
    phones = extract_phones(raw_text)
    
    # Clean up line-by-line classification
    parsed_emails = set(emails)
    parsed_websites = set(websites)
    parsed_phones = set(phones)
    
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    
    # Pre-process lines: split lines containing contact markers (e.g. "Name Mobile: 1234")
    # to separate names/designations from their inline contact labels.
    processed_lines = []
    contact_marker_pattern = r"\b(mobile|mob|phone|ph|tel|email|mail|skype|website|web|fax)\b\s*[:.-]?\s*"
    
    for line in lines:
        match = re.search(contact_marker_pattern, line, re.IGNORECASE)
        if match:
            left = line[:match.start()].strip()
            right = line[match.start():].strip()
            
            left_clean = clean_text_line(left)
            if left_clean:
                processed_lines.append(left_clean)
                
            right_clean = clean_text_line(right)
            if right_clean:
                processed_lines.append(right_clean)
        else:
            cleaned = clean_text_line(line)
            if cleaned:
                processed_lines.append(cleaned)
                
    cleaned_lines = processed_lines
    
    # We will categorize each line to find name, designation, company, and location
    designations = []
    company_name = ""
    owner_name = ""
    location_lines = []
    
    # To identify name and company, we check lines that are NOT contact details or address
    candidate_lines = []
    
    for line in cleaned_lines:
        # Skip if this line is just an email, website, skype or phone number
        is_contact = False
        line_lower = line.lower()
        
        # Explicit check for contact labels
        if any(re.search(rf"\b{lbl}\b", line_lower) for lbl in ["mobile", "mob", "phone", "tel", "email", "mail", "skype", "website", "web"]):
            is_contact = True
            
        for email in parsed_emails:
            if email in line:
                is_contact = True
        for web in parsed_websites:
            if web in line:
                is_contact = True
                
        # If line is mostly digits and dashes, classify as phone
        digits_count = sum(c.isdigit() for c in line)
        if len(line) > 0 and (digits_count / len(line)) > 0.5 and digits_count >= 8:
            is_contact = True
            
        if is_contact:
            continue
            
        # Check if line matches Designation keywords
        is_designation = False
        for kw in DESIGNATION_KEYWORDS:
            # Word boundary check for English keywords, simple inclusion for Gujarati
            if kw in ["ceo", "vp", "md", "prop."]:
                pattern = rf"\b{kw}\b"
            else:
                pattern = re.escape(kw)
                
            if re.search(pattern, line_lower):
                is_designation = True
                designations.append(line)
                break
                
        if is_designation:
            continue
            
        # Check if line contains Location keywords or Pincode/Zipcode
        is_location = False
        for kw in ADDRESS_KEYWORDS:
            if kw in line_lower:
                is_location = True
                break
        # Or look for a pincode or zip code (e.g. 380001, 380 001, 94105, 94105-1234)
        if re.search(r"\b\d{6}\b|\b\d{3}\s?\d{3}\b|\b\d{5}(?:-\d{4})?\b", line):
            is_location = True
            
        if is_location:
            location_lines.append(line)
            continue
            
        # If it's not designation, contact, or location, it's a candidate for name/company
        candidate_lines.append(line)

    # Secondary location check: grab adjacent lines that look like part of address (e.g. contains digits)
    # or start with digits, which is very common for street numbers/shop numbers.
    changed = True
    while changed:
        changed = False
        for i, line in enumerate(cleaned_lines):
            if line in candidate_lines:
                # IMPORTANT: Skip if the candidate line has contact-related labels
                line_lower = line.lower()
                if any(lbl in line_lower for lbl in ["mobile", "mob", "phone", "tel", "email", "mail", "skype", "website", "web"]):
                    continue
                
                # Check if it has a digit or address term
                has_digit = any(c.isdigit() for c in line)
                # Check if adjacent to an already identified location line
                is_adjacent = False
                if i > 0 and cleaned_lines[i - 1] in location_lines:
                    is_adjacent = True
                if i < len(cleaned_lines) - 1 and cleaned_lines[i + 1] in location_lines:
                    is_adjacent = True
                
                # Check if it contains specific address helper words
                has_address_word = any(
                    w in line_lower 
                    for w in ["way", "suite", "floor", "block", "bldg", "office", "shop", "flat", "માળ", "ઓફિસ", "દુકાન"]
                )
                
                if is_adjacent and (has_digit or has_address_word):
                    location_lines.append(line)
                    candidate_lines.remove(line)
                    changed = True
                    break # Restart loop since collections modified

    # 2. Extract Company Name
    # Look for company suffixes in candidates
    for cand in candidate_lines:
        cand_lower = cand.lower()
        has_company_kw = False
        for kw in COMPANY_KEYWORDS:
            # Word boundary check for English, simple inclusion for Gujarati
            if kw.startswith(r"\b"):
                pattern = kw
            else:
                pattern = re.escape(kw)
                
            if re.search(pattern, cand_lower):
                has_company_kw = True
                company_name = cand
                break
        if has_company_kw:
            break
            
    # If company name found, remove it from candidates
    if company_name in candidate_lines:
        candidate_lines.remove(company_name)
        
    # 3. Extract Owner Name
    # Heuristic: The owner name is usually:
    # - Directly above or below the designation line
    # - If we search cleaned_lines around the designation, we can identify it.
    if designations:
        for desig in designations:
            try:
                desig_idx = cleaned_lines.index(desig)
                # Check line above designation first
                if desig_idx > 0:
                    above_line = cleaned_lines[desig_idx - 1]
                    if above_line in candidate_lines:
                        owner_name = above_line
                        break
                # Check line below designation if not found
                if desig_idx < len(cleaned_lines) - 1:
                    below_line = cleaned_lines[desig_idx + 1]
                    if below_line in candidate_lines:
                        owner_name = below_line
                        break
            except ValueError:
                pass
            
    # If owner name is still not found, take the first candidate line that doesn't contain digits
    # and has a reasonable length (typically 2-4 words in English, or similar length in Gujarati).
    if not owner_name and candidate_lines:
        for cand in candidate_lines:
            # Names shouldn't contain digits or common URL/email patterns
            if not any(c.isdigit() for c in cand) and len(cand) > 3:
                # Avoid company names if possible (often company name is longer or contains symbols)
                words = cand.split()
                if len(words) <= 5: # Name is rarely more than 5 words
                    owner_name = cand
                    break
                    
    # If owner name found, remove from candidates
    if owner_name in candidate_lines:
        candidate_lines.remove(owner_name)
        
    # 4. Fallback for Company Name if not found yet
    # If company name was not found via suffixes, the first remaining candidate line
    # (often at the top of the card or largest text) could be the company name.
    if not company_name and candidate_lines:
        # Select the candidate line that is not the owner name and could represent a company
        company_name = candidate_lines[0]
        candidate_lines.pop(0)

    # 5. Format Location / Address
    # Sort location lines based on original appearance order in cleaned_lines
    location_lines = sorted(location_lines, key=lambda l: cleaned_lines.index(l) if l in cleaned_lines else 999)
    location = ", ".join(location_lines) if location_lines else ""
    
    # If we have left-over candidate lines that contain address-like terms or look like street numbers
    # but weren't classified, we can append them to location if location is empty.
    if not location and candidate_lines:
        # If there are left-over lines with numbers (could be flat/shop numbers), treat them as location
        shop_nums = [cand for cand in candidate_lines if any(c.isdigit() for c in cand)]
        if shop_nums:
            location = ", ".join(shop_nums)
            for item in shop_nums:
                if item in candidate_lines:
                    candidate_lines.remove(item)

    # Combine multiple designations if found
    cleaned_designations = [clean_stray_artifacts(d) for d in designations if clean_stray_artifacts(d)]
    designation_str = " / ".join(cleaned_designations) if cleaned_designations else ""

    # Extract city and state
    city, state = extract_city_and_state(raw_text)

    return {
        "person_name": clean_stray_artifacts(owner_name),
        "business_name": clean_stray_artifacts(company_name),
        "designation": designation_str,
        "phones": phones,
        "emails": emails,
        "websites": websites,
        "address": clean_stray_artifacts(location),
        "city": city or "",
        "state": state or "",
        "raw_text": raw_text
    }
