FROM ubuntu:16.04

# Install Basics
RUN apt-get update -yq && \
	    apt-get install -yq --no-install-recommends git ca-certificates curl fuse uuid-runtime \
	    python-pip pkg-config libpq-dev python-dev build-essential python-tk

# Install Go 1.7.0
RUN curl -sSL https://storage.googleapis.com/golang/go1.7.linux-amd64.tar.gz | tar -C /usr/local -xz  && \
mkdir -p /go/bin

ENV PATH /usr/local/go/bin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin
ENV GOPATH /go
ENV GOROOT /usr/local/go

# Install Pachyderm job-shim
RUN go get github.com/pachyderm/pachyderm && \
go get github.com/pachyderm/pachyderm/src/server/cmd/job-shim && \
cp $GOPATH/bin/job-shim /job-shim
