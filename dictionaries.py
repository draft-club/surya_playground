morocco_regions = {
    "طنجة-تطوان-الحسيمة": ["طنجة-أصيلة", "المضيق-الفنيدق", "تطوان", "الفحص-أنجرة", "العرائش", "الحسيمة", "شفشاون", "وزان"],
    "الجهة الشرقية": ["وجدة-أنجاد", "الناظور", "الدريوش", "جرادة", "بركان", "تاوريرت", "جرسيف", "فكيك"],
    "فاس-مكناس": ["فاس", "مكناس", "الحاجب", "إفران", "مولاي يعقوب", "صفرو", "بولمان", "تاونات", "تازة"],
    "الرباط-سلا-القنيطرة": ["الرباط", "سلا", "الصخيرات-تمارة", "القنيطرة", "الخميسات", "سيدي قاسم", "سيدي سليمان"],
    "بني ملال-خنيفرة": ["بني ملال", "أزيلال", "الفقيه بن صالح", "خنيفرة", "خريبكة"],
    "الدار البيضاء-سطات": ["الدار البيضاء", "المحمدية", "الجديدة", "النواصر", "مديونة", "بنسليمان", "برشيد", "سطات", "سيدي بنور"],
    "مراكش-آسفي": ["مراكش", "شيشاوة", "الحوز", "قلعة السراغنة", "الصويرة", "الرحامنة", "آسفي", "اليوسفية"],
    "درعة-تافيلالت": ["الرشيدية", "ورزازات", "ميدلت", "تنغير", "زاكورة"],
    "سوس-ماسة": ["أكادير-إيدا أوتنان", "إنزكان-آيت ملول", "اشتوكة آيت باها", "تارودانت", "تزنيت", "طاطا"],
    "كلميم-واد نون": ["كلميم", "آسا الزاك", "طانطان", "سيدي إفني"],
    "العيون-الساقية الحمراء": ["العيون", "بوجدور", "السمارة", "طرفاية"],
    "الداخلة-وادي الذهب": ["وادي الذهب", "أوسرد"]
}

# Define regex patterns as constants
LOI_REGEX = r"^2\.\d{2}\.\d{3}$"  # Only items starting with 2.
PUNCTUATION_REGEX = r"[^\w\s]"  # Matches any character that is not a word or whitespace
YEAR_REGEX_TEMPLATE = lambda current_year: fr"^(19(8[0-9]|9[0-9])|20(0[0-9]|1[0-9]|2[0-{current_year % 10}]))$"  # Year regex
FIRST_INTEGER_REGEX = r"\b\d+\b"  # Finds the first integer in a string

# Define Arabic words and their matching fields
ARABIC_WORDS = [
    ("الجريدة", "is_جريدة", True, (3, 12)),  # 3 words before and 12 words after
    ("الرسمية", "is_الرسمية", True, (3, 12)),  # 3 words before and 12 words after
    ("درهم", "is_amount", False, (3, 3)),  # Default context range
    ("متر", "is_area", False, (3, 3)),
    ("قرار", "is_قرار", False, (3, 3)),
    ("مقرر", "is_مقرر", False, (3, 3)),
    ("حكم", "is_حكم", False, (3, 3)),
]

# Define keywords for matching
KEYWORD_AMOUNT = "DH"