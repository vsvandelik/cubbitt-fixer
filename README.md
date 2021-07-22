# CUBBITT post-processor

Tool for post-processing of outputs of a czech-english translator. It supports fixing numbers with units, 
separators of decimal numbers and thousands and personal proper name.

## Installation 

```shell
pip install git+https://github.com/vsvandelik/cubbitt-fixer
```

## Usage

```python
from fixer import Fixer, FixerConfigurator

configuration = FixerConfigurator()

configuration.load_from_file("config.yaml") 

fixer = Fixer(configuration)

sentence, has_changed, marks = fixer.fix(
    "Veronika Stýblová vážila o~20 kilo víc.", 
    "Veronica Bean weighed 20 pounds more.")
```

The output of main `fix` method contains:

  - possible changed sentence
  - flag whenever the sentence was changed
  - marks (or labels) about input sentences

Example of the config file:

```yaml
source_lang: cs
target_lang: en
aligner: fast_align # [fast_align|order_based]
lemmatizator: udpipe_online # [udpipe_online|udpipe_offline]
names_tagger: nametag # [nametag]
mode: fixing # [fixing|recalculating]
base_tolerance: 0.1 # [0 - 1]
approximately_tolerance: 0.2 # [0 - 1]
target_units:
    - imperial # [Imperial|SI]
    - USD # [CZK|USD|GBP|EUR]
    - F # [C|F]
exchange_rates: cnb # [cnb|*list of rates - USD, EUR, GBP*]
tools: # sublist of [separators|names|units]
    - separators
    - names
    - units
```


## Licence

MIT License

Copyright (c) 2021 Vojtech Svandelik