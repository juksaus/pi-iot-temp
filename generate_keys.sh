#!/usr/bin/env bash

mkdir ~/.ssh
openssl ecparam -genkey -name prime256v1 -noout -out ~/.ssh/ec_private.pem
openssl ec -in ~/.ssh/ec_private.pem -pubout -out ~/.ssh/ec_public.pem
wget -O ~/.ssh/roots.pem https://pki.goog/roots.pem
