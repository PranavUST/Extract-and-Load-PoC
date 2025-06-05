import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
import threading
import sys

# Ensure project root is in sys.path for src imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from run_pipeline import run_ingestion

class InputSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Data Ingestion Input Selector")
        self.root.geometry("330x600")
        self.root.resizable(False, False)
        self.selected_mode = None
        self.config_file = None
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        title_label = ttk.Label(main_frame, text="Choose Data Input Method",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        self.mode_var = tk.StringVar(value="API")

        # API Radio button
        api_frame = ttk.LabelFrame(main_frame, text="REST API", padding="10")
        api_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Radiobutton(api_frame, text="Extract data from REST API",
                        variable=self.mode_var, value="API").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(api_frame, text="Fetch data from a REST API endpoint",
                  foreground="gray").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # SFTP Radio button
        sftp_frame = ttk.LabelFrame(main_frame, text="SFTP/FTP", padding="10")
        sftp_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Radiobutton(sftp_frame, text="Extract data from SFTP/FTP",
                        variable=self.mode_var, value="SFTP").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(sftp_frame, text="Download files from SFTP/FTP server",
                  foreground="gray").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # Config file selection
        config_frame = ttk.LabelFrame(main_frame, text="Configuration File", padding="10")
        config_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 5))
        self.config_label = ttk.Label(config_frame, text="No config file selected")
        self.config_label.grid(row=0, column=0, sticky=tk.W)
        ttk.Button(config_frame, text="Browse Config File",
                   command=self.browse_config).grid(row=1, column=0, pady=(10, 0))

        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(30, 0))
        ttk.Button(button_frame, text="Run Pipeline",
                   command=self.run_pipeline).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel",
                   command=self.root.quit).grid(row=0, column=1)

        # Status frame
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        self.status_label = ttk.Label(self.status_frame, text="Ready to run pipeline")
        self.status_label.grid(row=0, column=0)

    def browse_config(self):
        filetypes = [("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
        filename = filedialog.askopenfilename(
            title="Select Configuration File",
            initialdir="config",
            filetypes=filetypes
        )
        if filename:
            self.config_file = filename
            display_name = os.path.basename(filename)
            self.config_label.config(text=f"Selected: {display_name}")

    def run_pipeline(self):
        if not self.config_file:
            messagebox.showerror("Error", "Please select a configuration file")
            return

        self.selected_mode = self.mode_var.get()
        self.status_label.config(text=f"Running {self.selected_mode} pipeline...")
        self.root.update()
        threading.Thread(target=self._run_pipeline_thread, daemon=True).start()

    def _run_pipeline_thread(self):
        try:
            from src.logging_utils import setup_logging
            setup_logging("INFO", "pipeline.log")
            run_ingestion(self.config_file)
            self.status_label.config(text="Pipeline completed successfully!", foreground="green")
            messagebox.showinfo("Success", "Data extraction completed successfully!")
        except Exception as e:
            self.status_label.config(text="Pipeline failed!", foreground="red")
            messagebox.showerror("Error", f"Pipeline execution failed: {str(e)}")

    def show(self):
        self.root.mainloop()
        return self.selected_mode, self.config_file

if __name__ == "__main__":
    selector = InputSelector()
    mode, config = selector.show()
