#!/usr/bin/python
import sys
from integralstor_common import alerts

alerts.raise_alert(('Update Available : '+sys.argv[1]+' (Check configuration for update settings)',))
