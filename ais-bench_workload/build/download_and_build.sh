CURDIR=$(dirname $(readlink -f $0))

function try_download_stubs_packet(){
    mkdir -p $INFER_BASE_PATH/opensource/gflags/src/
    #cmd="wget $1 --no-check-certificate -O $2"
    cmd="curl -o $2 $1"
    timeout 60 $cmd #>/dev/null 2>&1
    ret=$?
    if [ "$ret" == 0 -a -s "$2" ];then
        echo "download cmd:$cmd targetfile:$2 OK"
    else
        echo "downlaod targetfile by $cmd Failed please check network or manual download to target file"
        return 1
    fi
}

main()
{
    stubs_packet_url="http://www.aipubservice.com/airesource/tools/20210903%20Stubs%E7%A8%8B%E5%BA%8F.rar"
    target_file="$CURDIR/stubs.rar"
    [ -f $target_file ] && rm -rf $target_file
    
    try_download_stubs_packet $stubs_packet_url $target_file || { echo "donwload stubs failed";return 1; }



}

main "$@"
exit $?