import re
from datetime import datetime
import pandas as pd
from rapidfuzz import fuzz


def process_text_file(file_path):
    """
    Reads a text file, splits its content into words, and returns the words as a list.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        words = file.read().split()  # Read file content and split into words
    return words


def remove_punctuation(words):
    """
    Removes punctuation from a list of words.
    """
    punctuation_regex = r"[^\w\s]"  # Matches any character that is not a word or whitespace
    return [re.sub(punctuation_regex, "", word) for word in words]


def extract_matching_fields_with_context(words, regex, description, matches_with_context, field_name, is_regex, is_keyword, fuzzy_match_word=None, threshold=90):
    """
    Extracts words matching the given regex or via fuzzy matching, stores them in a dictionary with their indexes,
    and prints context based on the field type.
    """
    print(f"\n--- Matching fields for: {description} ---")

    for index, word in enumerate(words):  # Iterate through words with their indexes
        # Check regex or fuzzy match
        match_found = False
        if regex:
            match_found = re.match(regex, word)  # Use regex if provided
        elif fuzzy_match_word:
            match_found = fuzz.partial_ratio(word, fuzzy_match_word) >= threshold  # Use fuzzy matching if enabled

        if match_found:  # If a match is found
            # Determine context based on field type
            if field_name == "is_loi":
                context = [word]  # Return only the matched word
            elif field_name == "is_year":
                context = words[max(0, index - 2):index + 1]  # Two words before the match
            elif field_name in ["is_amount", "is_area"]:
                context = words[max(0, index - 3):index + 1]  # Three words before the match
            else:
                context = words[max(0, index - 3):index + 1] + words[index + 1:index + 4]  # Additional words

            # Store match and its index with the field flag
            matches_with_context[index] = {
                "word": word,
                "context": context,
                field_name: 1,  # Set the flag for this field type
                "is_regex": is_regex,  # Set regex indicator
                "is_keyword": is_keyword,  # Set keyword indicator
            }

            # Print the match with context
            context_str = " ".join(context)
            print(f"Matched Element: {word}, Index: {index}, Context: {context_str}")


# Main script
if __name__ == "__main__":
    # Replace 'output_surya_commune.txt' with the path to your text file
    file_path = 'output_surya_commune.txt'

    # Step 1: Read the words from the file
    all_text_list = process_text_file(file_path)

    # Step 2: Remove punctuation
    cleaned_elements = remove_punctuation(all_text_list)

    # Step 3: Define the LOI regex (only items starting with 2.)
    loi_regex = r"^2\.\d{2}\.\d{3}$"

    # Step 4: Define the year regex for years between 1980 and the current year
    current_year = datetime.now().year
    year_regex = fr"^(19(8[0-9]|9[0-9])|20(0[0-9]|1[0-9]|2[0-{current_year % 10}]))$"

    # Step 5: Define the Arabic words to match
    arabic_words = [
        ("الجريدة", "is_جريدة", True),  # Apply fuzzy matching
        ("الرسمية", "is_الرسمية", True),  # Apply fuzzy matching
        ("درهم", "is_amount", False),   # Exact matching
        ("متر", "is_area", False),      # Exact matching
        ("قرار", "is_قرار", False),     # Exact matching
        ("مقرر", "is_مقرر", False),     # Exact matching
        ("حكم", "is_حكم", False),       # Exact matching
    ]
    keyword_amount = "DH"

    # Step 6: Create a shared dictionary to store matches
    matches_with_context = {}

    # Step 7: Extract and print matching fields for LOI regex (using uncleaned list)
    extract_matching_fields_with_context(all_text_list, loi_regex, "LOI pattern (e.g., 2.22.645)", matches_with_context, "is_loi", is_regex=1, is_keyword=0)

    # Step 8: Extract and print matching fields for year regex (using cleaned list)
    extract_matching_fields_with_context(cleaned_elements, year_regex, f"Valid years between 1980 and {current_year}", matches_with_context, "is_year", is_regex=1, is_keyword=0)

    # Step 9: Apply fuzzy or exact matching for Arabic words and "DH"
    for arabic_word, field_name, use_fuzzy in arabic_words:
        extract_matching_fields_with_context(
            all_text_list,
            rf"\b{arabic_word}\b" if not use_fuzzy else None,  # Exact regex if not fuzzy
            f"Arabic word: {arabic_word}",
            matches_with_context,
            field_name,
            is_regex=0,
            is_keyword=1,
            fuzzy_match_word=arabic_word if use_fuzzy else None,  # Only apply fuzzy match for specific words
            threshold=90 if use_fuzzy else 0  # High threshold for fuzzy matching
        )

    extract_matching_fields_with_context(all_text_list, rf"\b{keyword_amount}\b", f"Keyword: {keyword_amount}", matches_with_context, "is_amount", is_regex=0, is_keyword=1)

    # Step 10: Ensure all boolean fields are present in the dictionary
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

    # Step 11: Convert the dictionary into a DataFrame
    df = pd.DataFrame.from_dict(matches_with_context, orient="index")
    df["context"] = df["context"].apply(lambda x: " ".join(x))  # Convert context list to string for readability

    # Step 12: Add new columns to the DataFrame
    df["extraction_regex"] = 0  # Initialize the 'extraction_regex' column with 0
    df["final_extraction"] = ""  # Initialize the 'final_extraction' column with an empty string

    # Step 13: Apply regex extraction to the 'context' column if 'extraction_regex' is not 0
    for idx, row in df.iterrows():
        if row["extraction_regex"] != 0:
            match = re.search(row["extraction_regex"], row["context"])
            df.at[idx, "final_extraction"] = match.group(0) if match else ""

    # Step 14: Sort the DataFrame by index
    df = df.sort_index()

    # Step 15: Export the DataFrame to an Excel file
    output_file = "matches_output.xlsx"
    df.to_excel(output_file, index=True, sheet_name="Matches")
    print(f"\nDataFrame exported to Excel file: {output_file}")

    # Step 16: Print the sorted DataFrame
    print("\n--- Matches DataFrame (Sorted by Index) ---")
    print(df.to_string())
