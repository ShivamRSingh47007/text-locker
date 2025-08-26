import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pdf2image import convert_from_path
from PIL import Image
import os
import threading
selected_pdf = None
def browse_pdf():
    global selected_pdf
    selected_pdf = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if selected_pdf:
        pdf_label.config(text=f"Selected PDF: {os.path.basename(selected_pdf)}")
        start_btn.config(state="normal")
    else:
        pdf_label.config(text="No PDF selected")
        start_btn.config(state="disabled")
def start_conversion():
    if not selected_pdf:
        messagebox.showwarning("Warning", "Please select a PDF first!")
        return
    browse_btn.config(state="disabled")
    start_btn.config(state="disabled")
    threading.Thread(target=convert_pdf_to_images_to_pdf, daemon=True).start()
def convert_pdf_to_images_to_pdf():
    try:
        temp_folder = "temp_images"
        os.makedirs(temp_folder, exist_ok=True)
        images = convert_from_path(selected_pdf)
        total_pages = len(images)
        image_paths = []
        for i, img in enumerate(images):
            img_path = os.path.join(temp_folder, f"page_{i+1}.png")
            img.save(img_path, "PNG")
            image_paths.append(img_path)
            progress_bar['value'] = ((i+1)/total_pages) * 50
            status_label.config(text=f"Locking Texts: Page {i+1}/{total_pages}")
            root.update_idletasks()
        output_pdf = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not output_pdf:
            messagebox.showinfo("Cancelled", "Output PDF save cancelled")
            return
        pil_images = [Image.open(img_path).convert("RGB") for img_path in image_paths]
        pil_images[0].save(output_pdf, save_all=True, append_images=pil_images[1:])
        progress_bar['value'] = 100
        status_label.config(text="Locking Text Completed!")
        messagebox.showinfo("Success", f"PDF converted successfully!\nSaved as {output_pdf}")
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong: {e}")
    finally:
        for img_path in os.listdir(temp_folder):
            os.remove(os.path.join(temp_folder, img_path))
        os.rmdir(temp_folder)
        browse_btn.config(state="normal")
        start_btn.config(state="normal")
        progress_bar['value'] = 0
        status_label.config(text="Waiting for user action...")
root = tk.Tk()
root.title("Text:Locker - Lock PDFs Text")
root.geometry("550x300")
root.resizable(False, False)
tk.Label(root, text="Text:Locker - Lock PDFs Text", font=("Arial", 12)).pack(pady=10)
browse_btn = tk.Button(root, text="Select PDF", command=browse_pdf, width=25)
browse_btn.pack(pady=5)
pdf_label = tk.Label(root, text="No PDF selected", font=("Arial", 10))
pdf_label.pack(pady=5)
start_btn = tk.Button(root, text="Start Conversion", command=start_conversion, width=25, state="disabled")
start_btn.pack(pady=10)
style = ttk.Style()
style.theme_use('default')
style.configure("green.Horizontal.TProgressbar", troughcolor='white', background='green', thickness=20)
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", style="green.Horizontal.TProgressbar")
progress_bar.pack(pady=10)
progress_bar['maximum'] = 100
progress_bar['value'] = 0
status_label = tk.Label(root, text="Waiting for user action...", font=("Arial", 10))
status_label.pack(pady=5)
about_text = "Text:Locker - Made by Shivam Singh\nFor locking copy text\n"
tk.Label(root, text=about_text, font=("Arial", 9), fg="gray").pack(side="bottom", pady=5)
root.mainloop()
