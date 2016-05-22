#This file is part of build-utilities.
#
#    build-utilities is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    build-utilities is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with build-utilities.  If not, see <http://www.gnu.org/licenses/>.

FROM gliderlabs/alpine

MAINTAINER Alexandre ACEBEDO <alexandre@acebedo.fr>

ARG BRANCH

LABEL Description="This image is used to build build-utilities" Vendor="Alexandre ACEBEDO" VERSION=$BRANCH

RUN apk update && apk upgrade
RUN apk add git python3 python3-dev bash ruby-dev gcc make ruby ruby-bundler \
 g++ libstdc++ libffi-dev ruby-rdoc ruby-irb tar xz-libs xz-dev zsh go
RUN python3 -m ensurepip && pip3 install --upgrade pip setuptools

RUN gem install fpm
RUN git clone http://github.com/aacebedo/build-utilities -b $BRANCH /src
RUN cd /src && ./setup.py install && rm -rf /src

VOLUME ["/build"]
ENTRYPOINT ["build-utilities"]

