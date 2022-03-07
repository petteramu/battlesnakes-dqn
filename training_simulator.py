import re
import subprocess
from typing import Dict, List

from battlesnake_types import TurnRequest

end_reason_regex = "{([\w\d]{8}-[\w\d]{4}-[\w\d]{4}-[\w\d]{4}-[\w\d]{12}) \[(?:{[-\d ]+ [-\d]} )+{[-\d ]+ [-\d]}] [\d]{2} ([\w-]*) [\d]+"
round_regex = "\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} \[(\d)]"



