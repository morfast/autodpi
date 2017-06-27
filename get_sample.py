#!/usr/bin/python -u

import sys
import os

if len(sys.argv) < 3:
    sys.stderr.write("%s <pcap_filename> <csv_filename>\n" % sys.argv[0])
    sys.exit(0)

pcap_filename = sys.argv[1]

for fname in sys.argv[2:]:
    for i,line in enumerate(open(fname).readlines()[1:]):
        spline = line.strip().split(',')
        five_tuple = spline[3]
        protocol = spline[2]
        s, d = five_tuple.split("-->")
        sip,sport = s.split(":")
        dip,dport = d.split(":")

        #print protocol, sip, sport, dip, dport

        # tshark -r lol.pcap -Y "udp and ip.src_host==1.1.1.1 and ip.dst_host==10.8.74.126 and udp.dstport eq 111 and udp.srcport eq 57780" -w 1.cap
        # tshark -r lol.pcap -Y "tcp and ip.src_host==1.1.1.1 and ip.dst_host==10.8.74.126 and tcp.dstport eq 111 and tcp.srcport eq 57780" -w 1.cap

        if dport == "443": continue

        fname_body = fname.split(".")[0]
        if protocol == "TCP":
            output_filename = fname_body + "_tcp_" + str(i) + ".cap"
            cmd1 = 'tshark -r %s -Y "(tcp and ip.src_host==%s and ip.dst_host==%s and tcp.srcport eq %s and tcp.dstport eq %s) or ' \
                                   '(tcp and ip.src_host==%s and ip.dst_host==%s and tcp.srcport eq %s and tcp.dstport eq %s)" -w %s' \
                       % (pcap_filename, sip, dip, sport, dport, \
                                         dip, sip, dport, sport, output_filename)
            cmd2 ="tshark -r %s  -qz follow,tcp,raw,0 > %s" % (output_filename, "flow_tcp_" + fname_body + "_" + str(i))
            print cmd1
            os.system(cmd1)
            print cmd2
            os.system(cmd2)
        elif protocol == "UDP":
            output_filename = fname_body + "_udp_" + str(i) + ".cap"
            cmd1 = 'tshark -r %s -Y "(udp and ip.src_host==%s and ip.dst_host==%s and udp.srcport eq %s and udp.dstport eq %s) or ' \
                                   '(udp and ip.src_host==%s and ip.dst_host==%s and udp.srcport eq %s and udp.dstport eq %s)" -w %s' \
                       % (pcap_filename, sip, dip, sport, dport, \
                                         dip, sip, dport, sport, output_filename)
            cmd2 = "tshark -r %s  -T fields -e data > %s" % (output_filename, "flow_udp_" + fname_body + "_" + str(i))
            print cmd1
            os.system(cmd1)
            print cmd2
            os.system(cmd2)
        print




