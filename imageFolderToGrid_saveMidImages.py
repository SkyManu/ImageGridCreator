import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime


class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Grid Creator")

        # Variables
        self.input_folder = "images/"
        self.output_folder = "convertedImages/"
        self.pdf_file = ""
        self.resize_width = 800
        self.resize_height = 800
        self.border_size = 2
        self.columns = 6
        self.rows = 6

        # Create UI elements
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Select Input Folder:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        tk.Button(self.root, text="Browse", command=self.select_folder).grid(row=0, column=1, padx=10, pady=10)

        self.folder_label = tk.Label(self.root, text=f"Selected Folder: {self.input_folder}")
        self.folder_label.grid(row=0, column=2, padx=10, pady=10)

        tk.Label(self.root, text="Number of Cells:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.cell_slider = tk.Scale(self.root, from_=4, to_=6, orient="horizontal", resolution=1,
                                    label="Cells per Page")
        self.cell_slider.set(6)  # Default value for 36 cells (6x6 grid)
        self.cell_slider.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self.root, text="Generate PDF", command=self.generate_pdf).grid(row=2, column=0, columnspan=3,
                                                                                  padx=10, pady=20)

    def select_folder(self):
        self.input_folder = filedialog.askdirectory(initialdir="images/", title="Select Input Folder")
        if not self.input_folder:
            messagebox.showwarning("Warning", "No folder selected.")
        else:
            self.folder_label.config(text=f"Selected Folder: {self.input_folder}")

    def addBorder(self, image, border_size, color=(0, 0, 0)):
        """Añade un borde alrededor de la imagen."""
        bordered_image = Image.new('RGB',
                                   (image.width + 2 * border_size, image.height + 2 * border_size),
                                   color)
        bordered_image.paste(image, (border_size, border_size))
        return bordered_image

    def resizeImages(self):
        if not self.input_folder:
            messagebox.showwarning("Warning", "No input folder selected.")
            return

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        for item in os.listdir(self.input_folder):
            if item.lower().endswith(".png"):
                im = Image.open(os.path.join(self.input_folder, item))
                im = im.resize((self.resize_width, self.resize_height), Image.Resampling.LANCZOS)

                if im.mode == 'RGBA':
                    background = Image.new('RGB', (self.resize_width, self.resize_height),
                                           (255, 255, 255))  # Fondo blanco
                    background.paste(im, (0, 0), im)
                    im = background
                else:
                    im = im.convert('RGB')

                im = self.addBorder(im, self.border_size)
                new_image_name = os.path.splitext(item)[0] + '.jpg'
                im.save(os.path.join(self.output_folder, new_image_name), 'JPEG', quality=90)

    def createPDF(self):
        image_files = [f for f in os.listdir(self.output_folder) if f.lower().endswith('.jpg')]
        image_files.sort()

        num_cells = self.cell_slider.get()
        # Determine number of columns and rows based on number of cells
        if num_cells == 4:
            self.columns = 4
            self.rows = 4
        elif num_cells == 5:
            self.columns = 5
            self.rows = 5
        elif num_cells == 6:
            self.columns = 6
            self.rows = 6

        # Generate PDF file name with current date and time
        now = datetime.now()
        date_time_str = now.strftime("%Y%m%d_%H%M")
        self.pdf_file = f"image_grid_{date_time_str}.pdf"

        c = canvas.Canvas(self.pdf_file, pagesize=letter)
        page_width, page_height = letter
        cell_width = page_width / self.columns
        cell_height = page_height / self.rows
        margin = 0

        x_offset = margin
        y_offset = page_height - margin - cell_height

        for idx, img_path in enumerate(image_files):
            if idx >= self.columns * self.rows:
                c.showPage()
                x_offset = margin
                y_offset = page_height - margin - cell_height

            img_full_path = os.path.join(self.output_folder, img_path)
            c.drawImage(img_full_path, x_offset, y_offset, width=cell_width, height=cell_height)

            x_offset += cell_width
            if (idx + 1) % self.columns == 0:
                x_offset = margin
                y_offset -= cell_height

        c.save()

    def generate_pdf(self):
        self.resizeImages()
        self.createPDF()
        messagebox.showinfo("Success", f"PDF generated successfully!\nSaved as: {self.pdf_file}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()
