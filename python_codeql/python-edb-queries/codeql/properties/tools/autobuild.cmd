@echo off

type NUL && "%CODEQL_DIST%\codeql" database index-files ^
    --include-extension=.properties ^
    --size-limit=5m ^
    --language=properties ^
    "%CODEQL_EXTRACTOR_PROPERTIES_WIP_DATABASE%"
exit /b %ERRORLEVEL%    
