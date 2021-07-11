import re


def unformat(string, pattern):
    pattern = pattern.replace("{}", "(.+)")
    return re.search(pattern, string).groups()[0]


class Config:
    strings = None
