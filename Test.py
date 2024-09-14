import argparse


class C:

    pass


c = C()

parser = argparse.ArgumentParser()

parser.add_argument('--foo')

parser.parse_args(namespace=c)

print(c.foo)
