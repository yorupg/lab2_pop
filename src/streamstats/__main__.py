import json
import logging
from pathlib import Path

import typer

from streamstats.errors import CLIConfigError, InvalidLineError, UnsupportedFormatError
from streamstats.parsers import parse_csv, parse_jsonl
from streamstats.report import report


def read_events(file_paths, skip_lines, file_formats, skip_invalid):
    
    for index, file_path in enumerate(file_paths):
        
        if len(file_formats) == 1:
            current_format = file_formats[0]
        else:
            current_format = file_formats[index]
        
        if current_format == "csv":
            file_events = parse_csv(file_path, skip_lines, skip_invalid)
        elif current_format == "jsonl":
            file_events = parse_jsonl(file_path, skip_lines, skip_invalid)
        else:
            raise UnsupportedFormatError(f"неподдерживаемый формат файла: {current_format}")
        
        for event in file_events:
            yield event

app = typer.Typer()

@app.callback()
def main():
    pass

@app.command()
def analyze(file_paths: list[Path],
            output: Path = typer.Option(Path("REPORT.json"), "--output", help = "введите путь для сохранения json отчёта"),
            file_formats: list[str] = typer.Option(..., "--format", help = "введите расширение файла [csv|jsonl]"),
            skip_invalid: bool = typer.Option(False, "--skip-invalid", help = "введите, если хотите пропускать неправильные строки")):
    
    skip_lines = {"skip_lines": 0}
    
    if len(file_formats) not in (1, len(file_paths)):
        raise typer.BadParameter("введите один --format для всех файлов или отдельный --format для каждого")
           
    events = read_events(file_paths, skip_lines, file_formats, skip_invalid)
    
    try:
        
        for file_path in file_paths:
            if output.resolve() == file_path.resolve():
                raise CLIConfigError("входной файл совпадает с выходным")
        
        result = report(events, skip_lines)
    
    except (InvalidLineError, UnsupportedFormatError, CLIConfigError) as error:
        logging.error("%s", error)
        raise typer.Exit(code = 2) from error

    
    except FileNotFoundError as error:
        logging.error("не найден файл %s", error.filename)
        raise typer.Exit(code = 2) from error
    
    with output.open("w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=4)
    typer.echo(f"Отчёт сохранён: {output}")
    
    
if __name__ == "__main__":
    app()