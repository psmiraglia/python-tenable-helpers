# Bulk creation of remediation goals

It's time to fix the findings identified by Tenable so, we would like to track the progress of our patching.

Our environment composed of multiple zones (e.g. `Europe` and `America`).
To test the patching, each zone contains two rings of assets (`All` and `TestRing`) identified with tags.
All the findings were grouped by filtering on the plugin name.

For each group of findings we would like to have a `remediation goal` focused on each ring of each zone.

## zones.json

The file `zones.json` defines the zones composing the environment. In the current example

* the environment is composed of two zones (`America` and `Europe`)

* for each zone, two rings were defined (`All` and `TestRing`)

* each ring includes assets with a specific tag

## goals.json

The file `goals.json` defines the groups of findings. For each group we have

* a label (e.g. `Adobe Acrobat Reader`)

* a set of conditions to filter the plugins names (e.g. `*adobe*reader*`)

* a description (optional)

## cmdline-generator.py

The script `cmdline-generator.py` takes a set of input parameters and generates all the command lines to be executed to define the remediation goals.

## Run the example

Run `cmdline-generator.py` as follows

~~~
$ ./cmdline-generator.py goals.json zones.json "[MyGoal]" "2022-09-01" "2022-09-30"
~~~

It will generate under `files` directory a set of files where the `.txt` ones contain the remediation goal description while the `.json` ones the conditions to be used. Furthermore, the script will output the `tio-create-rg` command lines to be executed.

~~~
$ ./cmdline-generator.py goals.json zones.json "[MyGoal]" 2022-09-01 2022-09-30 | tee commands.txt
tio-create-rg -n "[MyGoal] Adobe Acrobat Reader (America, TestRing)" -d @files/reader.txt -c @files/reader-america-tr.json -S 2022-09-01 -D 2022-09-30
tio-create-rg -n "[MyGoal] Adobe Acrobat Reader (America, All)" -d @files/reader.txt -c @files/reader-america-all.json -S 2022-09-01 -D 2022-09-30
tio-create-rg -n "[MyGoal] Adobe Acrobat Reader (Europe, TestRing)" -d @files/reader.txt -c @files/reader-europe-tr.json -S 2022-09-01 -D 2022-09-30
tio-create-rg -n "[MyGoal] Adobe Acrobat Reader (Europe, All)" -d @files/reader.txt -c @files/reader-europe-all.json -S 2022-09-01 -D 2022-09-30
tio-create-rg -n "[MyGoal] Adobe Flash Player (America, TestRing)" -d @files/flash.txt -c @files/flash-america-tr.json -S 2022-09-01 -D 2022-09-30
tio-create-rg -n "[MyGoal] Adobe Flash Player (America, All)" -d @files/flash.txt -c @files/flash-america-all.json -S 2022-09-01 -D 2022-09-30
tio-create-rg -n "[MyGoal] Adobe Flash Player (Europe, TestRing)" -d @files/flash.txt -c @files/flash-europe-tr.json -S 2022-09-01 -D 2022-09-30
tio-create-rg -n "[MyGoal] Adobe Flash Player (Europe, All)" -d @files/flash.txt -c @files/flash-europe-all.json -S 2022-09-01 -D 2022-09-30
tio-create-rg -n "[MyGoal] Google Chrome (America, TestRing)" -d @files/chrome.txt -c @files/chrome-america-tr.json -S 2022-09-01 -D 2022-09-30
tio-create-rg -n "[MyGoal] Google Chrome (America, All)" -d @files/chrome.txt -c @files/chrome-america-all.json -S 2022-09-01 -D 2022-09-30
tio-create-rg -n "[MyGoal] Google Chrome (Europe, TestRing)" -d @files/chrome.txt -c @files/chrome-europe-tr.json -S 2022-09-01 -D 2022-09-30
tio-create-rg -n "[MyGoal] Google Chrome (Europe, All)" -d @files/chrome.txt -c @files/chrome-europe-all.json -S 2022-09-01 -D 2022-09-30

$ tree files
files
├── chrome-america-all.json
├── chrome-america-tr.json
├── chrome-europe-all.json
├── chrome-europe-tr.json
├── chrome.txt
├── flash-america-all.json
├── flash-america-tr.json
├── flash-europe-all.json
├── flash-europe-tr.json
├── flash.txt
├── reader-america-all.json
├── reader-america-tr.json
├── reader-europe-all.json
├── reader-europe-tr.json
└── reader.txt

$ cat commands.txt | bash
~~~
