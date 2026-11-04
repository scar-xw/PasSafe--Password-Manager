# PasSafe

A simple, local-first password manager. Your passwords are encrypted on your own computer and never sent anywhere.

PasSafe comes with a desktop app (built with CustomTkinter) and a terminal version, both using the same encryption code.

<img width="853" height="584" alt="project5-photo" src="https://github.com/user-attachments/assets/1a111883-378b-4d7c-8958-e3fb699de86e" />


## Features

- **Local and offline.** Nothing is uploaded; your data stays in files you control.
- **Fernet encryption.** Passwords are encrypted with Fernet from Python's [`cryptography`](https://cryptography.io) library (AES-128 in CBC mode, authenticated with HMAC-SHA256).
- **Separate key file.** The encryption key lives in its own file, so you can store it apart from your passwords (for example, on a USB drive).
- **Desktop app.** Searchable list of saved sites, add, update and delete passwords, show or hide, copy to clipboard, and a random password generator.
- **Clipboard auto-clear.** Copied passwords are removed from the clipboard after 30 seconds.
- **Terminal version.** A simple menu-based interface in `main.py`.
- **Separated design.** All encryption and file logic lives in `password_manager.py`, with no UI code mixed in.

## Getting started

### Requirements

- Python 3.10 or newer

### Install and run

```bash
pip install cryptography customtkinter
python app.py
```

If you use [uv](https://docs.astral.sh/uv/):

```bash
uv sync
uv run app.py
```

To use the terminal version instead:

```bash
python main.py
```

## How to use

1. **Create a key** (or load one you already have) and save the key file somewhere safe.
2. **Create a password file** (or load an existing one). It must be used with the key that created it.
3. **Add passwords.** Enter a site and password, then click **Save**. Saving a site that already exists updates its password.
4. Next time, just **load your key** and **load your password file**, then click a site to see its password.

## Build a Windows .exe

On a Windows machine with Python installed, double-click `build.bat`. When it finishes, your program is at `dist\PasSafe.exe`. It is a single file that does not need Python to run.

Windows SmartScreen may warn about an unsigned app you built yourself. Choose **More info**, then **Run anyway**.

## Project structure

```
app.py               Desktop app (CustomTkinter)
main.py              Terminal version
password_manager.py  Encryption and file handling
build.bat            Builds PasSafe.exe with PyInstaller
pyproject.toml       Project metadata and dependencies
```

## Security notes

PasSafe is a learning project. Please read this before trusting it with important passwords.

- **Whoever has your key file and your password file can read all your passwords.** Keep them in different places and back both up.
- **If you lose the key file, your passwords cannot be recovered.**
- **There is no master password.** Protection comes entirely from keeping the key file private.
- Passwords are held in memory while the app is open.
- **Never commit `.key` or `.pw` files to a public repository.**

## Technical stack

- Python
- cryptography (Fernet)
- CustomTkinter
- PyInstaller (for the `.exe`)
- uv (optional, for environment management)
