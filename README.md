# pass2csv

Command line utility for exporting your pass(1) password store to plain text CSV.


## Usage

```
usage: pass2csv.py [-h] [-p path] [-k [keywords [keywords ...]]] [-g path]
                   output

Export pass database to a CSV file

positional arguments:
  output                path to the output file

optional arguments:
  -h, --help            show this help message and exit
  -p path, --password-store path
                        path to pass directory [default: ~/.password-store]
  -k [keywords [keywords ...]], --keywords [keywords [keywords ...]]
                        list of keywords on begining of each line in a .gpg
                        file [default: ['username', 'url']]
  -g path, --gpg-keyring path
                        path to GnuPG keyring [default: ~/.gnupg]
```

