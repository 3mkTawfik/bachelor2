import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import subprocess
import os
import cv2
import shutil

class ObjectDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Object Detection App")
        self.runtime = 0
        # Fixed weights file path
        self.weights_file = "best.pt"

        # UI elements for input
        self.source_label = tk.Label(root, text="Source File:", font=('Arial', 14))
        self.source_label.pack(pady=(10, 5))

        self.source_entry = tk.Entry(root, width=40, font=('Arial', 12))
        self.source_entry.pack(pady=5)

        self.browse_button = tk.Button(root, text="Browse", command=self.browse_file, font=('Arial', 12))
        self.browse_button.pack(pady=(5, 10))

        # Label to display only the file name
        self.filename_label = tk.Label(root, text="", font=('Arial', 12), wraplength=400)
        self.filename_label.pack()

        # Button to run detection
        self.run_button = tk.Button(root, text="Run Detection", command=self.run_detection, font=('Arial', 14, 'bold'), bg='#4CAF50', fg='white')
        self.run_button.pack(pady=10)

        # UI elements for output
        self.output_label = tk.Label(root, text="Output:", font=('Arial', 14))
        self.output_label.pack(pady=(10, 5))

        # Label to display the output image or video
        self.output_image_label = tk.Label(root)
        self.output_image_label.pack()

        # Bind the close event to the reset_exp method
        root.protocol("WM_DELETE_WINDOW", self.reset_exp)

    def browse_file(self):
        # Open file dialog to select source file (image or video)
        file_path = filedialog.askopenfilename()
        if file_path:
            # Display full file path in the entry field
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, file_path)

            # Display only the file name in a separate label
            filename = os.path.basename(file_path)
            self.filename_label.config(text=f"File: {filename}")

    def run_detection(self):
        # Get the source file path
        source_file = self.source_entry.get()

        if source_file:
            # Construct the command for object detection
            command = f"python yolov5/detect.py --weights {self.weights_file} --img 640 --conf 0.25 --source {source_file}"
            subprocess.run(command, shell=True)

            # Extract the file name and extension
            file_name, file_extension = os.path.splitext(os.path.basename(source_file))

            # Assuming the output path pattern is yolov5\runs\detect\exp, exp2, exp3, ...
            if self.runtime == 0:
                output_path = "yolov5/runs/detect/exp"
                self.runtime = self.runtime + 2
            else:
                output_path = f"yolov5/runs/detect/exp{self.runtime}"
                self.runtime = self.runtime + 1

            # Generate the output file path based on the input file name and exp number
            output_file = os.path.join(output_path + f"/{file_name}{file_extension}")

            # Display the output image or video
            self.display_output(output_file)
        else:
            print("Please provide a source file.")

    def display_output(self, file_path):
        _, file_extension = os.path.splitext(file_path.lower())

        if file_extension in ['.jpg', '.png', '.jpeg']:
            # Display the output image using PIL
            image = Image.open(file_path)
            photo = ImageTk.PhotoImage(image)

            self.output_image_label.configure(image=photo)
            self.output_image_label.image = photo

        elif file_extension in ['.mp4', '.avi', '.mov']:
            # Display the output video using OpenCV
            cap = cv2.VideoCapture(file_path)

            if cap.isOpened():
                # Get video dimensions
                width = int(cap.get(3))
                height = int(cap.get(4))

                # Set a fixed display size
                display_width = 800
                display_height = 600

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(frame)

                    # Resize the image to fit within the fixed display size
                    resized_image = image.resize((display_width, display_height), Image.LANCZOS)

                    photo = ImageTk.PhotoImage(resized_image)

                    self.output_image_label.config(width=display_width, height=display_height)
                    self.output_image_label.configure(image=photo)
                    self.output_image_label.image = photo

                    self.root.update_idletasks()  # Update the GUI to show the new frame
                    self.root.update()

                cap.release()
            else:
                print(f"Failed to open the video file: {file_path}")
        else:
            print("Unsupported file format for display.")

    def reset_exp(self):
    # Reset exp number to 1 when the application is closed
        output_path = "yolov5/runs/detect/"

    # Get a list of all files and directories in the directory
        files_and_dirs = os.listdir(output_path)

    # Iterate over the files and directories and delete each one
        for item in files_and_dirs:
            item_path = os.path.join(output_path, item)
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                # Remove the contents of the directory
                    for subitem in os.listdir(item_path):
                        subitem_path = os.path.join(item_path, subitem)
                        if os.path.isfile(subitem_path):
                            os.remove(subitem_path)
                        elif os.path.isdir(subitem_path):
                            os.rmdir(subitem_path)
                # Remove the directory itself after its contents are deleted
                    os.rmdir(item_path)
            except Exception as e:
                print(f"Error deleting {item_path}: {e}")

        self.root.destroy()



if __name__ == "__main__":
    root = tk.Tk()
    app = ObjectDetectionApp(root)
    root.mainloop()
