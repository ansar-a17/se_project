#!/bin/bash

MTTools=$( dirname $0 )

if [ -z $TRGLANG ]
then
    TRGLANG=en
fi
sed -r 's/\@\@ //g' | perl $MTTools/detruecase.perl | perl $MTTools/detokenizer.perl -l $TRGLANG
