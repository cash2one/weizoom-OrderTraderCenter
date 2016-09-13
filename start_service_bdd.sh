@echo off
set a=%cd: =:%
set a=%a:\= %
for %%j in (%a%) do (set a=%%j)
set a=%a::= %
title %a%

python manage.py runserver_bdd 0.0.0.0 8001
