import tkinter as tk
import customtkinter as ctk
import pyperclip
from pynput.keyboard import Key, Listener
import ollama as olm
import time
import threading
from duckduckgo_search import DDGS


class FloatingTextBoxApp:
    def __init__(self, root: ctk.CTk):
        print(root.winfo_screenwidth )
        self.root = root
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Window dimensions
        window_width = 500
        window_height = 210
        
        # Calculate position to center the window on the screen
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)

        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")  # Initial window size
        self.root.overrideredirect(True)  # Hide the window frame
        self.root.attributes("-topmost", True)  # Keep window on top
        self.root.resizable(True, True)  # Make window resizable

        self.is_visible = True  # Flag to track visibility of the floating textbox
        self.is_chatbox = False
        self.is_done = False
        self.new_x = x_position
        self.new_y = y_position

        # Create a container frame for the layout
        self.view = ctk.CTkFrame(self.root, width=1000, height=200)

        # Create the floating textbox
        self.textbox = ctk.CTkEntry(self.root, width=380, height=40, placeholder_text="Type a message...")
        self.textbox.grid(row=0, column=0, padx=5, pady=5)

        # Get available models from Ollama
        # self.models = [model['model'] for model in olm.list()['models']]
        self.models = ["gpt-4o-mini", "claude-3-haiku", "llama-3.1-70b", "mixtral-8x7b"]
        self.ModelMenu = ctk.CTkComboBox(self.root, width=100, height=40, values=self.models)
        self.ModelMenu.grid(row=0, column=1, padx=5, pady=5, sticky="w")  # Combo box next to the textbox

        # Progress bar for feedback
        self.progress_bar = ctk.CTkProgressBar(self.root, width=480,progress_color='gray')
        self.progress_bar.grid(row=1, column=0, columnspan=2, padx=10, pady=2)
        self.progress_bar.set(0)

        # Description box (initial message)
        self.description_box = ctk.CTkTextbox(self.root, width=480, height=320, state="normal", 
                                              fg_color="lightgray", text_color="black")
        self.description_box.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        self.description_box.insert("0.0", "Welcome to the Chat! Type a message below and press Enter.")
        self.description_box.configure(state="disabled")

        # Chatbox (hidden initially)
        self.chatbox = ctk.CTkTextbox(self.root, width=480, height=320, state="normal")
        self.chatbox.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        self.chatbox.grid_forget()  # Hide the chatbox initially

        # Copy button (hidden initially)
        self.copy_button = ctk.CTkButton(self.root, text="copy", height=10, width=20, command=self.copy_to_clipboard)
        self.copy_button.grid(row=2, column=1, padx=10, pady=10, sticky="e")
        self.copy_button.grid_forget()  # Hide the copy button initially

        # Variables for dragging window
        self._drag_data = {"x": 0, "y": 0}

        # Bind mouse events to move the window
        self.root.bind("<ButtonPress-1>", self.on_button_press)
        self.root.bind("<B1-Motion>", self.on_mouse_move)

        # Focus on textbox and handle key press for Enter
        self.textbox.focus_set()
        self.textbox.bind("<Return>", self.on_enter)

        # Set up pynput Listener
        self.listener = Listener(on_press=self.on_key_press)
        self.listener.start()

    def toggle_visibility(self):
        """Toggle the visibility of the floating textbox."""
        if self.is_visible:
            self.hide()
        else:
            self.show()

    # def genai(self, prompt, model):
    #     """Generate AI response based on prompt and model."""
    #     if model not in self.models:
    #         model = olm.pull(model)
    #         res = olm.generate(prompt=prompt, model=model)
    #     else:
    #         res = olm.generate(prompt=prompt, model=model)



    #     self.is_done = True
    #     self.display_message(res['response'])
    def genai(self,prompt,model):
    # models=["gpt-4o-mini", "claude-3-haiku", "llama-3.1-70b", "mixtral-8x7b"]
    # model=random.choice(models)
    # chatprompt = prompt_templat
    # e.substitute(prompt=prompt)
    # model = models[1]
        try:
            res = DDGS().chat(prompt,model=model)
        except Exception as e:
            return f"Error: {str(e)}"
    # res2 = AsyncDDGS.chat(prompt,model='gpt-40-mini')
        self.is_done = True
        self.display_message(res)
        # return model , res

    def genrate_response(self):
        """Simulate response generation with dynamic progress bar updates."""
        prompt = self.textbox.get()
        model = self.ModelMenu.get()
        self.is_done = False
        print(f"Generating for model: {model} with prompt: {prompt}")
        self.changeDecription()

        # self.genai(prompt,model)
        threading.Thread(target=self.genai, args=(prompt, model)).start()

        # Simulate loading progress
        for i in range(1, 500):
            self.progress_bar.set(i / 500)  # Update the progress bar
            self.root.update_idletasks()  # Update the GUI
            time.sleep(0.05)  # Simulate time delay
            if self.is_done or self.is_done==True:
                self.progress_bar.set(100)
                break

    def show(self):
        """Show the floating textbox."""
        self.root.deiconify()  # Show the window
        self.textbox.focus_set()  # Set focus back to the textbox
        self.is_visible = True

    def display_message(self, message):
        """Display the message in the chatbox."""
        if not self.is_chatbox:
            self.root.geometry(f"500x395+{self.new_x}+{self.new_y}")
            # self.root.geometry('500x395+1000+100')  # Resize the window when message appears
            self.description_box.grid_forget()  # Hide the description box
            self.chatbox.grid(row=2, column=0, columnspan=2, padx=10, pady=10)  # Show the chatbox
            self.copy_button.place(x=447, y=75)
            self.is_chatbox = True

        # Clear chatbox and insert the new message
        self.chatbox.delete("0.0", "end")
        self.chatbox.insert("0.0", message)

    def changeDecription(self):
        """Change the description text to 'Thinking...' while processing."""
        self.description_box.configure(state="normal")  # Make the description box editable
        self.description_box.delete("0.0", "end")  # Clear the current message
        self.description_box.insert("0.0", "Thinking...")  # Update the description box with "Thinking..."
        self.description_box.configure(state="disabled")  # Make it read-only again

    def on_enter(self, event):
        """Handle Enter key press."""
        message = self.textbox.get()
        if message:
            self.genrate_response()
            self.textbox.delete(0, tk.END)  # Clear the textbox after sending the message

    def show_toast(self, message):
            """Show a toast message for 2 seconds."""
            toast = tk.Toplevel(self.root)
            toast.overrideredirect(True)
            toast.attributes("-topmost", True)
            toast.geometry(f"+{self.root.winfo_x() + 450}+{self.root.winfo_y() + 550}")
            toast.wm_attributes("-transparentcolor", "white")
            label = ctk.CTkLabel(toast, text=message,bg_color='Black', corner_radius=5)
            label.pack(padx=1, pady=0.5)
            
            self.root.after(2000, toast.destroy)  # Destroy the toast after 2 seconds
            print(message)

    def copy_to_clipboard(self):
        """Copy the chat content to clipboard."""
        chatContent = self.chatbox.get('0.0', 'end-1c')
        pyperclip.copy(chatContent)
        self.show_toast("Copied")
        print("It's copied to Clipboard")

    def hide(self):
        """Hide the floating textbox."""
        self.root.withdraw()  # Hide the window
        self.is_visible = False

    def on_button_press(self, event):
        """Track the position where the mouse click occurred for dragging."""
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_mouse_move(self, event):
        """Move the window based on the mouse movement."""
        deltax = event.x - self._drag_data["x"]
        deltay = event.y - self._drag_data["y"]
        self.new_x = self.root.winfo_x() + deltax
        self.new_y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{self.new_x}+{self.new_y}")  # Update window position

    def on_key_press(self, key):
        """Handle key press events."""
        try:
            # Check if F7 is pressed
            if key == Key.f7:
                self.toggle_visibility()

            # Check if Alt and Space are pressed
            if key == Key.space and any([key == Key.alt_l, key == Key.alt_r]):
                self.toggle_visibility()

        except AttributeError:
            pass  # Handle special keys gracefully


# Main
if __name__ == "__main__":
    root = ctk.CTk()
    app = FloatingTextBoxApp(root)
    root.mainloop()
