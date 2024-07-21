# -*- coding: utf-8 -*-

import json
import sys
from typing import Iterator
from string import ascii_uppercase
import requests
from multiprocessing.pool import ThreadPool as Pool


CMC_FILE = 'coinmarketcap.json'
MYCRYPTO_FILE = 'mycrypto.json'
TICKER_LENGTH = 3


def get_cmc_file():
    with open(CMC_FILE, 'bw') as cmc_f:
        resp = requests.get('https://s2.coinmarketcap.com/generated/search/quick_search.json')
        cmc_f.write(resp.content)


def get_mycrypto_file():
    with open(MYCRYPTO_FILE, 'wb') as mc_f:
        resp = requests.get('https://raw.githubusercontent.com/MyCryptoHQ/MyCrypto/2b60ba96500fe4445e605996e989936be29587df/common/config/tokens/eth.json')
        mc_f.write(resp.content)


def concat(head: str, tail: Iterator[str]) -> Iterator[str]:
    if tail:
        yield from [head + e for e in tail]
    else:
        yield head


def gen_names(pattern: str) -> Iterator[str]:
    if not pattern:
        return []
    for c in pattern:
        if c == '*':
            ret = list()
            for letter in ascii_uppercase:
                for item in concat(letter, gen_names(pattern[1:])):
                    ret.append(item)
            return ret
        else:
            return concat(c, gen_names(pattern[1:]))


def gen_partial_template(partial_template: str) -> Iterator[str]:
    if len(partial_template) == TICKER_LENGTH:
        yield from gen_names(partial_template)
    else:
        for i in range(len(partial_template) + 1):
            template = partial_template[:i] + '*' + partial_template[i:]
            yield from gen_partial_template(template)


def list_tokens_on_etherscan(symbol: str):
    params = {'t': 't', 'term': symbol}
    resp = requests.get('http://etherscan.io/searchHandler', params=params)
    assert resp.status_code == 200
    data = resp.json()
    tokens = list()
    for line in data:
        name_part = line.split('\t')[0]
        if '({})'.format(symbol.lower()) in name_part.lower():
            tokens.append(name_part)
    return tokens


def check(symbol):
    for c in symbol:
        if c not in ascii_uppercase:
            return False
    return True


def encode_decode(text):
    return text.encode(sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding)


def main():
    try:
        with open(CMC_FILE) as in_f:
            cmc = json.load(in_f)
    except IOError:
        get_cmc_file()
        with open(CMC_FILE) as in_f:
            cmc = json.load(in_f)

    try:
        with open(MYCRYPTO_FILE) as in_f:
            mew = json.load(in_f)
    except IOError:
        get_mycrypto_file()
        with open(MYCRYPTO_FILE) as in_f:
            mew = json.load(in_f)

    cmc_symbol_dict = {e['symbol']: e for e in cmc}
    mew_symbol_dict = {e['symbol']: e for e in mew}

    partial_templates = sys.argv[1:]

    acceptable_words = set()

    if partial_templates:
        for template in partial_templates:
            names = [name for name in gen_partial_template(template) if name not in cmc_symbol_dict and name not in mew_symbol_dict]
            acceptable_words |= set(names)
    else:
        with open('words.txt') as in_f:
            for word in in_f:
                word = word.upper().strip()
                if check(word) and len(word) in [3, 4] and word not in cmc_symbol_dict and word not in mew_symbol_dict:
                    acceptable_words.add(word)

    with Pool(4) as p:
        tickers = p.imap(list_tokens_on_etherscan, acceptable_words)

    tickers = {k: v for k, v in zip(acceptable_words, tickers)}

    for ticker, tokens in sorted(tickers.items(), key=lambda x: (len(x[1]), x[0])):
        print(encode_decode('{};{};{}'.format(ticker, len(tokens), tokens or '')))


if __name__ == '__main__':
    main()
