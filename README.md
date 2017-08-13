# demo-ott-2017
demo task for OTT

## System requirements
- docker

## Python requirements
- python 3
  - invoke
  - redis
  - nosetests
  - bumpversion

## How to run
1) inv build.redis
2) inv build.app
3) inv service.run

## How to stop
1) inv service.stop


## How to get errors
1) inv service.errors

## How to get clean db
1) inv service.clean
