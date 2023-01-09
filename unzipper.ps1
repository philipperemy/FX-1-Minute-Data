param([string]$path=".\output")

Get-ChildItem -Path $path -Recurse -Filter *.zip |

Foreach-Object {
    $endPath = $_.Directory.Name
    Expand-Archive $_.FullName "$path\$endPath"
}
