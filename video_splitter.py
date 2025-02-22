import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import re

def split_video():
    file_path = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv"), ("All Files", "*.*")]
    )
    if not file_path:
        return

    try:
        # Prompt for parameters using modal dialogs
        segment_length = simpledialog.askinteger("Segment Length",
                                                   "Enter segment length in seconds:",
                                                   parent=root, minvalue=10, maxvalue=600)
        if segment_length is None:
            return

        title_base = simpledialog.askstring("Video Title",
                                            "Enter the title for the video:",
                                            parent=root) or "Video"

        aspect_ratio = simpledialog.askstring("Aspect Ratio",
                                              "Enter aspect ratio (9:16 for Portrait, 16:9 for Landscape):",
                                              parent=root)
        if aspect_ratio not in ["9:16", "16:9"]:
            messagebox.showerror("Invalid Input", "Invalid aspect ratio. Please enter 9:16 or 16:9.")
            return

        # Optional: prompt for a section to cut out
        cut_out = messagebox.askyesno("Cut Out Section", "Do you want to cut out some seconds or minutes from your video?")
        cut_start, cut_end = None, None
        if cut_out:
            cut_start_str = simpledialog.askstring("Cut Start",
                                                    "Enter start time of the part to cut (HH:MM:SS):",
                                                    initialvalue="00:00:00", parent=root)
            cut_start = convert_to_seconds(cut_start_str)
            cut_end_str = simpledialog.askstring("Cut End",
                                                  "Enter end time of the part to cut (HH:MM:SS):",
                                                  initialvalue="00:00:04", parent=root)
            cut_end = convert_to_seconds(cut_end_str)

        duration = get_video_duration(file_path)
        if duration == 0:
            messagebox.showerror("Error", "Could not determine video duration.")
            return

        output_dir = os.path.dirname(file_path)
        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        num_segments = int(duration // segment_length) + (1 if duration % segment_length > 0 else 0)

        for i in range(num_segments):
            start_time = i * segment_length
            end_time = min(start_time + segment_length, duration)

            # Adjust start and end if cutting out a section
            if cut_start is not None and cut_end is not None:
                if cut_start <= start_time < cut_end:
                    start_time = cut_end
                if cut_start < end_time <= cut_end:
                    end_time = cut_start
            if end_time - start_time <= 0:
                continue

            part_label = f"Part {number_to_words(i+1)}"
            full_title = f"{title_base} - {part_label}"
            output_path = os.path.join(output_dir, f"{base_filename}_{part_label.replace(' ', '_')}.mp4")

            # Build filter chain: if 9:16, apply a crop filter and then a title overlay.
            font_path = "/usr/share/fonts/truetype/noto/NotoSansMyanmar-Regular.ttf"  # adjust as needed
            if aspect_ratio == "9:16":
                # Crop: from a landscape source, crop a portrait region centered horizontally.
                crop_filter = "crop=ih*9/16:ih:(iw-ih*9/16)/2:0"
                # Overlay: add a title box at the top; adjust y-position if needed.
                title_filter = (
                    "drawbox=x=0:y=0:w=iw:h=50:color=black@0.5:t=fill,"
                    f"drawtext=fontfile={font_path}:text='{full_title}':"
                    "x=(w-text_w)/2:y=(50-text_h)/2:fontcolor=white:fontsize=24"
                )
                full_filter = f"{crop_filter},{title_filter}"
            else:
                # For 16:9, no crop is applied.
                title_filter = (
                    "drawbox=x=0:y=20:w=iw:h=100:color=black@0.5:t=fill,"
                    f"drawtext=fontfile={font_path}:text='{full_title}':"
                    "x=(w-text_w)/2:y=50:fontcolor=white:fontsize=30"
                )
                full_filter = title_filter

            cmd = [
                'ffmpeg', '-i', file_path,
                '-vf', full_filter,
                '-ss', str(start_time), '-to', str(end_time),
                '-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental',
                output_path
            ]
            print("Running command:", " ".join(cmd))
            subprocess.run(cmd)

        messagebox.showinfo("Success", "Yay! Your video is ready, sweetheart! Now go show it off!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to split video:\n{str(e)}")

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

def convert_to_seconds(time_str):
    h, m, s = map(int, time_str.split(":"))
    return h * 3600 + m * 60 + s

root = tk.Tk()
root.title("Fire Your Video Editor || Isaac Talb")
root.geometry("300x200")

tk.Button(root, text="Select Video and Split", command=split_video, padx=10, pady=5).pack(pady=30)
root.mainloop()
