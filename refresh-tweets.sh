#!/bin/sh

PYTHON=python
if (cat /proc/version |grep -i cygwin) ; then
    PYTHON=python3
fi

i=0
for twid in 762697549979484161 \
                758761004255711232 \
                762602474293321728 \
                463440424141459456 \
                761310539280769024 \
                762738381143023620 \
                762678098206814208 \
                760888006022574081 \
                761779435653652480 \
                762518022372352004 \
                763841870480879617 \
                761967912085323776 \
                764859108579274752 \
                866553062361415681 \
            ;
do
    i=$(($i+1))
    echo refreshing tweet $twid
    $PYTHON ./tweet2latex.py $twid |tee tweet$i.tex
done
