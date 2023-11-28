# CTFd Rewind

CTFd Rewind is a simple tool that provides interesting visual insights on finished CTFd competitions.

## Features

- Submissions & solves per category
- Top users failed submissions
- First bloods
- Challenges stats
- Most popular category
- Longest submission
- Top failed submissions per challenge

Aditionally, CTFd Rewind also allows you to  **export visualization results in multiple formats (SVG, PNG, PDF)**.
## How to Use

Clone the repo:

    git clone https://github.com/caveeroo/ctfd-rewind.git


To run the tool you will need the backup of the CTFd event.

Export and unzip the backup ([docs.ctfd.io/docs/exports/ctfd-exports](https://docs.ctfd.io/docs/exports/ctfd-exports/)) to the newly created directory (ctfd-rewind).


Run the tool:

```bash
python main.py
```

To get the visual representation of the results, run the visualizer. You can choose between svg, png, pdf and all, which will create a zip file containing all previous output formats.

```bash
python visualizer.py -h

usage: visualize.py [-h] --format {svg,png,pdf,all}

Export graphs in specified format

options:
  -h, --help            show this help message and exit
  --format {svg,png,pdf,all}
                        Output format for the graphs
```

```bash
python visualizer.py --format all
results_all.zip created successfully
```

## CTFd Rewind result examples

![image](https://github.com/caveeroo/ctfd-rewind/assets/62477582/9e867a6d-44d9-4d70-8168-b51dfac3ff39)


![image](https://github.com/caveeroo/ctfd-rewind/assets/62477582/f1678f59-6e83-4059-bb95-03057afa86f6)

s/o [hackon.es](https://hackon.es/) for providing sample export data

## Contributing

Contributions are welcomed! If you're interested in improving CTF Rewind, please feel free to fork the repository, make your changes, and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.
