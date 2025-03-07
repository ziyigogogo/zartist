import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logger
logger = logging.getLogger('zartist')
log_level = os.getenv('LOGGER_LVL', 'INFO').upper()
logger.setLevel(getattr(logging, log_level))

# Add console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, log_level))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

from zartist.errors import StrParseError
from zartist.utils.builtin_utils import fn_timer, str2dict
from zartist.utils.composite_utils import str2obj
from zartist.utils.image_utils import pil2b64, str2pil
from zartist.utils.pandas_utils import str2df

__all__ = ['str2obj', 'str2pil', 'pil2b64', 'str2df', 'str2dict', 'StrParseError', 'fn_timer', 'logger']
