"""Random friendly names for new addons ("Swift Otter Addon")."""

import random

_ADJECTIVES = (
    "Agile", "Amber", "Bold", "Brave", "Bright", "Calm", "Clever", "Cosmic",
    "Crisp", "Daring", "Eager", "Fancy", "Gentle", "Golden", "Happy", "Jolly",
    "Keen", "Lively", "Lucky", "Mellow", "Mighty", "Nimble", "Noble", "Quick",
    "Quiet", "Rapid", "Shiny", "Silent", "Sleek", "Snappy", "Sunny", "Swift",
    "Tidy", "Vivid", "Witty", "Zesty",
)  # fmt: skip

_NOUNS = (
    "Badger", "Comet", "Falcon", "Ferret", "Fox", "Gecko", "Heron", "Koala",
    "Lemur", "Lynx", "Marten", "Meteor", "Newt", "Otter", "Owl", "Panda",
    "Pebble", "Penguin", "Pixel", "Quasar", "Raven", "Robin", "Rocket",
    "Salmon", "Sparrow", "Squid", "Tapir", "Tiger", "Toucan", "Walrus",
    "Wombat", "Yak", "Zebra",
)  # fmt: skip


def random_addon_name() -> str:
    return f"{random.choice(_ADJECTIVES)} {random.choice(_NOUNS)} Addon"
