# gen-crypto-token-names

**Token ticker generator** by Python - Generate token names from templates and check their availabilities on `coinmarketcap`, `mycrypto` and `etherscan`

## Prerequisites

Corpus data from `./words.txt`

## Installing

```bash
$ pip install -r requirements.txt
```

## Run

Run on full english vocabulary to get list of 3- and 4-letter symbols.

```bash
$ python gen_token_names.py
```

You can also check your own templates.

```bash
$ python gen_token_names.py ET* AB *S*
```

Algorithm will check all available symbols in place of `\*`.

It will also extend the string to 3 symbols in all possible ways.

---

&copy; 2020 - 2024 @codeguru827

All rights reserved.
