import re
from typing import Dict, List, Any

# English and Gujarati designation keywords (case-insensitive)
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
    "શિક્ષક", "પ્રોફેસર", "મેનેજર"
]

# English and Gujarati company suffix/type keywords (case-insensitive)
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
    "એસોસિએટ્સ", "ગ્રુપ", "એજન્સી", "બેંક", "ટ્રસ્ટ", "મંડળ", "દુકાન", "સ્ટોર્સ", "સ્ટોર"
]

# English and Gujarati address / location keywords (case-insensitive)
ADDRESS_KEYWORDS = [
    # English address tokens
    "road", "rd", "street", "st", "avenue", "ave", "society", "soc", "sector", "sec",
    "building", "bldg", "complex", "comp.", "plaza", "tower", "towers", "floor", "flr",
    "area", "city", "state", "district", "dist", "pincode", "pin", "near", "opp", "opposite",
    "behind", "beside", "at & po", "at.", "post", "taluka", "tal.", "tehsil", "highway", "hwy",
    "india", "gujarat", "ahmedabad", "surat", "vadodara", "baroda", "rajkot", "gandhinagar",
    "bhavnagar", "jamnagar", "junagadh", "anand", "nadiad", "mehsana", "morbi", "bhuj", "valsad",
    "way", "suite", "ste", "apt", "apartment", "flat", "shop", "office", "off.", "block", "blck",
    "zone", "center", "centre", "square", "sq", "lane", "ln", "cross", "bypass",
    # Gujarati address tokens
    "રોડ", "સોસાયટી", "સોસા.", "નગર", "નગરની", "ગામ", "પોસ્ટ", "તાલુકો", "જીલ્લો",
    "બિલ્ડિંગ", "બિલ્ડીંગ", "કોમ્પ્લેક્સ", "પાસે", "સામે", "પાછળ", "નજીક", "હાઈવે", "હાઇવે",
    "ગુજરાત", "ભારત", "અમદાવાદ", "સુરત", "વડોદરા", "રાજકોટ", "ગાંધીનગર", "ભાવનગર", "જામનગર",
    "બ્લોક", "ફ્લેટ", "ઓફિસ", "માળ", "શોપ", "દુકાન", "ઝોન", "સેક્ટર",
    "પાર્ક", "બાગ", "વાડી", "ચોક", "શેરી", "ગલી", "અપાર્ટમેન્ટ", "બંગલો", "બંગલોઝ", "કોલોની", "વિસ્તાર", "જિલ્લો", "જિ."
]

def clean_text_line(line: str) -> str:
    """Cleans a line of text by stripping whitespace and removing leading/trailing punctuation."""
    if not line:
        return ""
    # Strip whitespace
    line = line.strip()
    # Remove leading/trailing common punctuation but preserve Gujarati and English letters/numbers
    line = re.sub(r"^[^\w\s\u0A80-\u0AFF]+|[^\w\s\u0A80-\u0AFF]+$", "", line)
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

def extract_phones(text: str) -> List[str]:
    """Extracts phone numbers, mobile numbers from text."""
    # Matches formats like +91 98765 43210, 0261-2345678, (079) 12345678, 98765-43210, etc.
    # Pattern allows for Gujarati numbers as well if transcribed as digits (Tesseract usually outputs English digits for numbers)
    phone_pattern = r"\+?\d{1,4}[-.\s]??\(?\d{1,4}?\)?[-.\s]??\d{3,4}[-.\s]??\d{3,4}[-.\s]??\d{0,4}"
    
    candidates = re.findall(phone_pattern, text)
    valid_phones = []
    for candidate in candidates:
        # Clean candidates: count actual digits
        digits_only = re.sub(r"\D", "", candidate)
        # Phone numbers usually have 8 to 15 digits (including country code)
        if 8 <= len(digits_only) <= 15:
            valid_phones.append(candidate.strip())
            
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
        if any(lbl in line_lower for lbl in ["mobile", "mob", "phone", "tel", "email", "mail", "skype", "website", "web"]):
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
    designation_str = " / ".join(designations) if designations else None

    return {
        "owner_name": owner_name or None,
        "designation": designation_str,
        "company_name": company_name or None,
        "email": emails[0] if emails else None,
        "website": websites[0] if websites else None,
        "location": location or None,
        "phones": phones
    }
