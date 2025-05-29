import sys
import os
import re
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QTextEdit

class GoogleDorkGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.related_dorks_list = []
        self.generated_dork = ""
        self.initUI()
        self.load_related_dorks()

    def initUI(self):
        self.setWindowTitle('Google Dork Generator')
        self.setGeometry(100, 100, 520, 550)

        layout = QVBoxLayout()

        # Target Domain
        self.domain_label = QLabel('Target Domain:')
        self.domain_entry = QLineEdit()
        layout.addWidget(self.domain_label)
        layout.addWidget(self.domain_entry)

        # Search Parameters
        self.inurl_label = QLabel('inurl: (Search for text in URL path)')
        self.inurl_entry = QLineEdit()
        layout.addWidget(self.inurl_label)
        layout.addWidget(self.inurl_entry)

        self.intitle_label = QLabel('intitle: (Search for text in the title tag)')
        self.intitle_entry = QLineEdit()
        layout.addWidget(self.intitle_label)
        layout.addWidget(self.intitle_entry)

        self.filetype_label = QLabel('filetype: (Search for specific file types, multiple separated by space or comma)')
        self.filetype_entry = QLineEdit()
        layout.addWidget(self.filetype_label)
        layout.addWidget(self.filetype_entry)

        self.intext_label = QLabel('intext: (Search for specific text within the page, multiple separated by space or comma)')
        self.intext_entry = QLineEdit()
        layout.addWidget(self.intext_label)
        layout.addWidget(self.intext_entry)

        self.cache_label = QLabel('cache: (View Google\'s cached version of a page)')
        self.cache_entry = QLineEdit()
        layout.addWidget(self.cache_label)
        layout.addWidget(self.cache_entry)

        self.related_label = QLabel('related: (Find similar sites)')
        self.related_entry = QLineEdit()
        layout.addWidget(self.related_label)
        layout.addWidget(self.related_entry)

        self.link_label = QLabel('link: (Find sites that link to a specific page)')
        self.link_entry = QLineEdit()
        layout.addWidget(self.link_label)
        layout.addWidget(self.link_entry)

        # Buttons
        self.generate_button = QPushButton('Generate Dork')
        self.generate_button.clicked.connect(self.generate_dork)
        layout.addWidget(self.generate_button)

        self.copy_button = QPushButton('Copy to Clipboard')
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(self.copy_button)

        # Related Dorks Display (Read-only QTextEdit)
        self.related_dorks_display = QTextEdit()
        self.related_dorks_display.setReadOnly(True)
        self.related_dorks_display.setPlaceholderText("Related Google Dorks will appear here based on your inputs...")
        layout.addWidget(self.related_dorks_display)

        self.setLayout(layout)

    def load_related_dorks(self):
        # Load related dorks from relatedDorks.txt in the same directory
        filename = "relatedDorks.txt"
        if not os.path.isfile(filename):
            self.related_dorks_list = []
            return
        try:
            with open(filename, "r", encoding="utf-8") as f:
                self.related_dorks_list = [line.strip() for line in f if line.strip()]
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load related dorks file:\n{str(e)}")
            self.related_dorks_list = []

    def _split_inputs(self, text):
        # Splits input on commas and/or spaces and strips each part, ignoring empty strings
        if not text:
            return []
        parts = re.split(r'[,\s]+', text)
        return [part.strip() for part in parts if part.strip()]

    def generate_dork(self):
        parts = []

        domain = self.domain_entry.text().strip()
        # If domain is exactly two letters and no dot, treat as country code for site:
        if re.fullmatch(r'[a-zA-Z]{2}', domain):
            parts.append(f'site:.{domain.lower()}')
        elif domain:
            parts.append(f'site:.{domain.lower()}')

        inurl_text = self.inurl_entry.text().strip()
        if inurl_text:
            inurl_parts = self._split_inputs(inurl_text)
            for val in inurl_parts:
                parts.append(f'inurl:"{val}"')

        intitle_text = self.intitle_entry.text().strip()
        if intitle_text:
            intitle_parts = self._split_inputs(intitle_text)
            for val in intitle_parts:
                parts.append(f'intitle:"{val.title()}"')

        filetype_text = self.filetype_entry.text().strip()
        if filetype_text:
            filetype_parts = self._split_inputs(filetype_text)
            for val in filetype_parts:
                parts.append(f'filetype:"{val}"')

        intext_text = self.intext_entry.text().strip()
        if intext_text:
            intext_parts = self._split_inputs(intext_text)
            for val in intext_parts:
                parts.append(f'intext:"{val}"')

        cache_text = self.cache_entry.text().strip()
        if cache_text:
            parts.append(f'cache:"{cache_text}"')

        related_text = self.related_entry.text().strip()
        if related_text:
            parts.append(f'related:"{related_text}"')

        link_text = self.link_entry.text().strip()
        if link_text:
            parts.append(f'link:"{link_text}"')

        self.generated_dork = " ".join(parts)
        QMessageBox.information(self, 'Generated Dork', self.generated_dork)

        # Update related dorks display based on user inputs
        self.update_related_dorks_display()

    def update_related_dorks_display(self):
        # Gather keywords from relevant fields to filter related dorks
        keywords = set()

        # Collect keywords from domain, inurl, intitle, intext fields (split by space/comma)
        for entry in [self.domain_entry, self.inurl_entry, self.intitle_entry, self.intext_entry]:
            text = entry.text().strip()
            if text:
                words = self._split_inputs(text.lower())
                keywords.update(words)

        # If no keywords, show all or empty
        if not keywords:
            self.related_dorks_display.setPlainText("No input keywords detected to find related dorks.")
            return

        # Filter related dorks that contain any keyword (case-insensitive)
        matched_dorks = []
        for dork in self.related_dorks_list:
            dork_lower = dork.lower()
            if any(k in dork_lower for k in keywords):
                matched_dorks.append(dork)

        # Show top 10 related dorks or message if none found
        if matched_dorks:
            display_text = "\n\n".join(matched_dorks[:10])
        else:
            display_text = "No related dorks found for the given inputs."

        self.related_dorks_display.setPlainText(display_text)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        if self.generated_dork:
            clipboard.setText(self.generated_dork)
            QMessageBox.information(self, 'Copied', 'Dork copied to clipboard!')
        else:
            QMessageBox.warning(self, 'Warning', 'Please generate the dork before copying.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GoogleDorkGenerator()
    ex.show()
    sys.exit(app.exec_())

