rm -rf build
mkdir -p build/intermediates/host
cd build/intermediates/host
cmake ../../../src -DCMAKE_CXX_COMPILER=g++ -DCMAKE_SKIP_RPATH=TRUE
make
cd ../../../out
mv main amexec

