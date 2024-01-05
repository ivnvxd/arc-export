# Arc Pinned Tabs to HTML Bookmarks Converter

## Overview

This project provides a script for converting pinned tabs in the **Arc Browser** to standard HTML bookmarks file. These bookmarks can then be imported into any web browser.

This addresses the lack of a pinned tabs export feature in Arc Browser.

## Requirements

- Python 3.x
- Arc Browser installed

## Installation

1. Clone the repository: `git clone git@github.com:ivnvxd/arc-export.git`
2. Navigate to the project folder: `cd arc-export`

or download using `curl`:

```sh
curl -o main.py https://raw.githubusercontent.com/ivnvxd/arc-export/main/main.py
```

## Usage

Run the `main.py` script from the command line:

```sh
python main.py
# or
python3 main.py
```

### Troubleshooting

If you encounter any problems, manually copy the `StorableSidebar.json` file from the `~/Library/Application Support/Arc/` directory to the project's directory and run the script again.

## How It Works

1. **Read JSON**: Reads the `StorableSidebar.json` file from the Arc Browser's directory *or* the project's directory.
2. **Convert Data**: Converts the JSON data into a hierarchical bookmarks dictionary.
3. **Generate HTML**: Transforms the bookmarks dictionary into an HTML file.
4. **Write HTML**: Saves the HTML file with a timestamp, allowing it to be imported into any web browser.

## Contributions

Contributions are very welcome. Please submit a pull request or create an issue.

Do not forget to give the project a star if you like it! :star:

## License

This project is licensed under the MIT License.
