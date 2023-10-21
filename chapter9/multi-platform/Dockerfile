FROM multiarch/crossbuild

ARG CROSS_TRIPLE
WORKDIR /workdir/
COPY main.c .

ENV CROSS_TRIPLE=${CROSS_TRIPLE}

RUN crossbuild gcc -o main main.c

CMD ["./main"]
