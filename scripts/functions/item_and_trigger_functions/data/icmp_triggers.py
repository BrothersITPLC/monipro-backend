icmp_triggers_params = [
    {
        "expression": "max(/MoniPro ICMP PING/icmpping,#3)=0",
        "description": "MoniPro ICMP PING: Unavailable by MoniPro ICMP PING",
        "priority": "4",
        "comments": "Last three attempts returned timeout.  Please check device connectivity.",
    },
    {
        "expression": "min(/MoniPro ICMP PING/icmppingloss,5m)>20 and min(/MoniPro ICMP PING/icmppingloss,5m)<100",
        "description": "MoniPro ICMP PING: High MoniPro ICMP PING loss",
        "priority": "2",
        "comments": "ICMP ping loss is too high. Please check device connectivity.",
    },
    {
        "expression": "avg(/MoniPro ICMP PING/icmppingsec,5m)>0.15",
        "description": "MoniPro ICMP PING: High MoniPro ICMP PING response time",
        "priority": "2",
        "comments": "Average ICMP response time is too high.",
    },
]
