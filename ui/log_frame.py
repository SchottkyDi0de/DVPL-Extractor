import customtkinter as ctk


class CustomLogFrame(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.task_font = ctk.CTkFont(family="Cascadia Code", size=12)
        self.log_font = ctk.CTkFont(family="Cascadia Code", size=12)

        self.log = ctk.CTkTextbox(self, font=self.log_font, wrap='none')
        self.task = ctk.CTkTextbox(
            self, 
            text_color='gray', 
            height=30,
            font=self.task_font
        )
        self.label = ctk.CTkLabel(self, text="Log", height=20)
        self.task_label = ctk.CTkLabel(self, text="Current Task", height=20)
        self.progress_bar_label = ctk.CTkLabel(self, text="wait for task", height=15)
        self.progress_bar = ctk.CTkProgressBar(self, height=10, progress_color='orange')
        self.progress_bar.set(1)

        self.label.pack()
        self.log.pack(expand=True, fill="both")
        self.task_label.pack()
        self.task.pack(fill="both")
        self.progress_bar_label.pack()
        self.progress_bar.pack(fill="both", anchor='sw', pady=5)
        
    def set_task(self, task: str):
        self.task.delete('1.0', 'end')
        self.task.insert('1.0', task)

    def set_pb_value(self, value: int, max: int):
        if max <= 0:
            max = 1
        
        normalized_value = value / max
        if normalized_value >= 1:
            normalized_value = 1
            
            self.progress_bar.configure(progress_color="green")
            self.progress_bar_label.configure(text_color="green", text="Done!")
        else:
            self.progress_bar.configure(progress_color="orange")
            self.progress_bar_label.configure(text_color="orange", text=f"processing... ({normalized_value*100:.2f}%) - {value}/{max}")
        
        self.progress_bar.set(normalized_value)
    
    def set_state_unpack_DVPL(self):
        self.progress_bar.configure(progress_color="green")
        self.progress_bar_label.configure(text_color="green", text="Ready to Unpack!")
        
    def set_state_unpack_DVPD(self):
        self.progress_bar.configure(progress_color="green")
        self.progress_bar_label.configure(text_color="green", text="Ready to Unpack!")

    def set_state_pack_DVPL(self):
        self.progress_bar.configure(progress_color="green")
        self.progress_bar_label.configure(text_color="green", text="Ready to Pack!")

    def set_state_default(self):
        self.progress_bar.configure(progress_color="orange")
        self.progress_bar_label.configure(text_color="white", text="wait for task")

    def set_state_none_DVPD(self):
        self.progress_bar.configure(progress_color="red")
        self.progress_bar_label.configure(text_color="red", text="DVPD file not found!")

    def add_log(self, log: str, prefix: str = "[app]: "):
        self.log.insert('end', prefix + log + '\n')
        self.log.see('end')
