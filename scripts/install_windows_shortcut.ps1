$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Runner = Join-Path $Root "scripts\run_windows.ps1"
$PowerShell = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"

if (-not (Test-Path $Runner)) {
    throw "Could not find ErgoVision runner: $Runner"
}

function Set-ErgoVisionShortcutAppId {
    param([string]$ShortcutPath, [string]$AppId)

    # WScript.Shell cannot set System.AppUserModel.ID. Use the ShellLink COM
    # property store interfaces to stamp the required AUMID onto the .lnk.
    $source = @"
using System;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;

[ComImport, Guid("00021401-0000-0000-C000-000000000046")]
class ShellLink {}

[ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99")]
interface IPropertyStore {
    void GetCount(out uint count);
    void GetAt(uint index, out PROPERTYKEY key);
    void GetValue(ref PROPERTYKEY key, out PROPVARIANT value);
    void SetValue(ref PROPERTYKEY key, ref PROPVARIANT value);
    void Commit();
}

[StructLayout(LayoutKind.Sequential, Pack = 4)]
struct PROPERTYKEY { public Guid fmtid; public uint pid; }

[StructLayout(LayoutKind.Explicit)]
struct PROPVARIANT {
    [FieldOffset(0)] public ushort vt;
    [FieldOffset(8)] public IntPtr pointerValue;
}

public static class ShortcutAppId {
    static readonly Guid AppUserModelIdFormat = new Guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3");
    const uint AppUserModelIdProperty = 5;

    public static void Set(string shortcutPath, string appId) {
        var link = new ShellLink();
        var persistFile = (IPersistFile)link;
        // STGM_READWRITE is required because the shell-link property store is
        // read-only when the link is loaded in the default read-only mode.
        persistFile.Load(shortcutPath, 2);
        var store = (IPropertyStore)link;
        var key = new PROPERTYKEY { fmtid = AppUserModelIdFormat, pid = AppUserModelIdProperty };
        var variant = new PROPVARIANT { vt = 31, pointerValue = Marshal.StringToCoTaskMemUni(appId) };
        try {
            store.SetValue(ref key, ref variant);
            store.Commit();
            persistFile.Save(shortcutPath, true);
        } finally {
            Marshal.FreeCoTaskMem(variant.pointerValue);
            Marshal.ReleaseComObject(link);
        }
    }
}
"@
    # PowerShell can run this installer repeatedly in the same session. Give
    # each Add-Type compilation a private namespace to avoid type collisions.
    $Namespace = "ErgoVisionShortcut$([guid]::NewGuid().ToString('N'))"
    $source = "namespace $Namespace {`r`n$source`r`n}"
    $CompiledTypes = Add-Type -TypeDefinition $source -ErrorAction Stop -PassThru
    $HelperType = $CompiledTypes | Where-Object { $_.Name -eq "ShortcutAppId" }
    $HelperType.GetMethod("Set").Invoke($null, [object[]]@($ShortcutPath, $AppId))
}

$Shell = New-Object -ComObject WScript.Shell
$AppId = "ErgoVision.Desktop"
$Desktop = [Environment]::GetFolderPath("Desktop")
$StartMenu = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"

foreach ($ShortcutPath in @(
    (Join-Path $Desktop "ErgoVision.lnk"),
    (Join-Path $StartMenu "ErgoVision.lnk")
)) {
    $Shortcut = $Shell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $PowerShell
    $Shortcut.Arguments = "-NoLogo -NoProfile -ExecutionPolicy Bypass -File `"$Runner`""
    $Shortcut.WorkingDirectory = $Root
    $Shortcut.Description = "ErgoVision local posture monitor"
    $Shortcut.Save()

    # Desktop toast notifications require a Start Menu shortcut with an AUMID.
    if ($ShortcutPath.StartsWith($StartMenu, [System.StringComparison]::OrdinalIgnoreCase)) {
        Set-ErgoVisionShortcutAppId -ShortcutPath $ShortcutPath -AppId $AppId
        $Key = "HKCU:\Software\Classes\AppUserModelId\$AppId"
        New-Item -Path $Key -Force | Out-Null
        New-ItemProperty -Path $Key -Name "DisplayName" -Value "ErgoVision" -PropertyType String -Force | Out-Null
    }
    Write-Host "Created: $ShortcutPath"
}

Write-Host "Windows shortcuts installed." -ForegroundColor Green
