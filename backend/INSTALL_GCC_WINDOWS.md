# Installing GCC on Windows

This guide will help you install GCC (via MinGW) on Windows so you can compile C programs with this application.

## Option 1: Install MinGW-w64 (Recommended)

### Method A: Direct Download

1. **Download MinGW-w64:**
   - Visit: https://www.mingw-w64.org/downloads/
   - Click on "MingW-W64-builds" or use the installer from: https://github.com/niXman/mingw-builds-binaries/releases
   - Download the latest version (e.g., `x86_64-*-release-posix-seh-ucrt-rt_v*-rev*.7z`)

2. **Extract the archive:**
   - Extract to a location like `C:\mingw64` (avoid spaces in path)

3. **Add to PATH:**
   - Press `Win + X` and select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find and select "Path", then click "Edit"
   - Click "New" and add: `C:\mingw64\bin` (adjust path if you installed elsewhere)
   - Click "OK" on all dialogs

4. **Verify installation:**
   - Open a **new** PowerShell or Command Prompt window
   - Run: `gcc --version`
   - You should see version information

### Method B: Using MSYS2 (Alternative)

1. **Download and install MSYS2:**
   - Visit: https://www.msys2.org/
   - Download and run the installer
   - Follow the installation wizard

2. **Install MinGW-w64:**
   - Open MSYS2 terminal
   - Run: `pacman -S mingw-w64-x86_64-gcc`
   - Add `C:\msys64\mingw64\bin` to your PATH (same steps as Method A)

### Method C: Using Chocolatey (If you have it)

1. Open PowerShell as Administrator
2. Run: `choco install mingw`
3. Restart your terminal

## Option 2: Using Visual Studio Build Tools

1. Download Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/
2. During installation, select "Desktop development with C++"
3. This includes MSVC compiler (not GCC, but can compile C code)

## Verifying Installation

After installation, verify GCC is available:

```powershell
# Open PowerShell or Command Prompt
gcc --version
```

You should see output like:
```
gcc (x86_64-posix-seh-rev0, Built by MinGW-W64 project) 13.2.0
Copyright (C) 2023 Free Software Foundation, Inc.
```

## Troubleshooting

### "gcc is not recognized as an internal or external command"

**Problem:** GCC is not in your PATH or you haven't restarted your terminal.

**Solutions:**
1. Make sure you added the correct path to PATH (should end with `\bin`)
2. **Restart your terminal/IDE** - PATH changes require a restart
3. Verify the path exists: Check if `C:\mingw64\bin\gcc.exe` exists (adjust path as needed)
4. Try running the full path: `C:\mingw64\bin\gcc.exe --version`

### Still Not Working?

1. Check if GCC is actually installed:
   - Navigate to the MinGW bin directory in File Explorer
   - Look for `gcc.exe`

2. Verify PATH:
   ```powershell
   $env:PATH -split ';' | Select-String -Pattern 'mingw'
   ```

3. Restart your computer (sometimes required for PATH changes to take effect)

## Testing the Installation

Create a test C file (`test.c`):
```c
#include <stdio.h>
int main() {
    printf("Hello, World!\n");
    return 0;
}
```

Compile it:
```powershell
gcc test.c -o test.exe
```

Run it:
```powershell
.\test.exe
```

If you see "Hello, World!", GCC is working correctly!

## Need Help?

- MinGW-w64 Documentation: https://www.mingw-w64.org/
- MSYS2 Documentation: https://www.msys2.org/docs/
- Check backend logs for more detailed error messages


