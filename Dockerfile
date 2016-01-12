FROM ruby:2.3.0

VOLUME /src
WORKDIR /src

RUN gem install fpm

CMD ["sh","/src/build.sh"]