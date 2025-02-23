import os
import csv
import json
import time
import re
from PySide6.QtCore import QThread, Signal
from gemini_api import upload_to_gemini, analyze_expression


def extract_info(json_str):
    """Extract '表情の名前' and '言いそうなセリフ' from JSON-like string"""
    name_pattern = re.compile(r'[\"]*表情の名前[\"]*\s*:\s*[\"]+([^\"]+)[\"]+')
    line_pattern = re.compile(r'[\"]*言いそうなセリフ[\"]*\s*:\s*[\"]+([^\"]+)[\"]+')
    name_match = name_pattern.search(json_str)
    line_match = line_pattern.search(json_str)
    return (name_match.group(1) if name_match else '', line_match.group(1) if line_match else '')


class ImageProcessingWorker(QThread):
    progress_signal = Signal(str)
    result_signal = Signal(dict)
    finished_signal = Signal()

    def __init__(self, file_paths, parent=None):
        super().__init__(parent)
        self.file_paths = file_paths

    def get_output_dir(self):
        """Get output directory from environment variable or use default"""
        output_dir = os.environ.get('OUTPUT_DIR', os.path.join(os.getcwd(), "output"))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"DEBUG: Created output directory at {output_dir}")
        return output_dir

    def run(self):
        output_rows = []
        output_dir = self.get_output_dir()

        for file_path in self.file_paths:
            file_name = os.path.basename(file_path)
            self.progress_signal.emit(f"Processing {file_name} ...")
            print(f"DEBUG: Starting processing file: {file_path}")
            try:
                # Upload file using Gemini API
                file_obj = upload_to_gemini(file_path, mime_type='image/jpeg')
                print(f"DEBUG: Uploaded {file_name} with URI: {file_obj.uri}")

                # Analyze the image using Gemini API
                response = analyze_expression(file_obj)
                print(f"DEBUG: Received analysis response for {file_name}")
                
                # Extract the JSON response
                result_text = response.text
                # Remove any markdown formatting if present (```json and ```)
                result_text = result_text.replace("```json", "").replace("```", "").strip()
                
                # Extract emotion name and line text
                emotion_name, line_text = extract_info(result_text)
                
                self.result_signal.emit({
                    "file_name": file_name, 
                    "path": file_path, 
                    "result": result_text,
                    "表情の名前": emotion_name,
                    "言いそうなセリフ": line_text
                })
                
                output_rows.append({
                    "ファイル名": file_name,
                    "ファイルパス": file_path,
                    "表情の名前": emotion_name,
                    "言いそうなセリフ": line_text
                })
                
            except Exception as e:
                error_message = f"Error processing {file_name}: {str(e)}"
                print(f"DEBUG: {error_message}")
                self.result_signal.emit({
                    "file_name": file_name,
                    "path": file_path,
                    "result": error_message,
                    "表情の名前": "",
                    "言いそうなセリフ": ""
                })
                output_rows.append({
                    "ファイル名": file_name,
                    "ファイルパス": file_path,
                    "表情の名前": "",
                    "言いそうなセリフ": ""
                })

        # Write output CSV file
        csv_file_path = os.path.join(output_dir, f"result_{int(time.time())}.csv")
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["ファイル名", "ファイルパス", "表情の名前", "言いそうなセリフ"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for row in output_rows:
                # Replace any tabs in the values with spaces to avoid formatting issues
                cleaned_row = {
                    k: str(v).replace('\t', ' ') for k, v in row.items()
                }
                writer.writerow(cleaned_row)
        print(f"DEBUG: CSV file written to {csv_file_path}")
        self.finished_signal.emit() 