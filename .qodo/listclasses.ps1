$h = Get-Content "c:\Users\User\Desktop\website real\index.html" -Raw
$classes = [regex]::Matches($h, 'class="([^"]+)"') | ForEach-Object { $_.Groups[1].Split(' ') }
$classes | Sort-Object -Unique | ForEach-Object { Write-Output $_ }