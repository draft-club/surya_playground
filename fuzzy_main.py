import re
from datetime import datetime
import pandas as pd
from rapidfuzz import fuzz
from dictionaries import (
    morocco_regions,
    LOI_REGEX,
    PUNCTUATION_REGEX,
    YEAR_REGEX_TEMPLATE,
    ARABIC_WORDS,
    KEYWORD_AMOUNT,
    CONTEXT_RANGES,
    THRESHOLD_VALUES
)

def match_localities_to_region(localities):
    """
    Matches a list of localities to their corresponding region based on a dictionary.
    Returns the first matching region or 'NA' if no match is found.
    """
    province_to_region = {}
    for region, provinces in morocco_regions.items():
        for province in provinces:
            province_to_region[province] = region

    result = "NA"
    for locality in localities:
        if locality in province_to_region:
            result = province_to_region[locality]
            break
    return result

def process_text_file(file_path):
    """
    Reads a text file, splits its content into words, and returns the words as a list.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        words = file.read().split()
    return words

def remove_punctuation(words):
    """
    Removes punctuation from a list of words.
    """
    return [re.sub(PUNCTUATION_REGEX, "", word) for word in words]

def extract_matching_fields_with_context(words, regex, description, matches_with_context, field_name, is_regex, is_keyword, fuzzy_match_word=None):
    """
    Extracts words matching the given regex or via fuzzy matching, stores them in a dictionary with their indexes,
    and prints context based on the field type.
    """
    print(f"\n--- Matching fields for: {description} ---")

    for index, word in enumerate(words):
        # Check regex or fuzzy match
        match_found = False
        if regex:
            match_found = re.match(regex, word)
        elif fuzzy_match_word:
            threshold = THRESHOLD_VALUES.get(field_name, 90)  # Use threshold from dictionary
            match_found = fuzz.partial_ratio(word, fuzzy_match_word) >= threshold

        if match_found:
            # Determine context range from CONTEXT_RANGES
            before, after = CONTEXT_RANGES.get(field_name, (0, 0))
            context = words[max(0, index - before):index + 1] + words[index + 1:index + after + 1]

            # Store match and its index with the field flag
            matches_with_context[index] = {
                "word": word,
                "context": context,
                "context_in_words": len(context),
                field_name: 1,
                "is_regex": is_regex,
                "is_keyword": is_keyword,
                "object_start_index": index,
            }

            # Print the match with context
            context_str = " ".join(context)
            print(f"Matched Element: {word}, Index: {index}, Context: {context_str}")

# Main script
if __name__ == "__main__":
    file_path = 'output_surya_radeff.txt'

    # Step 1: Read the words from the file
    all_text_list = process_text_file(file_path)

    # Step 2: Remove punctuation
    cleaned_elements = remove_punctuation(all_text_list)

    # Step 3: Generate the year regex dynamically
    current_year = datetime.now().year
    year_regex = YEAR_REGEX_TEMPLATE(current_year)

    # Step 4: Create a shared dictionary to store matches
    matches_with_context = {}

    # Step 5: Extract and print matching fields for LOI regex (using uncleaned list)
    extract_matching_fields_with_context(all_text_list, LOI_REGEX, "LOI pattern (e.g., 2.22.645)", matches_with_context, "is_loi", is_regex=1, is_keyword=0)

    # Step 6: Extract and print matching fields for year regex (using cleaned list)
    extract_matching_fields_with_context(cleaned_elements, year_regex, f"Valid years between 1980 and {current_year}", matches_with_context, "is_year", is_regex=1, is_keyword=0)

    # Step 7: Apply fuzzy or exact matching for Arabic words and "DH"
    for arabic_word, field_name, use_fuzzy, context_range in ARABIC_WORDS:
        extract_matching_fields_with_context(
            all_text_list,
            rf"\b{arabic_word}\b" if not use_fuzzy else None,
            f"Arabic word: {arabic_word}",
            matches_with_context,
            field_name,
            is_regex=0,
            is_keyword=1,
            fuzzy_match_word=arabic_word if use_fuzzy else None,
        )

    extract_matching_fields_with_context(all_text_list, rf"\b{KEYWORD_AMOUNT}\b", f"Keyword: {KEYWORD_AMOUNT}", matches_with_context, "is_amount", is_regex=0, is_keyword=1)

    # Step 8: Ensure all boolean fields are present in the dictionary
    for match in matches_with_context.values():
        match.setdefault("is_loi", 0)
        match.setdefault("is_year", 0)
        match.setdefault("is_جريدة", 0)
        match.setdefault("is_الرسمية", 0)
        match.setdefault("is_amount", 0)
        match.setdefault("is_area", 0)
        match.setdefault("is_قرار", 0)
        match.setdefault("is_مقرر", 0)
        match.setdefault("is_حكم", 0)
        match.setdefault("is_regex", 0)
        match.setdefault("is_keyword", 0)

    # Step 9: Convert the dictionary into a DataFrame
    df = pd.DataFrame.from_dict(matches_with_context, orient="index")
    df["context"] = df["context"].apply(lambda x: " ".join(x))  # Convert context list to string for readability

    # Step 10: Add two new columns
    df["regex_expression"] = df.apply(
        lambda row: LOI_REGEX if row["is_loi"] == 1 else (year_regex if row["is_year"] == 1 else "NA"),
        axis=1
    )
    df["final_extraction"] = ""  # Initialize the 'final_extraction' column as empty

    # Step 11: Export the DataFrame to an Excel file
    output_file = "matches_output.xlsx"
    df.to_excel(output_file, index=True, sheet_name="Matches")
    print(f"\nDataFrame exported to Excel file: {output_file}")

    # Step 12: Print the sorted DataFrame
    print("\n--- Matches DataFrame (Sorted by Index) ---")
    print(df.to_string())
