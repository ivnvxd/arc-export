from src import converter, reader, writer


def main() -> None:
    data: dict = reader.read_json()
    html: str = converter.convert_json_to_html(data)
    writer.write_html(html)

    print("Done!")


if __name__ == "__main__":
    main()
