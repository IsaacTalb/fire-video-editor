import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import re

def split_video():
    # Open a file dialog to select video
    file_path = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=[("Video Files", "*.mp4;*.avi;*.mkv;*.mov;*.wmv;*.flv"), ("All Files", "*.*")]
    )
    if not file_path:
        return  # User canceled the selection

    try:
        # Ask user for segment length (default is 59 sec)
        segment_length = simpledialog.askinteger(
            "Segment Length", "Enter segment length in seconds:", minvalue=10, maxvalue=600
        )
        if not segment_length:
            return  # User canceled input

        # Ask user for the base title
        title_base = simpledialog.askstring("Video Title", "Enter the title for the video:")
        if not title_base:
            title_base = "Video"  # Provide a default if nothing is entered

        duration = get_video_duration(file_path)  # Get the total duration of the video
        output_dir = os.path.dirname(file_path)  # Save clips in the same directory as the input video
        base_filename = os.path.splitext(os.path.basename(file_path))[0]  # Filename without extension

        num_segments = int(duration // segment_length) + (1 if duration % segment_length > 0 else 0)

        for i in range(num_segments):
            start_time = i * segment_length
            # Create a human-readable part label (Part One, Part Two, etc.)
            part_label = f"Part {number_to_words(i+1)}"
            # Construct the full title text
            title_text = f"{title_base} - {part_label}"
            output_path = os.path.join(output_dir, f"{base_filename}_{part_label.replace(' ', '_')}.mp4")

            # Construct the filter chain:
            # 1. drawbox: draws a black box covering the top 100 pixels of the video.
            # 2. drawtext: overlays the title text in white, centered horizontally and vertically within the box.
            #
            # Adjust the font file path and font size as needed.
            title_filter = (
                "drawbox=x=0:y=0:w=iw:h=100:color=black@1:t=fill,"
                "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"text='{title_text}':"
                "x=(w-text_w)/2:"
                "y=(100-text_h)/2:"
                "fontcolor=white:fontsize=24"
            )


            # Use ffmpeg to split the video and apply the filter
            cmd = [
                'ffmpeg',
                '-i', file_path,
                '-ss', str(start_time),
                '-t', str(segment_length),
                '-vf', title_filter,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-strict', 'experimental',
                output_path
            ]
            # Optional: print or log the command for debugging purposes
            print("Running command:", " ".join(cmd))
            subprocess.run(cmd)

        messagebox.showinfo("Success", "Video has been successfully split!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to split video:\n{str(e)}")


def get_video_duration(file_path):
    result = subprocess.run(['ffmpeg', '-i', file_path],
                            stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    output = result.stderr.decode()
    # Use a regular expression to find the duration in the output.
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", output)
    if match:
        try:
            h, m, s = match.groups()
            return float(h) * 3600 + float(m) * 60 + float(s)
        except ValueError as e:
            print(f"Error parsing duration: {e}")
            return 0
    else:
        print("Could not find duration in video file.")
        return 0


def number_to_words(n):
    """
    A simple function to convert small integers to words.
    For example, 1 -> "One", 2 -> "Two", etc.
    Extend this function if you expect more than 10 parts.
    """
    words = {
        1: "One", 2: "Two", 3: "Three", 4: "Four",
        5: "Five", 6: "Six", 7: "Seven", 8: "Eight",
        9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve",
        13: "Thirteen", 14: "Fourteen", 15: "Fifteen",
        16: "Sixteen", 17: "Seventeen", 18: "Eighteen",
        19: "Nineteen", 20: "Twenty", 21: "Twenty One",
        22: "Twenty Two", 23: "Twenty Three", 24: "Twenty Four",
        25: "Twenty Five", 26: "Twenty Six", 27: "Twenty Seven",
        28: "Twenty Eight", 29: "Twenty Nine", 30: "Thirty",
        31: "Thirty One", 32: "Thirty Two", 33: "Thirty Three",
        34: "Thirty Four", 35: "Thirty Five", 36: "Thirty Six",
        37: "Thirty Seven", 38: "Thirty Eight", 39: "Thirty Nine",
        40: "Fourty", 41: "Fourty One", 42: "Fourty Two",
        43: "Fourty Three", 44: "Fourty Four", 45: "Fourty Five",
        46: "Fourty Six", 47: "Fourty Seven", 48: "Fourty Eight",
        49: "Fourty Nine", 50: "Fifty", 51: "Fifty One",
        52: "Fifty Two", 53: "Fifty Three", 54: "Fifty Four",
        55: "Fifty Five", 56: "Fifty Six", 57: "Fifty Seven",
        58: "Fifty Eight", 59: "Fifty Nine", 60: "Sixty",
        61: "Sixty One", 62: "Sixty Two", 63: "Sixty Three",
        64: "Sixty Four", 65: "Sixty Five", 66: "Sixty Six",
        67: "Sixty Seven", 68: "Sixty Eight", 69: "Sixty Nine",
        70: "Seventy"
    }
    return words.get(n, str(n))


# Create GUI Window
root = tk.Tk()
root.title("Video Splitter")
root.geometry("300x200")

btn_select = tk.Button(root, text="Select Video and Split", command=split_video, padx=10, pady=5)
btn_select.pack(pady=30)

root.mainloop()
