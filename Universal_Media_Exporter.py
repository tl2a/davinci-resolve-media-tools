#!/usr/bin/env python3
import os
import sys
import time
import glob
import subprocess
import shlex

PRESETS = {
    "H.264 (MP4) - Standard / High Quality": {
        "ext": ".mp4",
        "ffmpeg": "-c:v libx264 -preset slow -crf 18 -c:a aac -b:a 320k -movflags +faststart"
    },
    "H.264 (MP4) - Small File Size (Web/Discord)": {
        "ext": ".mp4",
        "ffmpeg": "-c:v libx264 -preset medium -crf 24 -c:a aac -b:a 192k -movflags +faststart"
    },
    "H.265 / HEVC (MP4) - High Efficiency": {
        "ext": ".mp4",
        "ffmpeg": "-c:v libx265 -preset medium -crf 22 -tag:v hvc1 -c:a aac -b:a 320k -movflags +faststart"
    },
    "AV1 (MKV) - Modern Open Codec": {
        "ext": ".mkv",
        "ffmpeg": "-c:v libsvtav1 -preset 6 -crf 26 -c:a libopus -b:a 192k"
    },
    "VP9 / Opus (WebM) - Web Standard": {
        "ext": ".webm",
        "ffmpeg": "-c:v libvpx-vp9 -crf 28 -b:v 0 -c:a libopus -b:a 192k"
    },
    "Audio Only - MP3 (320kbps CBR)": {
        "ext": ".mp3",
        "ffmpeg": "-vn -c:a libmp3lame -b:a 320k"
    },
    "Audio Only - AAC (.m4a)": {
        "ext": ".m4a",
        "ffmpeg": "-vn -c:a aac -b:a 320k"
    }
}

def export_timeline():
    if 'resolve' not in globals():
        print("Error: This script must be executed from inside DaVinci Resolve's Workspace/Fusion menu.")
        return

    project_manager = resolve.GetProjectManager()
    current_project = project_manager.GetCurrentProject()
    
    if not current_project:
        subprocess.run(["zenity", "--error", "--text=Please open a project with an active timeline first!"])
        return

    timeline = current_project.GetCurrentTimeline()
    if not timeline:
        subprocess.run(["zenity", "--error", "--text=No active timeline found to export!"])
        return

    project_name = current_project.GetName()
    timeline_name = timeline.GetName()
    base_export_name = project_name if project_name and project_name != "Untitled Project" else timeline_name

    # 1. Preset Selection Dialog
    preset_list_args = []
    for name in PRESETS.keys():
        preset_list_args.extend(["FALSE", name])
    if preset_list_args:
        preset_list_args[0] = "TRUE"

    zenity_preset_cmd = [
        "zenity", "--list", "--radiolist",
        "--title=Export Format & Codec",
        "--text=Select the target format for encoding:",
        "--column=Select", "--column=Format Preset",
        *preset_list_args,
        "--width=620", "--height=500"
    ]

    try:
        selected_preset_name = subprocess.check_output(zenity_preset_cmd, text=True).strip()
    except subprocess.CalledProcessError:
        return

    if not selected_preset_name or selected_preset_name not in PRESETS:
        return

    preset_config = PRESETS[selected_preset_name]
    target_ext = preset_config["ext"]

    # 2. File Destination Dialog
    default_filename = f"{base_export_name}{target_ext}"
    zenity_save_cmd = [
        "zenity", "--file-selection", "--save", "--confirm-overwrite",
        f"--filename={os.path.expanduser('~')}/{default_filename}",
        f"--title=Save Exported File As ({target_ext})",
        "--width=700", "--height=550"
    ]

    try:
        final_output_path = subprocess.check_output(zenity_save_cmd, text=True).strip()
    except subprocess.CalledProcessError:
        return

    if not final_output_path:
        return

    if not final_output_path.lower().endswith(target_ext.lower()):
        final_output_path += target_ext

    # 3. Resolve Media Storage Path Configuration
    media_storage = resolve.GetMediaStorage()
    mounted_volumes = media_storage.GetMountedVolumeList()
    
    if mounted_volumes:
        base_temp_dir = mounted_volumes[0]
    else:
        base_temp_dir = os.path.expanduser("~")

    intermediate_dir = os.path.join(base_temp_dir, ".resolve_temp_render")
    try:
        os.makedirs(intermediate_dir, exist_ok=True)
    except OSError:
        intermediate_dir = base_temp_dir

    timestamp_id = int(time.time())
    intermediate_prefix = f"resolve_export_temp_{timestamp_id}"
    expected_direct_file = os.path.join(intermediate_dir, f"{intermediate_prefix}.mov")

    current_project.SetCurrentRenderFormatAndCodec("mov", "DNxHR")
    
    render_settings = {
        "TargetDir": intermediate_dir,
        "CustomName": intermediate_prefix,
        "ExportVideo": True,
        "ExportAudio": True,
        "SelectAllFrames": True
    }
    current_project.SetRenderSettings(render_settings)

    current_project.DeleteAllRenderJobs()
    job_id = current_project.AddRenderJob()
    
    if not job_id:
        current_project.SetCurrentRenderFormatAndCodec("mov", "")
        job_id = current_project.AddRenderJob()

    if not job_id:
        subprocess.run(["zenity", "--error", "--text=Failed to create DaVinci Resolve render job.\nPlease verify that your project has video/audio tracks enabled."])
        return

    # 4. Single Persistent Progress Dialog (Remains open for entire pipeline)
    progress_proc = subprocess.Popen(
        [
            "zenity", "--progress",
            "--title=Exporting Media",
            "--text=Preparing export...",
            "--pulsate",
            "--auto-close",
            "--no-cancel",
            "--width=560",
            "--height=130"
        ],
        stdin=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    def update_status(text):
        try:
            if progress_proc.stdin and not progress_proc.stdin.closed:
                progress_proc.stdin.write(f"# {text}\n")
                progress_proc.stdin.flush()
        except (BrokenPipeError, OSError):
            pass

    # Stage 1: Render in DaVinci Resolve
    update_status("Stage 1/2: DaVinci Resolve is rendering intermediate master...")
    current_project.StartRendering([job_id])

    while current_project.IsRenderingInProgress():
        status = current_project.GetRenderJobStatus(job_id)
        if status.get("JobStatus") in ["Failed", "Cancelled"]:
            progress_proc.terminate()
            subprocess.run(["zenity", "--error", "--text=Resolve timeline render failed or was aborted."])
            return
        time.sleep(0.5)

    # Detect intermediate file
    intermediate_file = None
    if os.path.exists(expected_direct_file):
        intermediate_file = expected_direct_file
    else:
        matches = glob.glob(os.path.join(intermediate_dir, f"{intermediate_prefix}*"))
        if matches:
            intermediate_file = sorted(matches, key=os.path.getmtime, reverse=True)[0]

    if not intermediate_file or not os.path.exists(intermediate_file):
        progress_proc.terminate()
        subprocess.run(["zenity", "--error", f"--text=Intermediate render file was not found in:\n{intermediate_dir}"])
        return

    # Stage 2: FFmpeg Encoding (Update text in the same window)
    update_status(f"Stage 2/2: FFmpeg encoding to {selected_preset_name}...")
    ffmpeg_exec_cmd = (
        f"ffmpeg -y -i {shlex.quote(intermediate_file)} {preset_config['ffmpeg']} {shlex.quote(final_output_path)}"
    )
    subprocess.run(ffmpeg_exec_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Close progress window cleanly
    try:
        if progress_proc.stdin and not progress_proc.stdin.closed:
            progress_proc.stdin.write("100\n")
            progress_proc.stdin.flush()
            progress_proc.stdin.close()
    except (BrokenPipeError, OSError):
        pass
    progress_proc.wait()

    # 5. Cleanup & Notification
    for temp_f in glob.glob(os.path.join(intermediate_dir, f"{intermediate_prefix}*")):
        try:
            os.remove(temp_f)
        except OSError:
            pass

    if os.path.exists(final_output_path):
        success_text = (
            f"<span foreground='#2ecc71' size='large' weight='bold'>Export Complete!</span>\n\n"
            f"Successfully saved to:\n"
            f"<b>{final_output_path}</b>"
        )
        subprocess.run(["zenity", "--info", f"--text={success_text}", "--title=Export Succeeded", "--width=460"])
    else:
        subprocess.run(["zenity", "--error", "--text=FFmpeg encoding failed to generate the output file."])

export_timeline()
