# RPGMV Converter

Encrypt and decrypt images and audio from RPG Maker MV/MZ games.

Made specifically for **Look Outside**, but works with any RPG Maker MV/MZ game using standard RPGMV encryption.

## Features

- Decrypt `.png_`, `.rpgmvp` images to PNG
- Decrypt `.ogg_`, `.rpgmvo` audio to OGG
- Encrypt PNG/OGG back to RPGMV format
- Image preview with fullscreen slideshow
- Auto-detect encryption key from System.json
- Preserve folder structure on export
- Dark theme UI

## Download

Go to [Releases](../../releases) and download the executable for your OS:

- `RPGMV_Converter_Windows.exe` - Windows
- `RPGMV_Converter_Linux` - Linux
- `RPGMV_Converter_MacOS` - macOS

## Run from Source

```bash
pip install pillow
python rpgmv_converter.py
```

## Usage

1. Select PNG or OGG tab
2. Click "Carpeta" to select game folder (auto-detects encryption key)
3. Optionally select output folder
4. Click "DESENCRIPTAR" to decrypt or "ENCRIPTAR" to encrypt

## Credits

**Coded by Karl Ravenlight**

- https://www.ravenlight.net
- https://www.instagram.com/vjravenlight

---

*"Breaking barriers between creators and their assets"*
