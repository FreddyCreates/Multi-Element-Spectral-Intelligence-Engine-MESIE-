#!/usr/bin/env python3
from mesie.cloud.alpha_catalog import write_alpha_catalog

if __name__ == "__main__":
    path = write_alpha_catalog()
    print(path)