#!/bin/bash

#Ustawienie proxy
export no_proxy=localhost,127.0.0.1

#DIR1="$PWD/in"

DIR3="$PWD/log"

if [ -f ".env" ]; then
    SHARED_VALUE=$(grep -E '^SHARED=' .env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    if [ -n "$SHARED_VALUE" ]; then
        DIRECTORIES=("$SHARED_VALUE")
        README="$SHARED_VALUE/INFO.txt"
    else
        DIRECTORIES=("$PWD")
    fi
 else
    echo "Brak pliku .env"
    exit 1
fi

# Definicja kopiowania pliku log.html
copy_log() {
    local source_dir="$1"
    local target_dir="$2"
    # Utwórz podkatalog log jeśli nie istnieje
    mkdir -p $target_dir
    if [ -d "$target_dir" ]; then
        if [ -f "$source_dir/log.html" ]; then
            # Skopiuj plik z zachowaniem struktury katalogów
            cp "$source_dir/log.html" "$target_dir/log.html"
        fi
    fi
}

run_task() {
    local dir="$1" task="$2"
    filename=$(basename "$0")
    local lockfile="$DIR3/$(basename "$0" | sed 's#\.sh$##' | tr '[:lower:]' '[:upper:]')-${task}-ROBOT.lock"

    if [ -f "$lockfile" ]; then
        echo "Robot $task już działa ($lockfile)"; exit 1
    fi
    touch "$lockfile"

    SDIR=$dir /usr/local/bin/rcc run -t "$task"

    if [ "$1" != "$PWD" ]; then
        clean_dir="${dir%/}"
        copy_log "./log/$2" "$clean_dir/log/$2"
    fi
    rm -f "$lockfile"
}

# Obsługa tasków w zależności od trybu
run_robot() {
  local dir="$1" task="$2"
  echo "Uruchamiam $task w $dir"

  case "$task" in
    prep)
      run_task "$dir" "$task"
      ;;
    *)
      echo "Nieznana opcja: $task"
      echo "Dostępne: prep"
      ;;
  esac
}

# Definiecja funkcji tworzacej log
run_dolog() {
    year=$(date +%Y)
    month=$(date +%m)

    YEAR=$year MONTH=$month /usr/local/bin/rcc run -t Dolog
}

# Ustawia pusty plik
if [ -n "$SHARED_VALUE" ]; then
    dot="."
    if [ -f "$README" ]; then
        echo -e "${dot}$(tr -d '.' < "$README")" > "$README.tmp" && mv "$README.tmp" "$README"
    else
        echo "$dot" > "$README"
    fi
fi

# Wzorzec pliku: dowolny plik rozszerzeniem .xls lub .xlsx
FILE_PATTERN="*.xls*"

# Sprawdzanie, czy istnieje plik pasujacy do wzorca
for dir in "${DIRECTORIES[@]}"; do

dirin=$dir"/in/"
    if [ -d "$dirin" ]; then
        export LOG_BASE="$dir/"
        if ls "$dirin"/$FILE_PATTERN 1> /dev/null 2>&1; then
            echo "Znaleziono plik Excela w: $dirin"
            if [ -n "$SHARED_VALUE" ]; then # tylko jak jest sieciowy folder
                modified=$(date '+%Y-%m-%d %H:%M:%S')
                #local_dirin=$(echo "$dirin" | tr -d "$SHARED_VALUE")
                local_dir=${dir//$SHARED_VALUE/}
                wypisz="${modified} znaleziono plik Excela w: ${local_dir}/in szczegóły w ${local_dir}/log/"
                echo -e "${wypisz}\n$(cat "$README")" > "$README.tmp" && mv "$README.tmp" "$README"
            fi
            run_robot "$dir" "$1"
        else
            echo "Brak Excela w: $dirin"
        fi
    else
        echo "Brak Katalogu: $dirin"
    fi
done

# Wzorzec pliku: dowolny plik rozszerzeniem .json
FILE_PATTERN="*.json"
# Sprawdzanie, czy istnieje plik pasujacy do wzorca
if ls "$DIR3"/$FILE_PATTERN  1> /dev/null 2>&1; then
    echo "Znaleziono plik  rozszerzeniem .json w katalogu $DIR3."
    # SPRAWDZENIE CZY ISTNIEJE .lock
    if ls "$DIR3"/*.lock 1> /dev/null 2>&1; then
        echo "Wykryto plik .lock w katalogu $DIR3 - pomijam uruchomienie dolog."
    else
        run_dolog
    fi
fi
