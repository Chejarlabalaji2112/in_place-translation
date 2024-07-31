import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from deep_translator import GoogleTranslator

HITE = fitz.pdfcolor["white"]

# This flag ensures that text will be dehyphenated after extraction.
textflags = fitz.TEXT_DEHYPHENATE

# Configure the desired translator
to_trans = GoogleTranslator(source="en", target="te")

class PDFViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Viewer")

        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack()

        self.pdf_document = None
        self.current_page = 0

        self.open_button = tk.Button(root, text="Open PDF", command=self.open_pdf)
        self.open_button.pack(side=tk.LEFT)

        self.prev_button = tk.Button(root, text="Previous", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(root, text="Next", command=self.next_page)
        self.next_button.pack(side=tk.LEFT)

        self.canvas.bind("<Button-1>", self.on_click)

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.pdf_document = fitz.open(file_path)
            self.current_page = 0
            self.show_page(self.current_page)

    def show_page(self, page_num):
        page = self.pdf_document.load_page(page_num)
        pix = page.get_pixmap()

        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img = ImageTk.PhotoImage(img)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.image = img

    def next_page(self):
        if self.pdf_document and self.current_page < len(self.pdf_document) - 1:
            self.current_page += 1
            self.show_page(self.current_page)

    def prev_page(self):
        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            self.show_page(self.current_page)

    def on_click(self, event):
        if not self.pdf_document:
            return

        x, y = event.x, event.y
        page = self.pdf_document.load_page(self.current_page)

        # Convert canvas coordinates to PDF coordinates
        page_width, page_height = page.rect.width, page.rect.height
        canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        pdf_x = x * page_width / canvas_width
        pdf_y = y * page_height / canvas_height

        # Get the text at the clicked position
        words = page.get_text("words")  # Get text with bounding boxes
        for word in words:
            if word[0] <= pdf_x <= word[2] and word[1] <= pdf_y <= word[3]:
                print(f"Clicked on text: {word[4]}")
                # Optional: overlay new text at the location
                text =  to_trans.translate(word[4])
                print(text)
                self.overlay_text(page, word[:4], text)
                self.show_page(self.current_page)
                break

    def overlay_text(self, page, bbox, text):
        rect = fitz.Rect(bbox)
        page.insert_text(rect.top_left, text, fontsize=20, color=(1, 0, 0))

if __name__ == "__main__":
    root = tk.Tk()
    viewer = PDFViewer(root)
    root.mainloop()
