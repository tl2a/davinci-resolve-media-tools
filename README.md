# DaVinci Resolve Linux Media Importer, Exporter & Transcoder

A lightweight Python automation toolkit for **DaVinci Resolve (Free Version) on Linux** (tested on Fedora). It provides one-click importing and transcoding of common media into your active Media Pool, plus timeline export to popular delivery formats using FFmpeg and native Zenity GTK dialogs.

---

## Why This Exists

The free edition of DaVinci Resolve on Linux has well-known codec limitations due to licensing restrictions (specifically missing native support for AAC audio decoding and proprietary H.264/H.265 in MP4 containers). 

This script solves the problem by:
1. Providing a graphical file picker (`zenity`) to select single or batch media files.
2. Transcoding audio/video in the background via `ffmpeg` into DaVinci Resolve Linux-compatible native formats:
   - **Video**: MJPEG (`-vcodec mjpeg -q:v 2`) + Uncompressed 16-bit Big-Endian PCM Audio (`-acodec pcm_s16be`) in a `.mov` container.
   - **Audio**: Uncompressed 16-bit Big-Endian PCM Audio (`-acodec pcm_s16be`) in a `.mov` container.
3. Automatically injecting the transcoded clips straight into your open DaVinci Resolve project's Media Pool via DaVinci Resolve's Python Scripting API.
4. Exporting your active timeline to H.264, H.265, AV1, VP9, MP3, or AAC using selectable presets.

## See It in Action

<table>
   <tr>
      <td><img src="screenshots/1.png" alt="DaVinci Resolve Workspace Scripts menu"></td>
      <td><img src="screenshots/5.png" alt="DaVinci Resolve importer success dialog showing completed import"></td>
   </tr>
   <tr>
      <td align="center"><em>Launch the importer from Resolve's Workspace menu.</em></td>
      <td align="center"><em>Imported media appears in the Media Pool after processing.</em></td>
   </tr>
</table>

---

## Prerequisites

Ensure the following tools are installed on your Linux system:

### 1. Python 3
DaVinci Resolve requires Python 3 for scripting integration.

### 2. FFmpeg
Used for background audio and video transcoding.

### 3. Zenity
Used for GTK-based file selection dialogs and progress bars.

---

## Installation & Setup (Fedora Linux)

### Step 1: Install Dependencies

On **Fedora**, install `ffmpeg`, `zenity`, and `python3`:

```bash
# Enable RPM Fusion (required for full FFmpeg) if not already enabled:
sudo dnf install -y https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

# Install packages:
sudo dnf install -y ffmpeg zenity python3
```

> **Note for other distributions:**
> - **Ubuntu/Debian:** `sudo apt install ffmpeg zenity python3`
> - **Arch Linux:** `sudo pacman -S ffmpeg zenity python`

---

### Step 2: Install the Scripts into DaVinci Resolve

DaVinci Resolve loads user Utility scripts from the Fusion scripts directory.

Copy both scripts into the **Utility** scripts directory from a local clone:

```bash
# Create the Utility directory if it does not exist:
mkdir -p "$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Utility"

# Copy the importer and exporter:
cp Universal_Media_Importer.py "$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Utility/"
cp Universal_Media_Exporter.py "$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Utility/"

# Make sure both scripts have execute permissions:
chmod +x "$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Utility/Universal_Media_Importer.py"
chmod +x "$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Utility/Universal_Media_Exporter.py"
```

Or download both scripts directly from GitHub with `curl`:

```bash
mkdir -p "$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Utility"
curl -fL "https://raw.githubusercontent.com/tl2a/Davinci-universal-media-importer/refs/heads/main/Universal_Media_Importer.py" \
   -o "$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Utility/Universal_Media_Importer.py"
curl -fL "https://raw.githubusercontent.com/tl2a/Davinci-universal-media-importer/refs/heads/main/Universal_Media_Exporter.py" \
   -o "$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Utility/Universal_Media_Exporter.py"
chmod +x "$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Utility/Universal_Media_Importer.py"
chmod +x "$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Utility/Universal_Media_Exporter.py"
```

Or with `wget`:

```bash
mkdir -p "$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Utility"
wget -O "$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Utility/Universal_Media_Importer.py" \
   "https://raw.githubusercontent.com/tl2a/Davinci-universal-media-importer/refs/heads/main/Universal_Media_Importer.py"
wget -O "$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Utility/Universal_Media_Exporter.py" \
   "https://raw.githubusercontent.com/tl2a/Davinci-universal-media-importer/refs/heads/main/Universal_Media_Exporter.py"
chmod +x "$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Utility/Universal_Media_Importer.py"
chmod +x "$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Utility/Universal_Media_Exporter.py"
```

*Or system-wide for all users:*
```bash
sudo cp Universal_Media_Importer.py /opt/resolve/Fusion/Scripts/Utility/
sudo cp Universal_Media_Exporter.py /opt/resolve/Fusion/Scripts/Utility/
```

---

## How to Use

### Import Media

1. Launch **DaVinci Resolve** and open your project.
2. In the top menu bar, navigate to:
   ```
   Workspace -> Scripts -> Universal_Media_Importer
   ```
3. A GTK file picker will open. Select one or multiple media files (`.mp4`, `.mkv`, `.mp3`, `.mov`, `.webm`, `.flv`, `.m4a`, `.wav`, `.ogg`, `.aac`, `.flac`).
4. A progress window will display the batch encoding status.
5. Once completed, the transcoded files (`*_encoded.mov`) will be automatically imported into your active Media Pool bin ready for editing.

### Visual Walkthrough

<table>
   <tr>
      <td><img src="screenshots/1.png" alt="DaVinci Resolve Workspace Scripts menu"><br><em>Open the importer from Workspace &gt; Scripts.</em></td>
      <td><img src="screenshots/2.png" alt="Media file picker with multiple files selected"><br><em>Select one or more media files.</em></td>
   </tr>
   <tr>
      <td><img src="screenshots/3.png" alt="DaVinci Resolve importer processing the second file"><br><em>The importer processes the selected batch.</em></td>
      <td><img src="screenshots/4.png" alt="DaVinci Resolve importer processing the third file"><br><em>Progress updates as each file is transcoded.</em></td>
   </tr>
   <tr>
      <td><img src="screenshots/5.png" alt="DaVinci Resolve importer success dialog"><br><em>The imported media appears in the Media Pool as the confirmation modal appears.</em></td>
      <td><img src="screenshots/6.png" alt="Generated MOV files in the file manager"><br><em>Converted `.mov` files are available alongside the source media.</em></td>
   </tr>
</table>

### Export a Timeline

1. Launch **DaVinci Resolve**, open your project, and make sure an active timeline is selected.
2. In the top menu bar, navigate to:
   ```
   Workspace -> Scripts -> Universal_Media_Exporter
   ```
3. Select an export preset, such as H.264 MP4, H.265/HEVC, AV1, VP9/WebM, MP3, or AAC.
4. Choose the destination and filename for the exported media.
5. Resolve renders an intermediate master, then FFmpeg encodes it to the selected format.
6. A confirmation dialog appears when the export is complete, and the finished file is saved to the chosen location.

### Exporter Visual Walkthrough

<table>
   <tr>
      <td><img src="screenshots/7.png" alt="DaVinci Resolve Workspace Scripts menu with Universal Media Exporter selected"><br><em>Launch the exporter from Workspace &gt; Scripts.</em></td>
      <td><img src="screenshots/8.png" alt="DaVinci Resolve exporter format and codec selection dialog"><br><em>Choose the desired export format and codec preset.</em></td>
   </tr>
   <tr>
      <td><img src="screenshots/9.png" alt="DaVinci Resolve exporter encoding a timeline with FFmpeg"><br><em>Track the Resolve render and FFmpeg encoding progress.</em></td>
      <td><img src="screenshots/10.png" alt="Final exported media file shown in the file manager"><br><em>Find the completed export in the destination folder.</em></td>
   </tr>
</table>

---

## Output Format Details

| Source Type | Container | Video Codec | Audio Codec |
| :--- | :--- | :--- | :--- |
| **Video Files** (`.mp4`, `.mkv`, `.webm`, etc.) | QuickTime (`.mov`) | Motion JPEG (`mjpeg`, `-q:v 2`) | Uncompressed PCM (`pcm_s16be`) |
| **Audio Files** (`.mp3`, `.m4a`, `.aac`, `.ogg`, etc.) | QuickTime (`.mov`) | *None* (`-vn`) | Uncompressed PCM (`pcm_s16be`) |

### Export Presets

| Preset | Output | Video Codec | Audio Codec |
| :--- | :--- | :--- | :--- |
| H.264 Standard / High Quality | `.mp4` | H.264 (`libx264`) | AAC 320 kbps |
| H.264 Small File Size | `.mp4` | H.264 (`libx264`) | AAC 192 kbps |
| H.265 / HEVC High Efficiency | `.mp4` | H.265 (`libx265`) | AAC 320 kbps |
| AV1 Modern Open Codec | `.mkv` | AV1 (`libsvtav1`) | Opus 192 kbps |
| VP9 / Opus Web Standard | `.webm` | VP9 (`libvpx-vp9`) | Opus 192 kbps |
| Audio Only MP3 | `.mp3` | None | MP3 320 kbps CBR |
| Audio Only AAC | `.m4a` | None | AAC 320 kbps |

---

## Troubleshooting

- **"Please open a project first!"**: Ensure you have an active project loaded in DaVinci Resolve before executing the script.
- **Python Scripting not working inside Resolve**: In DaVinci Resolve, go to `Preferences -> General` and ensure external scripting is set to `Local` or `Network`. Ensure your system's Python 3 path is recognized by Resolve.
- **Zenity window not appearing**: Verify `zenity` is installed by running `zenity --version` in your terminal.
- **FFmpeg errors**: Verify `ffmpeg` is properly installed with support for common decoders by running `ffmpeg -version`.
- **Exporter cannot render**: Ensure the project has an active timeline with video or audio tracks enabled, and that the selected Resolve Media Storage volume is writable.

---

## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

```
Copyright (C) 2026 Arpan

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```