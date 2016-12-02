#!/bin/sh

export PATH=/sbin:/bin:/usr/sbin:/usr/bin
export PYTHONPATH=${PYTHONPATH}

NAME="${app}"
MAINPATH=$(cd "$(dirname "$0")"; pwd)
if [[ -e $MAINPATH/${NAME}_svr.py ]]; then
	SVRNAME=$MAINPATH/${NAME}_svr.py
else
	SVRNAME=$MAINPATH/${NAME}_svr.pyc
fi
SVRCONF=$MAINPATH/${NAME}_svr.conf
DAEMON="python $SVRNAME -c $SVRCONF -d"

do_start()
{
	while [[ 1 ]]
	do
		procnum=`ps -ef | grep "$SVRNAME" | grep -v "grep" | wc -l`
		if [[ $procnum -eq 0 ]]
		then
			$DAEMON
		else
			echo "started $NAME service"
			break
		fi
	done
}

do_stop()
{
	while [[ 1 ]]
	do
		procnum=`ps -ef | grep "$SVRNAME" | grep -v "grep" | wc -l`
		if [[ $procnum -eq 0 ]]
		then
			break
		else
			ps -ef | grep "$SVRNAME" | grep -v "grep" | awk '{print $2}' | while read pid
			do
				kill -9 $pid
			done
		fi
	done

	echo "stopped $NAME service"
}

case "$1" in
	start)
		do_start
		;;
	stop)
		do_stop
		;;
	restart)
		do_stop
		do_start
		;;
	*)
		echo "Usage: $0 {start|stop|restart}"
		;;
esac

