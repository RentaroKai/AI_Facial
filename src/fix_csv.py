import sys
import csv
import re


def extract_info(json_str):
    # Use regex to extract '表情の名前' and '言いそうなセリフ'
    name_pattern = re.compile(r'[\"]*表情の名前[\"]*\s*:\s*[\"]+([^\"]+)[\"]+')
    line_pattern = re.compile(r'[\"]*言いそうなセリフ[\"]*\s*:\s*[\"]+([^\"]+)[\"]+')
    name_match = name_pattern.search(json_str)
    line_match = line_pattern.search(json_str)
    if not name_match:
        print(f"[DEBUG] Failed to extract '表情の名前' from: {json_str}")
    if not line_match:
        print(f"[DEBUG] Failed to extract '言いそうなセリフ' from: {json_str}")
    return (name_match.group(1) if name_match else '', line_match.group(1) if line_match else '')


def main():
    if len(sys.argv) < 3:
        print("Usage: python src/fix_csv.py <input_csv> <output_csv>")
        sys.exit(1)
    input_csv = sys.argv[1]
    output_csv = sys.argv[2]
    
    try:
        with open(input_csv, newline='', encoding='utf-8') as infile, open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
            # Assume the input CSV is tab-delimited
            reader = csv.DictReader(infile, delimiter='\t')
            # Define new header fields
            fieldnames = ["ファイル名", "ファイルパス", "表情の名前", "言いそうなセリフ"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            
            for row in reader:
                json_str = row.get("結果", "")
                # Debug print the row being processed
                print(f"[DEBUG] Processing row: {row}")
                emotion_name, line_text = extract_info(json_str)
                out_row = {
                    "ファイル名": row.get("ファイル名", ""),
                    "ファイルパス": row.get("ファイルパス", ""),
                    "表情の名前": emotion_name,
                    "言いそうなセリフ": line_text
                }
                writer.writerow(out_row)
        print(f"CSV processing completed. Output written to {output_csv}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main() 