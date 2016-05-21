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

FROM alpine

MAINTAINER Alexandre ACEBEDO <alexandre@acebedo.fr>

ARG BUILD_UTILITIES_VERSION

LABEL Description="This image is used to build build-utilities" Vendor="Alexandre ACEBEDO" VERSION=$BUILD_UTILITIES_VERSION

RUN apk update
RUN apk upgrade
RUN apk add go git python3 bash ruby-dev gcc make ruby ruby-bundler \
 g++ libstdc++ libffi-dev ruby-rdoc tar
RUN python3 -m ensurepip && pip3 install --upgrade pip setuptools
RUN apk add ruby-irb ruby-rdoc
RUN gem install fpm
RUN pip3 install -I build-utilities==${BUILD_UTILITIES_VERSION}

VOLUMES ["/build"]
ENTRYPOINT ["build-utilities"]

