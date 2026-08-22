#!/usr/bin/env python3
import os
import subprocess
import shlex

def transcode_and_import():
    if 'resolve' not in globals():
        print("Error: This script must be executed from inside DaVinci Resolve's Workspace menu.")
        return

    project_manager = resolve.GetProjectManager()
    current_project = project_manager.GetCurrentProject()
    
    if not current_project:
        print("Please open a project first!")
        return
        
    media_pool = current_project.GetMediaPool()
    
    # 1. Multi-Format Linux File Picker
    try:
        zenity_cmd = [
            "zenity", "--file-selection", "--multiple", 
            "--file-filter=All Media Formats | *.mp4 *.mp3 *.mkv *.mov *.webm *.flv *.m4a *.wav *.ogg *.aac",
            "--title=Select Media Files to Transcode & Import"
        ]
        choice = subprocess.check_output(zenity_cmd, text=True).strip()
        file_paths = choice.split("|")
    except subprocess.CalledProcessError:
        return

    valid_files = [f for f in file_paths if f]
    if not valid_files:
        return

    total_files = len(valid_files)
    imported_clips = []
    shell_commands = []
    
    # 2. Build Commands with Advanced UI Layout Styling
    for index, path in enumerate(valid_files):
        directory = os.path.dirname(path)
        filename = os.path.basename(path)
        name_without_ext, ext = os.path.splitext(filename)
        ext = ext.lower()
        
        output_path = os.path.join(directory, f"{name_without_ext}_encoded.mov")
        
        audio_only_exts = ['.mp3', '.m4a', '.wav', '.ogg', '.aac', '.flac']
        if ext in audio_only_exts:
            ffmpeg_args = "-vn -acodec pcm_s16be -q:a 0 -f mov"
            format_badge = "<span foreground='#3498db' weight='bold'>[AUDIO]</span>"
        else:
            ffmpeg_args = "-vcodec mjpeg -q:v 2 -acodec pcm_s16be -q:a 0 -f mov"
            format_badge = "<span foreground='#e67e22' weight='bold'>[VIDEO]</span>"

        safe_input = shlex.quote(path)
        safe_output = shlex.quote(output_path)
        
        # Styled UI text variables with rich typography
        display_text = (
            f"<span foreground='#2ecc71' weight='bold'>Processing Batch:</span> "
            f"<b>File {index + 1} of {total_files}</b>\\n\\n"
            f"{format_badge} <span size='large' weight='bold'>{filename}</span>\\n"
            f"<span foreground='#7f8c8d' size='small'>Target: {output_path}</span>"
        )

        # Using printf instead of echo prevents shell interpolation parsing crashes
        file_command = (
            f"printf '# %b\\n' {shlex.quote(display_text)} && "
            f"ffmpeg -y -i {safe_input} {ffmpeg_args} {safe_output} > /dev/null 2>&1"
        )
        shell_commands.append(file_command)
        imported_clips.append(output_path)

    # 3. Create Custom-Sized Window Layout with Icon Styling
    full_pipeline = (
        f"{{ " + " && ".join(shell_commands) + f"; }} | "
        f"zenity --progress --title='DaVinci Resolve Media Importer' --text='Preparing environment...' "
        f"--pulsate --auto-close --no-cancel --width=550 --height=160 --window-icon='video-x-generic'"
    )
    
    subprocess.run(full_pipeline, shell=True)
    
    # 4. Import & Professional Completion Banner
    successful_clips = [path for path in imported_clips if os.path.exists(path)]
    
    if successful_clips:
        media_pool.ImportMedia(successful_clips)
        
        success_text = (
            f"<span foreground='#2ecc71' size='large' weight='bold'>Import Complete!</span>\\n\\n"
            f"Successfully added <b>{len(successful_clips)}</b> media assets into your active Media Pool bin.\\n"
            f"<span foreground='#7f8c8d' size='small'>All temporary formats converted to Linux-native MJPEG/PCM.</span>"
        )
        subprocess.run(["zenity", "--info", f"--text={success_text}", "--title=Success", "--width=400"])

transcode_and_import()

