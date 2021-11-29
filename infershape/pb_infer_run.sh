rm -rf main_infershape
rm -rf cpu_infershape_result
TF_VERSION=( $(python3 -c 'import tensorflow as tf; print(" ".join(tf.__version__))') )

TF_CFLAGS=( $(python3 -c 'import tensorflow as tf; print(" ".join(tf.sysconfig.get_compile_flags()))') )
TF_LFLAGS=( $(python3 -c 'import tensorflow as tf; print(" ".join(tf.sysconfig.get_link_flags()))') )
g++ pb_infershape.cpp -std=c++11 -o main_infershape ${TF_CFLAGS[@]} ${TF_LFLAGS[@]} -lpthread -ldl -O2 -DTF_VERSION${TF_VERSION}
TF_LD_LIBRARY_PATH=( $(python3 -c 'import tensorflow as tf; print(tf.sysconfig.get_lib())') )
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$TF_LD_LIBRARY_PATH

./main_infershape $1 $2

if [ $? != 0 ];then
	exit -1
fi
#./main_infershape gat.pb "ftr_in:1,2708,1433;bias_in:1,2708,2708;lbl_in:1,2708,7;msk_in:1,2708"
