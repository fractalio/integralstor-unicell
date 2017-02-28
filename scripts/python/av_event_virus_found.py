#!/usr/bin/python
import sys
from integralstor_common import alerts

alerts.raise_alert(('Virus Found : '+sys.argv[1]+' (check Quarantine and Virus scan Logs)',))
