import os
import json
from datetime import datetime


class HistoryManager:
    def __init__(self, history_file="history.json"):
        self.history_file = history_file
        self.ensure_history_file()

    def ensure_history_file(self):
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)

    def add_entry(self, files_processed, results):
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []

        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "files_processed": files_processed,
            "results": results
        }
        
        history.append(entry)
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def get_formatted_history(self, max_entries=5):
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            return "履歴なし"

        if not history:
            return "履歴なし"

        formatted_text = ""
        for entry in reversed(history[-max_entries:]):
            formatted_text += f"解析実行: {entry['timestamp']}\n"
            for file_name, result in zip(entry['files_processed'], entry['results']):
                formatted_text += f"  - {file_name}: {result}\n"
            formatted_text += "\n"

        return formatted_text.strip()

    def clear_history(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False) 