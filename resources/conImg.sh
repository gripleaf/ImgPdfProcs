#!/usr/bin/env bash

convert -density 200 -colorspace Gray $1 -transparent "#ffffff" $2.png
