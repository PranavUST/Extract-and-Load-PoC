import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
import threading

class InputSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Data Ingestion Input Selector")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        self.selected_mode = None
        self.config_file = None

        self.setup_ui()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(main_frame, text="Choose Data Input Method",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Input method selection
        self.mode_var = tk.StringVar(value="API")

        # API Radio button
        api_frame = ttk.LabelFrame(main_frame, text="REST API", padding="10")
        api_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        api_radio = ttk.Radiobutton(api_frame, text="Extract data from REST API",
                                   variable=self.mode_var, value="API")
        api_radio.grid(row=0, column=0, sticky=tk.W)

        api_desc = ttk.Label(api_frame, text="Fetch data from a REST API endpoint",
                            foreground="gray")
        api_desc.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # SFTP Radio button (commented for now)
        # sftp_frame = ttk.LabelFrame(main_frame, text="SFTP/FTP", padding="10")
        # sftp_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        # sftp_radio = ttk.Radiobutton(sftp_frame, text="Extract data from SFTP/FTP",
        #                             variable=self.mode_var, value="SFTP")
        # sftp_radio.grid(row=0, column=0, sticky=tk.W)
        # sftp_desc = ttk.Label(sftp_frame, text="Download files from SFTP/FTP server",
        #                      foreground="gray")
        # sftp_desc.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # Config file selection
        config_frame = ttk.LabelFrame(main_frame, text="Configuration File", padding="10")
        config_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 5))

        self.config_label = ttk.Label(config_frame, text="No config file selected")
        self.config_label.grid(row=0, column=0, sticky=tk.W)

        config_button = ttk.Button(config_frame, text="Browse Config File",
                                  command=self.browse_config)
        config_button.grid(row=1, column=0, pady=(10, 0))

        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(30, 0))

        run_button = ttk.Button(button_frame, text="Run Pipeline",
                               command=self.run_pipeline)
        run_button.grid(row=0, column=0, padx=(0, 10))

        cancel_button = ttk.Button(button_frame, text="Cancel",
                                  command=self.root.quit)
        cancel_button.grid(row=0, column=1)

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

        # Run pipeline in a separate thread to keep GUI responsive
        threading.Thread(target=self._run_pipeline_thread, daemon=True).start()

    def _run_pipeline_thread(self):
        try:
            if self.selected_mode == "API":
                # Import here to avoid circular imports
                from src.logging_utils import setup_logging
                from src.pipeline import DataPipeline

                setup_logging("INFO", "pipeline.log")
                pipeline = DataPipeline(self.config_file)
                pipeline.run()
                self.status_label.config(text="Pipeline completed successfully!")
                messagebox.showinfo("Success", "Data extraction completed successfully!")
            else:
                # Placeholder for SFTP/FTP logic
                self.status_label.config(text="SFTP/FTP not implemented yet.")
                messagebox.showinfo("Info", "SFTP/FTP extraction coming soon!")
        except Exception as e:
            self.status_label.config(text="Pipeline failed!")
            messagebox.showerror("Error", f"Pipeline execution failed: {str(e)}")

    def show(self):
        self.root.mainloop()
        return self.selected_mode, self.config_file

if __name__ == "__main__":
    selector = InputSelector()
    mode, config = selector.show()
