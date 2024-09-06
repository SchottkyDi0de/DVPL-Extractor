import customtkinter as ctk

class TaskMetadataFrame(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = ctk.CTkLabel(self, text="Metadata", height=20)
        self.label.pack()
        
        self.btn_copy = ctk.CTkButton(
            self, 
            text="Copy", 
            command=self.on_copy_click,
            height=20
        )

        self.text_box = ctk.CTkTextbox(self, wrap='none')
        self.text_box.pack(expand=True, fill="both")
        self.btn_copy.pack(fill="both", pady=5)

    def on_copy_click(self):
        self.clipboard_append(self.text_box.get('1.0', 'end'))
        
    def set_metadata(self, metadata: str):
        self.text_box.delete('1.0', 'end')
        self.text_box.insert('1.0', metadata)
