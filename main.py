import subprocess
import time
import json
import argparse
import re

from waggle.plugin import Plugin

# For Server: "iperf3 -s -p 7575"

stream_def = {"sender": "upload", "receiver": "download"}

# https://github.com/R0GGER/public-iperf3-servers
# Chicago (10 GB/S max)
# server = "speedtest.chi11.us.leaseweb.net -p 5201-5210"
# Los Angeles (10 GB/S max)
# server = "la.speedtest.clouvider.net -p 5200-5209"

# default_server = "la.speedtest.clouvider.net"
# default_port = "5200-5209"

default_command = "la.speedtest.clouvider.net -p 5200-5209 -t 5"

def post_error(plugin, error, time_ns, meta):
    print(error)
    plugin.publish("iperf3.error", error, timestamp=time_ns, meta=meta)

def sanitize_input(user_input):
    # Allow only alphanumeric characters, dots, and dashes
    sanitized_input = re.sub(r'[^a-zA-Z0-9.\- "\']', '', user_input)
    return sanitized_input

def main(cmd):        
    with Plugin() as plugin:
        # print("This is the start of an amazing app!")
        command = f"iperf3 -c {cmd} --json"
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        time_ns = int(time.time_ns())
        meta = {"units": "bits per second", "command": cmd}

        try:
            if result.stderr:
                post_error(plugin, result.stderr, time_ns, meta)
            else:
                print(result.stdout)
                output = json.loads(result.stdout)
                
                if "error" in output:
                    post_eror(plugin, output["error"], time_ns, meta)
                    return

                for stream in output["end"]["streams"]:
                    for stream_type in stream.keys():
                        if stream_type in stream_def:
                            print(stream_def[stream_type])
                            print(stream[stream_type]["bits_per_second"])
                            plugin.publish(f'iperf3.{stream_def[stream_type]}.bits.per.sec', float(stream[stream_type]["bits_per_second"]), timestamp=time_ns, meta=meta)

        except:
            post_error(plugin, "non-specific error", time_ns, meta)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='iPerf3 for Sage Node',
                    description='Measures the upload and download speed in bits per second against a known server',
                    epilog='')
    parser.add_argument('--command', dest='cmd', default=default_command,
                    help='Forwards the command to iPerf3. Example: --command "0.0.0.0 -p 7575" becomes "iperf3 -c 0.0.0.0 -p 7575 --json" behind the scenes')
    args = parser.parse_args()
    
    # if args.port != "":
    #     args.port = f"-p {args.port}"
    cmd = sanitize_input(args.cmd)
    print(cmd)
    main(cmd)
