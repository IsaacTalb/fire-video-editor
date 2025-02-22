import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import re

# Set up the main window
root = tk.Tk()
root.title("Fire Your Video Editor || Isaac Talb")
root.geometry("400x300")

# Set global options for dialog widgets so that simpledialog uses these colors.
root.option_add("*Dialog.msg.foreground", "white")
root.option_add("*Dialog.msg.background", "black")
root.option_add("*Dialog.entry.foreground", "white")
root.option_add("*Dialog.entry.background", "black")

# Now the simpledialogs will use white text on a black background.

def split_video():
    # Open file dialog for selecting the video file
    file_path = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv"), ("All Files", "*.*")]
    )
    if not file_path:
        return

    # Prompt for segment length, title, and aspect ratio with simpledialogs
    segment_length = simpledialog.askinteger("Segment Length",
                                               "Enter segment length in seconds:",
                                               parent=root, minvalue=10, maxvalue=600)
    if segment_length is None:
        return

    title_base = simpledialog.askstring("Video Title",
                                        "Enter the title for the video:",
                                        parent=root) or "My Video"

    aspect_ratio = simpledialog.askstring("Aspect Ratio",
                                          "Enter aspect ratio (9:16 or 16:9):",
                                          parent=root)
    if aspect_ratio not in ["9:16", "16:9"]:
        messagebox.showerror("Invalid Input", "Invalid aspect ratio. Please enter 9:16 or 16:9.")
        return

    # Get the duration of the video
    duration = get_video_duration(file_path)
    if duration == 0:
        messagebox.showerror("Error", "Could not determine video duration.")
        return

    output_dir = os.path.dirname(file_path)
    base_filename = os.path.splitext(os.path.basename(file_path))[0]
    num_segments = int(duration // segment_length) + (1 if duration % segment_length > 0 else 0)

    for i in range(num_segments):
        start_time = i * segment_length
        part_label = f"Part {number_to_words(i+1)}"
        full_title = f"{title_base} - {part_label}"
        output_path = os.path.join(output_dir, f"{base_filename}_{part_label.replace(' ', '_')}.mp4")
        title_filter = create_title_filter(full_title, aspect_ratio)

        cmd = [
            'ffmpeg', '-i', file_path,
            '-vf', title_filter,
            '-ss', str(start_time), '-t', str(segment_length),
            '-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental',
            output_path
        ]
        print("Running command:", " ".join(cmd))
        subprocess.run(cmd)

    messagebox.showinfo("Success", "Video has been successfully split!")

def get_video_duration(file_path):
    result = subprocess.run(['ffmpeg', '-i', file_path],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = result.stderr.decode()
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", output)
    return sum(float(x) * 60 ** i for i, x in enumerate(reversed(match.groups()))) if match else 0

def number_to_words(n):
    words = {
        1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
        6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten",
        11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen",
        16: "Sixteen", 17: "Seventeen", 18: "Eighteen", 19: "Nineteen", 20: "Twenty"
    }
    return words.get(n, str(n))

def create_title_filter(title_text, aspect_ratio):
    # Adjust the font path as needed on your system.
    font_path = "/usr/share/fonts/truetype/noto/NotoSansMyanmar-Regular.ttf"
    if aspect_ratio == "9:16":
        return (
            "drawbox=x=0:y=80:w=iw:h=120:color=black@0.5:t=fill,"
            f"drawtext=fontfile={font_path}:text='{title_text}':"
            "x=(w-text_w)/2:y=120:fontcolor=white:fontsize=30"
        )
    else:
        return (
            "drawbox=x=0:y=20:w=iw:h=100:color=black@0.5:t=fill,"
            f"drawtext=fontfile={font_path}:text='{title_text}':"
            "x=(w-text_w)/2:y=50:fontcolor=white:fontsize=30"
        )

tk.Button(root, text="Select Video and Split", command=split_video, padx=10, pady=5).pack(pady=30)

root.mainloop()
