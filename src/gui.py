from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QVBoxLayout, QListWidget, QTextEdit, QLabel, QFileDialog
from PySide6.QtCore import Qt
import os

from image_processing import ImageProcessingWorker
from history_manager import HistoryManager


class DragDropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            if os.path.isfile(path) and path.lower().endswith(('.jpg', '.jpeg')):
                self.addItem(path)
        event.acceptProposedAction()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("表情解析アプリケーション")
        self.history_manager = HistoryManager()
        self.worker = None
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # File selection button
        self.select_button = QPushButton("ファイル選択")
        self.select_button.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.select_button)

        # List widget for selected files
        self.file_list_widget = DragDropListWidget()
        layout.addWidget(self.file_list_widget)

        # Processing button
        self.process_button = QPushButton("解析実行")
        self.process_button.setStyleSheet("background-color: #2C7F20; color: white;")
        self.process_button.clicked.connect(self.start_processing)
        layout.addWidget(self.process_button)

        # Status label
        self.status_label = QLabel("未処理")
        layout.addWidget(self.status_label)

        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        # History text area
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        layout.addWidget(self.history_text)

        # Refresh history button
        self.refresh_history_button = QPushButton("履歴を更新")
        self.refresh_history_button.clicked.connect(self.update_history_display)
        layout.addWidget(self.refresh_history_button)

        # CSV folder open button
        self.open_csv_button = QPushButton("📁")
        self.open_csv_button.clicked.connect(self.open_csv_folder)
        layout.addWidget(self.open_csv_button)
        
        # Load initial history
        self.update_history_display()

    def open_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "画像ファイル選択", "", "Image Files (*.jpg *.jpeg *.JPG *.JPEG)")
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg')):
                self.file_list_widget.addItem(file)

    def start_processing(self):
        num_files = self.file_list_widget.count()
        if num_files == 0:
            self.status_label.setText("ファイルが選択されていません")
            return
        
        # Clear previous results
        self.results_text.clear()
        
        # Get file paths
        file_paths = [self.file_list_widget.item(i).text() for i in range(num_files)]
        
        # Create and setup worker
        self.worker = ImageProcessingWorker(file_paths)
        self.worker.progress_signal.connect(self.handle_progress)
        self.worker.result_signal.connect(self.handle_result)
        self.worker.finished_signal.connect(self.handle_finished)
        
        # Store current files for history
        self.current_files = file_paths
        self.current_results = []
        
        # Update UI state
        self.status_label.setText("解析中…")
        self.process_button.setEnabled(False)
        
        # Start processing
        self.worker.start()

    def handle_progress(self, message):
        self.status_label.setText(message)

    def handle_result(self, result):
        display_text = f"ファイル: {result['file_name']}\n"
        if "Error" in result.get('result', ''):
            display_text += f"結果: {result['result']}\n"
        else:
            display_text += f"表情の名前: {result['表情の名前']}\n"
            display_text += f"言いそうなセリフ: {result['言いそうなセリフ']}\n"
        display_text += "\n"
        self.results_text.append(display_text)
        
        # Store result for history
        self.current_results.append(result['result'])

    def handle_finished(self):
        self.status_label.setText("解析完了")
        self.process_button.setEnabled(True)
        
        # Add to history
        if hasattr(self, 'current_files') and hasattr(self, 'current_results'):
            self.history_manager.add_entry(self.current_files, self.current_results)
            delattr(self, 'current_files')
            delattr(self, 'current_results')
        
        self.update_history_display()
        self.file_list_widget.clear()

    def update_history_display(self):
        """Update the history display with the latest entries"""
        history_text = self.history_manager.get_formatted_history(max_entries=5)
        self.history_text.setText(history_text)

    def open_csv_folder(self):
        output_folder = os.path.join(os.getcwd(), "output")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print("outputフォルダが作成されました:", output_folder)
        os.startfile(output_folder)
        print("outputフォルダをエクスプローラーで開きました:", output_folder) 