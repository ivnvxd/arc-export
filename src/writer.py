import datetime


def write_html(html_content: str) -> None:
    print("Writing HTML...")

    current_date: str = datetime.datetime.now().strftime("%Y_%m_%d")
    output_file: str = "arc_bookmarks_" + current_date + ".html"

    with open(output_file, "w") as f:
        f.write(html_content)

    print(f"> HTML written to {output_file}.")
