@echo

rem call ..\\install\\python_install\\python ../Extractor/extractor.py

echo ----

rem cd install\\python_install

rem call install\\python_install\\python install\\python_install\sitecustomize.py

call install\python_install\python scraper_run.py

rem cd install\\python_install

rem call python ../../scraper_run.py

echo Running




pause