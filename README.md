# Autopsy Remote Case DataSourceProcessor

## Getting Started

Download and add any file as Data Source input artefacts.

## Prerequisites

* [Python](https://www.python.org/downloads/) (2.7+)
* [Autopsy from rubnogueira/autopsy (data-source-processor-jython)](https://github.com/rubnogueira/autopsy/tree/data-source-processor-jython) - Planned to merge in main repository - https://github.com/sleuthkit/autopsy/pull/6027

## How to use

The script can be used directly as Autopsy module.

### Running from Autopsy

1. Download repository contents ([zip](../../archive/master.zip)).
2. Open Autopsy -> Tools -> Python Plugins
3. Unzip previously downloaded zip in `python_modules` folder.
4. Restart Autopsy, create a case and select the module.

## Author

* **Ruben Nogueira** - [GitHub](https://github.com/rubnogueira)

## TODO
- Implement multiple link downloader
- Retain url file downloaded properties (filename, type)
- Separate classes into files

## Environments Tested

* Linux

## License

This project is licensed under the terms of the GNU GPL v3 License.

## Notes

* Made with ❤ in Leiria, Portugal