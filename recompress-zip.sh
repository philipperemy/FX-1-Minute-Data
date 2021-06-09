# Unzip all files
for dir in $1/*/; do
 echo "$dir"
 cd "$dir" || exit
 unzip "*.zip"
 cd ../../
done

# Re-compress + delete old files
for dir in ./$1/*/; do
  cd "$dir" || exit
  for csv in *.csv; do
    echo "$csv"
    filename="${csv%.*}"
    7z a -r -mx=9 -tzip $filename "$filename*.csv" "$filename*.txt"
  done
  cd ../../
done
