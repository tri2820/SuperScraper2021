@echo on

cd ..

curl.exe -L --output poppler.zip --url https://github.com/oschwartz10612/poppler-windows/releases/download/v21.03.0/Release-21.03.0.zip

echo /wait Downloading

tar -xf poppler.zip

echo /wait Extracting

move /y poppler-* poppler

